import json
from datetime import timedelta

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView

from accounts.models import User
from orders.models import Order, SubscriptionOrder, TempOrder
from payments.models import Payment, PaymentAPILog
from products.models import Package


User = get_user_model()


def initiate_cashfree_payment(request, obj):
    """
    Initiates a Cashfree payment link for an order or subscription order.

    Args:
        request (HttpRequest): Django HttpRequest object.
        obj (Order or SubscriptionOrder): The order/subscription instance.

    Returns:
        HttpResponseRedirect: Redirects to the Cashfree payment link or error page.
    """
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
            return redirect(response_data["link_url"])

    return redirect('payment_failed')


def initiate_subscription_payment(request):
    """
    Handles initiation of gym membership subscription payment flow.

    Args:
        request (HttpRequest): Django HttpRequest object.

    Returns:
        HttpResponseRedirect: Redirects to the payment page or registration page if session is invalid.
    """
    member_id = request.session.get('pending_member_member_id')
    package_id = request.session.get('pending_package_id')

    if not member_id or not package_id:
        messages.error(
            request,
            "Session expired or missing package. Please register again."
        )
        return redirect('register_member')

    user = get_object_or_404(User, member_id=member_id)
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

    return initiate_cashfree_payment(request, subscription_order)


@csrf_exempt
def cashfree_webhook(request):
    """
    Handles Cashfree webhook events for payment and refund status updates.

    Args:
        request (HttpRequest): Django HttpRequest object.

    Returns:
        JsonResponse or HttpResponse: Response based on webhook event handling.
    """
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
        link_id = None

        if event_type == "PAYMENT_SUCCESS_WEBHOOK":
            order_data = data.get('data', {}).get('order', {})
            payment_data = data.get('data', {}).get('payment', {})
            link_id = order_data.get('order_tags', {}).get('link_id')
            payment_status = payment_data.get('payment_status')
        elif event_type == "PAYMENT_LINK_EVENT":
            order_data = data.get('data', {}).get('order', {})
            link_id = data.get('data', {}).get('link_id')
            payment_status = data.get('data', {}).get('link_status')
        elif event_type == "PAYMENT_CHARGES_WEBHOOK":
            order_data = data.get('data', {}).get('order', {})
            link_id = order_data.get('order_tags', {}).get('link_id')
            payment_status = None
        else:
            link_id = None
            payment_status = None

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

        if (
            (event_type == "PAYMENT_SUCCESS_WEBHOOK" and payment_status == "SUCCESS") or
            (event_type == "PAYMENT_LINK_EVENT" and payment_status == "PAID")
        ):
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
        elif event_type == "PAYMENT_LINK_EVENT" and payment_status in ['EXPIRED', 'FAILED']:
            payment.status = Payment.Status.FAILED
            if hasattr(order, 'payment_status'):
                order.payment_status = 'failed'
            order.save()
            payment.save()

        log_entry.response_status = 200
        log_entry.response_body = json.dumps({
            'status': 'success',
            'event_type': event_type
        })
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
    """
    Handles user return from Cashfree payment gateway after payment.

    Args:
        request (HttpRequest): Django HttpRequest object.

    Returns:
        HttpResponse or HttpResponseRedirect: Renders success or failure template, or redirects.
    """
    order_id = request.GET.get('order_id')
    payment = None
    order = None

    if not order_id:
        return render(
            request,
            'advadmin/payment_failed.html',
            {'message': 'Missing order ID'}
        )

    payment = Payment.objects.filter(transaction_id=order_id).first()
    order = SubscriptionOrder.objects.filter(order_number=order_id).select_related('customer').first()

    if order and payment:
        user = order.customer
        if not user.on_subscription:
            user.on_subscription = True
            user.save(update_fields=['on_subscription'])
        if payment.customer != user:
            payment.customer = user
            payment.save(update_fields=['customer'])

    if not payment:
        return render(
            request,
            'advadmin/payment_failed.html',
            {'message': 'Payment not found'}
        )

    if payment.status == Payment.Status.COMPLETED:
        order = payment.content_object
        if not order:
            return render(
                request,
                'advadmin/payment_failed.html',
                {'message': 'Order not found'}
            )

        request.session[f'order_{order_id}_completed'] = True

        if hasattr(order, 'customer'):
            if isinstance(order, Order):
                TempOrder.objects.filter(user=order.customer, processed=False).update(
                    processed=True
                )
                return redirect('payment_order_success', pk=order.id)
            elif isinstance(order, SubscriptionOrder):
                return redirect('payment_subscription_success', pk=order.id)
            else:
                return render(
                    request,
                    'advadmin/payment_failed.html',
                    {'message': 'Unknown order type'}
                )
        else:
            return render(
                request,
                'advadmin/payment_failed.html',
                {'message': 'Invalid order data'}
            )
    else:
        return render(
            request,
            'advadmin/payment_failed.html',
            {'message': 'Payment was not successful'}
        )


def payment_failed(request):
    """
    Render payment failed page.

    Args:
        request (HttpRequest): Django HttpRequest object.

    Returns:
        HttpResponse: Rendered payment failed template.
    """
    return render(
        request,
        'advadmin/payment_failed.html',
        {'message': 'Payment Failed'}
    )


class PaymentListView(ListView):
    """
    Displays a paginated list of payments with filtering by user and date, and sortable columns.

    GET parameters:
        user_id: (int) Filter payments by user/customer.
        date_from: (YYYY-MM-DD) Filter payments with created_at >= date_from.
        date_to: (YYYY-MM-DD) Filter payments with created_at <= date_to.
        sort: (str) Field to sort by (id, customer__username, amount, etc.).
        order: (str) 'asc' or 'desc' for sort order.

    Context:
        payments: filtered/sorted/paginated queryset.
        users: all users for dropdown.
        current_sort: current sort field.
        current_order: current order (asc/desc).
    """
    model = Payment
    template_name = 'advadmin/payments/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 25

    def get_queryset(self):
        """
        Filter payments by user and date, and apply sorting from GET parameters.
        """
        queryset = Payment.objects.select_related('customer')
        user_id = self.request.GET.get('user_id')
        if user_id:
            queryset = queryset.filter(customer_id=user_id)
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from and date_to:
            queryset = queryset.filter(created_at__date__range=[date_from, date_to])
        elif date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        elif date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        sort_by = self.request.GET.get('sort', 'created_at')
        order = '' if self.request.GET.get('order', 'desc') == 'asc' else '-'
        # Allow simple whitelisting of sortable fields
        allowed = {
            'id', 'customer__username', 'amount', 'payment_method',
            'status', 'transaction_id', 'created_at', 'updated_at'
        }
        sort_field = sort_by if sort_by in allowed else 'created_at'
        return queryset.order_by(f'{order}{sort_field}')

    def get_context_data(self, **kwargs):
        """
        Add users list and sort context to template.
        """
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()
        context['current_sort'] = self.request.GET.get('sort', 'created_at')
        context['current_order'] = 'asc' if self.request.GET.get('order', 'desc') == 'asc' else 'desc'
        return context
