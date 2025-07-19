import json
import requests
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

from accounts.models import CustomUser
from orders.models import Order, Payment, SubscriptionOrder, TempOrder
from payments.models import PaymentAPILog
from products.models import Package

CustomUser = get_user_model()

def initiate_cashfree_payment(request, obj):
    """Sends a payment link request to Cashfree for any order/subscription_order."""
    payment, created = Payment.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(obj),
        object_id=obj.id,
        defaults={
            'payment_method': 'cashfree',
            'amount': obj.total,
            'status': Payment.Status.PENDING,
        }
    )
    if not created:
        payment.payment_method = 'cashfree'
        payment.amount = obj.total
        payment.status = Payment.Status.PENDING
        payment.save()

    return_url = request.build_absolute_uri(reverse('cashfree_return')) + f"?order_id={obj.order_number}"
    webhook_url = request.build_absolute_uri(reverse('cashfree_webhook'))

    print("return_urlreturn_urlreturn_urlreturn_url", return_url)
    print("webhook_urlwebhook_urlwebhook_urlwebhook_urlwebhook_url", webhook_url)

    customer = obj.customer
    customer_email = customer.email
    customer_name = customer.get_full_name() or customer.username
    customer_phone = getattr(customer, 'phone_number', '')

    payload = {
        "customer_details": {
            "customer_email": customer_email,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
        },
        "link_amount": float(obj.total),
        "link_currency": "INR",
        "link_id": obj.order_number,
        "link_meta": {
            "notify_url": webhook_url,
            "return_url": return_url,
            "upi_intent": False,
        },
        "link_notify": {
            "send_email": True,
            "send_sms": True,
        },
        "link_purpose": f"Payment for {obj.__class__.__name__} #{obj.order_number}"
    }

    print("payloadpayloadpayloadpayloadpayload", payload)

    headers = {
        "x-api-version": "2022-09-01",
        "x-client-id": settings.CASHFREE_APP_ID,
        "x-client-secret": settings.CASHFREE_SECRET_KEY,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            "https://sandbox.cashfree.com/pg/links",
            json=payload,
            headers=headers
        )
        res_data = response.json()
        print("res_datares_datares_datares_datares_datares_datares_data", res_data)
        PaymentAPILog.objects.create(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            action='CREATE_LINK',
            request_url="https://sandbox.cashfree.com/pg/links",
            request_payload=json.dumps(payload),
            response_status=response.status_code,
            response_body=json.dumps(res_data),
            link_id=res_data.get("link_id")
        )
    except Exception as e:
        PaymentAPILog.objects.create(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            action='ERROR',
            request_url="https://sandbox.cashfree.com/pg/links",
            request_payload=json.dumps(payload),
            error_message=str(e)
        )
        return redirect('payment_failed')

    if response.status_code == 200 and res_data.get("link_url"):
        payment.transaction_id = res_data.get("link_id")
        payment.gateway_response = res_data
        payment.save()
        return redirect(res_data["link_url"])

    if res_data.get("message") == "Link ID already exists":
        payment_log = PaymentAPILog.objects.filter(
            Q(response_body__contains=f'"link_id": "{obj.order_number}"'),
            response_status=200
        ).first()
        if payment_log:
            response_data = json.loads(payment_log.response_body)
            link_id = response_data.get("link_id")
            return redirect(response_data["link_url"])

    return redirect('payment_failed')

def initiate_subscription_payment(request):
    """Handle gym membership subscription payment initiation."""
    member_id = request.session.get('pending_member_member_id')
    package_id = request.session.get('pending_package_id')

    if not member_id or not package_id:
        messages.error(request, "Session expired or missing package. Please register again.")
        return redirect('register_member')

    user = get_object_or_404(CustomUser, member_id=member_id)
    package = get_object_or_404(Package, id=package_id)

    subscription_order = SubscriptionOrder.objects.create(
        customer=user,
        package=package,
        total=package.final_price,
        status=SubscriptionOrder.Status.PENDING,
        payment_status=SubscriptionOrder.PaymentStatus.PENDING,
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + timedelta(days=package.duration_days),
    )

    del request.session['pending_member_member_id']
    del request.session['pending_package_id']
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    return initiate_cashfree_payment(request, subscription_order)

@csrf_exempt
def cashfree_webhook(request):
    """Webhook handler for Cashfree events (payments, refunds, etc.)."""
    log_entry = PaymentAPILog.objects.create(
        action='WEBHOOK',
        request_url=request.path,
        response_body=request.body.decode('utf-8') if request.body else None,
        response_status=0
    )

    if request.method != 'POST':
        log_entry.error_message = "Invalid method"
        log_entry.response_status = 405
        log_entry.save()
        return JsonResponse({'error': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body)
        event_type = data.get("type")
        order_id = None
        link_id = None
        payment_status = None

        if event_type == "PAYMENT_SUCCESS_WEBHOOK":
            order_data = data.get('data', {}).get('order', {})
            payment_data = data.get('data', {}).get('payment', {})
            order_id = order_data.get('order_id')
            link_id = order_data.get('order_tags', {}).get('link_id')
            payment_status = payment_data.get('payment_status')

        elif event_type == "PAYMENT_LINK_EVENT":
            order_data = data.get('data', {}).get('order', {})
            order_id = order_data.get('order_id')
            link_id = data.get('data', {}).get('link_id')
            payment_status = data.get('data', {}).get('link_status')

        elif event_type == "PAYMENT_CHARGES_WEBHOOK":
            order_data = data.get('data', {}).get('order', {})
            order_id = order_data.get('order_id')
            link_id = order_data.get('order_tags', {}).get('link_id')

        if not link_id:
            error_msg = 'Missing link_id'
            log_entry.error_message = error_msg
            log_entry.response_status = 400
            log_entry.save()
            return JsonResponse({'error': error_msg}, status=400)

        payment = Payment.objects.filter(transaction_id=link_id).first()
        if not payment:
            error_msg = f'Payment not found for link_id: {link_id}'
            log_entry.error_message = error_msg
            log_entry.response_status = 404
            log_entry.save()
            return JsonResponse({'error': error_msg}, status=404)

        order = payment.content_object
        payment.gateway_response = data

        if event_type == "PAYMENT_SUCCESS_WEBHOOK" and payment_status == "SUCCESS":
            payment.status = Payment.Status.COMPLETED
            if hasattr(order, 'payment_status'):
                order.payment_status = 'completed'
            if isinstance(order, Order):
                order.status = Order.Status.PROCESSING
            elif isinstance(order, SubscriptionOrder):
                order.status = SubscriptionOrder.Status.ACTIVE
                order.payment_status = SubscriptionOrder.PaymentStatus.COMPLETED
            order.save()
            payment.save()
        elif event_type == "PAYMENT_LINK_EVENT":
            if payment_status == "PAID":
                payment.status = Payment.Status.COMPLETED
                if hasattr(order, 'payment_status'):
                    order.payment_status = 'completed'
                if isinstance(order, Order):
                    order.status = Order.Status.PROCESSING
                elif isinstance(order, SubscriptionOrder):
                    order.status = SubscriptionOrder.Status.ACTIVE
                    order.payment_status = SubscriptionOrder.PaymentStatus.COMPLETED
                order.save()
                payment.save()
            elif payment_status in ['EXPIRED', 'FAILED']:
                payment.status = Payment.Status.FAILED
                if hasattr(order, 'payment_status'):
                    order.payment_status = 'failed'
                order.save()
                payment.save()
        elif event_type == "PAYMENT_CHARGES_WEBHOOK":
            pass  # Handle as needed

        log_entry.response_status = 200
        log_entry.response_body = json.dumps({'status': 'success', 'event_type': event_type})
        log_entry.link_id = link_id
        log_entry.save()

        return HttpResponse(status=200)

    except Exception as e:
        error_msg = str(e)
        log_entry.error_message = error_msg
        log_entry.response_status = 500
        log_entry.save()
        return HttpResponse(status=200)

def cashfree_return(request):
    print("\n\n=== cashfree_return START ===")
    print(f"Request.GET: {request.GET}")
    print(f"Request path: {request.path}")
    print(f"Request method: {request.method}")

    order_id = request.GET.get('order_id')
    print(f"order_id from GET: {order_id}")

    if not order_id:
        print("ERROR: order_id is missing!")
        return render(request, 'advadmin/payment_failed.html', {'message': 'Missing order ID'})

    print(f"Searching for Payment with transaction_id={order_id}")
    payment = Payment.objects.filter(transaction_id=order_id).first()
    print(f"Found payment: {payment}")

    if not payment:
        print("ERROR: Payment not found!")
        return render(request, 'advadmin/payment_failed.html', {'message': 'Payment not found'})

    print(f"Payment status: {payment.status}")
    print(f"Payment content_type: {payment.content_type}")
    print(f"Payment object_id: {payment.object_id}")
    print(f"Payment content_object: {payment.content_object}")
    print(f"Payment gateway_response (type): {type(payment.gateway_response)}")
    print(f"Payment gateway_response (data): {payment.gateway_response}")

    if payment.status == Payment.Status.COMPLETED:
        print("\n--- Payment is COMPLETED ---")
        order = payment.content_object
        print(f"content_object type: {type(order)}")
        print(f"content_object: {order}")

        if not order:
            print("ERROR: content_object is None!")
            return render(request, 'advadmin/payment_failed.html', {'message': 'Order not found'})

        print(f"Setting session: order_{order_id}_completed = True")
        request.session[f'order_{order_id}_completed'] = True

        if hasattr(order, 'customer'):
            print(f"order has customer: {order.customer}")
            print(f"order.__class__.__name__: {order.__class__.__name__}")

            if isinstance(order, Order):
                print("--- This is an Order (e-commerce/product) ---")
                print(f"Updating TempOrder for user {order.customer}")
                TempOrder.objects.filter(user=order.customer, processed=False).update(processed=True)
                print(f"Redirecting to payment_order_success, pk={order.id}")
                return redirect('payment_order_success', pk=order.id)
            elif isinstance(order, SubscriptionOrder):
                print("--- This is a SubscriptionOrder (gym membership) ---")
                print(f"Redirecting to payment_subscription_success, pk={order.id}")
                return redirect('payment_subscription_success', pk=order.id)
            else:
                print(f"WARNING: Unknown order type: {order.__class__.__name__}")
                return render(request, 'advadmin/payment_failed.html', {'message': 'Unknown order type'})
        else:
            print("WARNING: Order has no customer attribute!")
            return render(request, 'advadmin/payment_failed.html', {'message': 'Invalid order data'})
    else:
        print("\n--- Payment is NOT completed ---")
        print(f"Payment status: {payment.status}")
        return render(request, 'advadmin/payment_failed.html', {'message': 'Payment was not successful'})

def payment_failed(request):
    print("\n--- payment_failed ---")
    print(f"Rendering payment_failed template")
    return render(request, 'advadmin/payment_failed.html', {'message': 'Payment Failed'})

