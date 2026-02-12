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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView


from accounts.models import User
from orders.models import Order, SubscriptionOrder, TempOrder
from payments.models import Payment, PaymentAPILog, Transaction
from products.models import Package

User = get_user_model()


def initiate_cashfree_payment(request, obj):
    """
    Initiates a Cashfree payment link for an order or subscription order.
    Creates a pending Transaction entry for tracking.

    Args:
        request (HttpRequest): Django HttpRequest object.
        obj (Order or SubscriptionOrder): The order/subscription instance.

    Returns:
        HttpResponseRedirect: Redirects to the Cashfree payment link or error page.
    """
    from payments.models import Transaction  # Import the Transaction model
    from django.utils import timezone
    
    amount = round(float(obj.total), 2)
    
    # Create or update Payment record
    payment, created = Payment.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(obj),
        object_id=obj.id,
        Vendor=request.user.vendor,
        defaults={
            'payment_method': 'cashfree',
            'amount': amount,
            'status': Payment.Status.PENDING,
        }
    )

    if not created:
        payment.payment_method = 'cashfree'
        payment.amount = amount
        payment.status = Payment.Status.PENDING
        payment.customer = obj.customer
        payment.save()

    # Extract customer information
    customer = obj.customer
    customer_email = customer.email
    customer_name = customer.get_full_name() or customer.username
    customer_phone = getattr(customer, 'phone_number', '') or getattr(customer, 'phone', '')

    # Create Transaction entry with PENDING status
    try:
        # Check if transaction already exists
        transaction, trans_created = Transaction.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            Vendor=request.user.vendor,
            defaults={
                'transaction_type': Transaction.Type.INCOME,  # Assuming payment is income
                'category': Transaction.Category.SALES if isinstance(obj, SubscriptionOrder) else Transaction.Category.OTHER,
                'status': Transaction.Status.PENDING,  # Set to PENDING initially
                'amount': amount,
                'description': f"Payment initiated for {obj.__class__.__name__} #{obj.order_number}",
                'reference': obj.order_number,
                'date': timezone.now().date(),
                # Customer information
                'customer_name': customer_name,
                'customer_email': customer_email,
                'customer_phone': str(customer_phone) if customer_phone else '',
            }
        )
        
        if not trans_created:
            # Update existing transaction
            transaction.status = Transaction.Status.PENDING
            transaction.amount = amount
            transaction.customer_name = customer_name
            transaction.customer_email = customer_email
            transaction.customer_phone = str(customer_phone) if customer_phone else ''
            transaction.description = f"Payment re-initiated for {obj.__class__.__name__} #{obj.order_number}"
            transaction.save()
            
        print(f"Transaction entry created/updated: {transaction.id} with status PENDING")
        
    except Exception as e:
        print(f"Error creating transaction entry: {str(e)}")
        # Continue with payment process even if transaction creation fails

    # Prepare Cashfree payment payload
    return_url = request.build_absolute_uri(reverse('cashfree_return')) + f"?order_id={obj.order_number}"
    webhook_url = request.build_absolute_uri(reverse('cashfree_webhook'))

    payload = {
        "customer_details": {
            "customer_email": customer_email,
            "customer_name": customer_name,
            "customer_phone": str(customer_phone) if customer_phone else '',
        },
        "link_amount": float(amount),
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
        "link_purpose": f"Payment for {obj.__class__.__name__} #{obj.order_number}",
        "link_tags": {
            "transaction_id": transaction.id if 'transaction' in locals() else None,
            "vendor_id": request.user.vendor.id,
            "customer_id": customer.member_id,
        }
    }

    headers = {
        "x-api-version": "2022-09-01",
        "x-client-id": settings.CASHFREE_APP_ID,
        "x-client-secret": settings.CASHFREE_SECRET_KEY,
        "Content-Type": "application/json",
    }

    print("Cashfree Payload :::::::::::::::::::", payload)

    try:
        response = requests.post(
            "https://sandbox.cashfree.com/pg/links",
            json=payload,
            headers=headers
        )
        res_data = response.json()

        print("Cashfree Response :::::::::::::::::::", res_data)

        PaymentAPILog.objects.create(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            action='CREATE_LINK',
            request_url="https://sandbox.cashfree.com/pg/links",
            request_payload=json.dumps(payload),
            response_status=response.status_code,
            response_body=json.dumps(res_data),
            link_id=res_data.get("link_id"),
            Vendor=request.user.vendor,
        )
        
    except Exception as e:
        # Update transaction status to failed if API call fails
        if 'transaction' in locals():
            transaction.status = Transaction.Status.INITIATED  # Keep as initiated since payment link creation failed
            transaction.description += f" - API Error: {str(e)}"
            transaction.save()
            
        PaymentAPILog.objects.create(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            action='ERROR',
            request_url="https://sandbox.cashfree.com/pg/links",
            request_payload=json.dumps(payload),
            error_message=str(e),
            Vendor=request.user.vendor,
        )
        return redirect('payment_failed')

    if response.status_code == 200 and res_data.get("link_url"):
        payment.transaction_id = res_data.get("link_id")
        payment.gateway_response = res_data
        payment.save()
        
        # Update transaction with link_id reference
        if 'transaction' in locals():
            transaction.reference = res_data.get("link_id", obj.order_number)
            transaction.description = f"Payment link created for {obj.__class__.__name__} #{obj.order_number}"
            transaction.save()
        
        return redirect(res_data["link_url"])

    if res_data.get("message") == "Link ID already exists":
        payment_log = PaymentAPILog.objects.filter(
            Q(response_body__contains=f'"link_id": "{obj.order_number}"'),
            response_status=200
        ).first()
        if payment_log:
            response_data = json.loads(payment_log.response_body)
            
            # Update transaction status since link already exists
            if 'transaction' in locals():
                transaction.description += " - Link already exists, redirecting to existing link"
                transaction.save()
                
            return redirect(response_data["link_url"])

    # If we reach here, something went wrong
    if 'transaction' in locals():
        transaction.status = Transaction.Status.INITIATED
        transaction.description += f" - Payment link creation failed: {res_data.get('message', 'Unknown error')}"
        transaction.save()

    return redirect('payment_failed')



def get_active_subscription_order(user):
    """
    Returns active subscription order for a user, if exists.
    """
    today = timezone.now().date()
    return SubscriptionOrder.objects.filter(
        customer=user,
        status=SubscriptionOrder.Status.ACTIVE,
        end_date__gte=today
    ).order_by('-end_date').first()


def calculate_new_expiry(user, package):
    """
    Returns the new expiry date for a subscription renewal.

    If user currently has an active package and 'package_expiry_date' in the future,
    new expiry = current package_expiry_date + package.duration_days.
    Otherwise, new expiry = today + package.duration_days
    """
    today = timezone.now().date()
    cur_expiry = getattr(user, "package_expiry_date", None)
    if cur_expiry and cur_expiry >= today:
        return cur_expiry + timedelta(days=package.duration_days)
    return today + timedelta(days=package.duration_days)


def initiate_subscription_payment(request):
    """
    Handles initiation of Vendor membership subscription payment flow.

    Args:
        request (HttpRequest): Django HttpRequest object.

    Returns:
        HttpResponseRedirect: Redirects to the payment page or registration page if session is invalid.
    """
    member_id = request.session.get('pending_member_member_id')
    package_id = request.session.get('pending_package_id')
    

    print("member_id", member_id)
    print("package_id", package_id)

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
        Vendor=request.user.vendor  
    )

    del request.session['pending_member_member_id']
    del request.session['pending_package_id']

    return initiate_cashfree_payment(request, subscription_order)



def buy_subscription_package(request):
    """
    Handles buying or renewal of a subscription package for a user.

    - If user has ACTIVE subscription or a package_expiry_date >= today:
        - new expiry = cur_expiry + package.duration_days
    - Else:
        - new expiry = today + package.duration_days

    Args:
        request (HttpRequest): Django HttpRequest object.

    Returns:
        HttpResponseRedirect: Redirects to payment initiation.
    """
    member_id = request.GET.get('member_id')
    package_id = request.GET.get('package_id')
    if not member_id or not package_id:
        messages.error(
            request,
            "Session expired or missing package. Please register again."
        )
        return redirect('register_member')

    user = get_object_or_404(User, member_id=member_id)
    package = get_object_or_404(Package, id=package_id)

    # Calculate the correct new expiry date
    new_expiry = calculate_new_expiry(user, package)
    today = timezone.now().date()

    subscription_order = SubscriptionOrder.objects.create(
        customer=user,
        package=package,
        total=package.final_price,
        status=SubscriptionOrder.Status.PENDING,
        payment_status=SubscriptionOrder.PaymentStatus.PENDING,
        start_date=today,
        end_date=new_expiry,
        Vendor=request.user.vendor
    )

    # Set these right-away for pending payment - will confirm on webhook success
    user.package = package
    # user.on_subscription = True
    # user.package_expiry_date = new_expiry
    user.save(update_fields=['package'])
    # user.save(update_fields=['package', 'on_subscription', 'package_expiry_date'])

    return initiate_cashfree_payment(request, subscription_order)



from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

@csrf_exempt
def cashfree_webhook(request):
    """
    Handles Cashfree webhook events for payment and refund status updates.
    Updates both Payment and Transaction records.
    """
    from payments.models import Transaction
    
    try:
        data = json.loads(request.body)
        event_type = data.get("type")
        link_id = None
        payment_status = None

        # Extract link_id and payment_status based on event type
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
        else:
            link_id = None

        payment = Payment.objects.filter(transaction_id=link_id).first()
        log_entry = PaymentAPILog.objects.create(
            Vendor=payment.Vendor if payment else None,
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

        # Get related transaction
        transaction = Transaction.objects.filter(
            content_type=payment.content_type,
            object_id=payment.object_id,
            Vendor=payment.Vendor
        ).first()

        print("transactioncustomer_name", transaction.customer_name)

        if (
            (event_type == "PAYMENT_SUCCESS_WEBHOOK" and payment_status == "SUCCESS") or
            (event_type == "PAYMENT_LINK_EVENT" and payment_status == "PAID")
        ):
            payment.status = Payment.Status.COMPLETED

            # Update Transaction status to COMPLETED
            if transaction:
                transaction.status = Transaction.Status.COMPLETED
                print("Transaction.Status.COMPLETED>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", Transaction.Status.COMPLETED)
                print("updateddddddddddddddddddddddd", transaction.status)
                transaction.description = f"Payment completed for {order.__class__.__name__} #{order.order_number if hasattr(order, 'order_number') else order.id}"
                transaction.save()
                print(f"Transaction {transaction.id} updated to COMPLETED")

            # Update user subscription and order status
            if hasattr(order, 'customer') and isinstance(order, SubscriptionOrder):
                user = order.customer
                package = order.package
                today = timezone.now().date()

                cur_expiry = getattr(user, "package_expiry_date", None)
                if cur_expiry and cur_expiry >= today:
                    user.package_expiry_date = cur_expiry + timedelta(days=package.duration_days)
                else:
                    user.package_expiry_date = today + timedelta(days=package.duration_days)
                user.package = package
                user.on_subscription = True
                user.save(update_fields=['package_expiry_date', 'package', 'on_subscription'])

                order.start_date = today
                order.end_date = user.package_expiry_date
                order.status = SubscriptionOrder.Status.ACTIVE
                order.payment_status = SubscriptionOrder.PaymentStatus.COMPLETED
                order.save(update_fields=['start_date', 'end_date', 'status', 'payment_status'])

            elif hasattr(order, 'customer') and isinstance(order, Order):
                order.status = Order.Status.PROCESSING
                order.payment_status = 'completed'
                order.save(update_fields=['status', 'payment_status'])

            payment.save(update_fields=['status', 'gateway_response'])

        elif event_type == "PAYMENT_LINK_EVENT" and payment_status in ['EXPIRED', 'FAILED']:
            payment.status = Payment.Status.FAILED
            
            # Update Transaction status to FAILED (you might want to add this status to your choices)
            if transaction:
                transaction.status = Transaction.Status.INITIATED  # or add FAILED status
                transaction.description = f"Payment failed for {order.__class__.__name__} #{order.order_number if hasattr(order, 'order_number') else order.id} - Status: {payment_status}"
                transaction.save()
                print(f"Transaction {transaction.id} updated to FAILED")
                
            if hasattr(order, 'payment_status'):
                order.payment_status = 'failed'
                order.save(update_fields=['payment_status'])
            payment.save(update_fields=['status'])

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
        if 'log_entry' in locals():
            log_entry.error_message = error_msg
            log_entry.response_status = 500
            log_entry.save()
        return HttpResponse(status=200)



def cashfree_return(request):
    """
    Handles user return from Cashfree payment gateway after payment.
    """
    order_id = request.GET.get('order_id')
    payment = None
    order = None

    if not order_id:
        # Redirect to failure view with a dummy pk=0 for missing ID
        return redirect('payment_subscription_failure', pk=0)

    payment = Payment.objects.filter(transaction_id=order_id).first()
    order = SubscriptionOrder.objects.filter(
        order_number=order_id
    ).select_related('customer').first()

    if order and payment:
        user = order.customer
        if payment.customer != user:
            payment.customer = user
            payment.save(update_fields=['customer'])

    if not payment:
        # Redirect to failure view with pk=order.pk or 0 if order is None
        return redirect('payment_subscription_failure', pk=order.pk if order else 0)

    if payment.status == Payment.Status.COMPLETED:
        order = payment.content_object
        request.session[f'order_{order_id}_completed'] = True

        if hasattr(order, 'customer'):
            if isinstance(order, Order):
                TempOrder.objects.filter(
                    user=order.customer, processed=False
                ).update(processed=True)
                return redirect('payment_order_success', pk=order.id)

            if isinstance(order, SubscriptionOrder):
                return redirect('payment_subscription_success', pk=order.id)

            return redirect('payment_subscription_failure', pk=order.pk if order else 0)

        return redirect('payment_subscription_failure', pk=order.pk if order else 0)

    # Payment not successful
    return redirect('payment_subscription_failure', pk=order.pk if order else 0)


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

class PaymentListView(LoginRequiredMixin, ListView):
    """
    Displays a paginated list of payments with filtering by user and date, and sortable columns.
    """
    model = Payment
    template_name = 'advadmin/payments/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 25

    def get_queryset(self):
        """
        Filter payments by user and date, and apply sorting from GET parameters.
        """
        user_vendor = self.request.user.vendor
        queryset = Payment.objects.select_related('customer').filter(customer__vendor=user_vendor)

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
        context['users'] = User.objects.filter(vendor=self.request.user.vendor)
        context['page_name'] = "payment_list"
        context['current_sort'] = self.request.GET.get('sort', 'created_at')
        context['current_order'] = 'asc' if self.request.GET.get('order', 'desc') == 'asc' else 'desc'
        return context

def choose_package(request, member_id):
    """
    Render available subscription packages for a user to choose from.
    """
    user_vendor = request.user.vendor
    packages = Package.objects.filter(Vendor=user_vendor)
    return render(request, 'advadmin/choose_package.html', {
        'packages': packages,
        'member_id': member_id,
    })
