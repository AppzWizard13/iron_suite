import logging
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import View, TemplateView, FormView, DetailView, ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
import json
from django.db import models
from core.models import Configuration
from orders.forms import CheckoutForm, OrderForm
from .models import Order, OrderItem, Product, Cart, CartItem, SubscriptionOrder, TempOrder, Payment, Transaction

# Set up logging
logger = logging.getLogger(__name__)

class CartDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'cart/cart_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, created = Cart.objects.get_or_create(customer=self.request.user.customer)
        context['cart'] = cart
        return context

class UpdateCartItemView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        cart_item = get_object_or_404(
            CartItem, 
            id=item_id, 
            cart__customer=request.user.customer
        )
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
            
        return redirect('cart_detail')

class RemoveCartItemView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        item_id = request.POST.get('item_id')
        
        cart_item = get_object_or_404(
            CartItem, 
            id=item_id, 
            cart__customer=request.user.customer
        )
        cart_item.delete()
            
        return redirect('cart_detail')

class GetCartCountView(View):
    def get(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        if user:
            cart_count = TempOrder.objects.filter(user=user,processed=False).aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0
        else:
            cart_count = 0
        return JsonResponse({'cart_count': cart_count})

class AddToCartView(View):
    def get(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        cart_items = TempOrder.objects.filter(user=user, processed=False)

        updated_cart_items = []
        for item in cart_items:
            updated_cart_items.append({
                'product_id': str(item.product.id),
                'quantity': item.quantity,
                'timestamp': item.timestamp,
                'username': item.user.username if item.user else 'guest',
                'price': float(item.price),
                'total_price': float(item.total_price),
                'product': {
                    'id': str(item.product.product_uid),
                    'name': item.product.name,
                    'sku': item.product.sku,
                    'image': item.product.images.url if item.product.images else '',
                    'description': item.product.description
                }
            })
        
        subtotal = sum(item.get('price', 0) * item.get('quantity', 1) for item in updated_cart_items)
        total = subtotal  # Assuming no additional fees
        
        context = {
            'enable_shipping' : Configuration.objects.get(config="shipping-module"),
            'enable_tax' : Configuration.objects.get(config="tax-module"),
            'cart_items': updated_cart_items,
            'cart_subtotal': subtotal,
            'cart_total': total,
            'cart_count': sum(item.quantity for item in cart_items),            
        }
        
        return render(request, 'advadmin/cart.html', context)
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            product_sku = data.get('product_sku')
            quantity = data.get('quantity', 1)
            action = data.get('action')  # Get the action from the request data
            
            # Get the current user (if authenticated)
            user = request.user if request.user.is_authenticated else None
            
            # Fetch the product
            try:
                product = Product.objects.get(sku=product_sku)
            except Product.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Product does not exist'}, status=400)
            
            # Check if the item already exists in the cart for the given user
            existing_item = TempOrder.objects.filter(user=user, product=product, processed = False).first()
            
            if action == "add_qty":
                if existing_item:
                    existing_item.quantity += quantity
                    existing_item.total_price = existing_item.price * existing_item.quantity
                    existing_item.save()
                else:
                    TempOrder.objects.create(
                        user=user,
                        product=product,
                        quantity=quantity,
                        timestamp=timezone.now(),
                        price=product.price,
                        total_price=product.price * quantity
                    )
            elif action == "update_qty":
                if existing_item:
                    existing_item.quantity = quantity
                    existing_item.total_price = existing_item.price * existing_item.quantity
                    existing_item.save()
                else:
                    TempOrder.objects.create(
                        user=user,
                        product=product,
                        quantity=quantity,
                        timestamp=timezone.now(),
                        price=product.price,
                        total_price=product.price * quantity
                    )
            elif action == "delete":
                if existing_item:
                    existing_item.delete()
                else:
                    return JsonResponse({'success': False, 'error': 'Item not found in cart'}, status=400)
            else:
                return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)
            
            # Calculate new totals and prepare cart items for response
            cart_items = TempOrder.objects.filter(user=user,  processed = False)
            updated_cart_items = []
            for item in cart_items:
                updated_cart_items.append({
                    'product_id': str(item.product.id),
                    'quantity': item.quantity,
                    'timestamp': item.timestamp,
                    'username': item.user.username if item.user else 'guest',
                    'price': float(item.price),
                    'total_price': float(item.total_price),
                    'product': {
                        'id': str(item.product.product_uid),
                        'name': item.product.name,
                        'sku': item.product.sku,
                        'image': item.product.images.url if item.product.images else '',
                        'description': item.product.description
                    }
                })
            
            subtotal = sum(item.price * item.quantity for item in cart_items)
            total = subtotal
            
            return JsonResponse({
                'success': True,
                'cart_count': sum(item.quantity for item in cart_items),
                'cart_subtotal': subtotal,
                'cart_total': total,
                'cart_items': updated_cart_items
            })
        except Exception as e:
            logger.error(f"Error in AddToCartView: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

class CheckoutView(LoginRequiredMixin, FormView):
    template_name = 'advadmin/checkout.html'
    form_class = CheckoutForm
    success_url = '/order-confirmation/{order_id}/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user = self.request.user if self.request.user.is_authenticated else None
        cart_items = TempOrder.objects.filter(user=user, processed = False)
        
        updated_cart_items = []
        for item in cart_items:
            updated_cart_items.append({
                'product_id': item.product.id,
                'quantity': item.quantity,
                'timestamp': item.timestamp,
                'username': item.user.username if item.user else 'guest',
                'price': item.price,
                'total_price': item.total_price,
                'product': {
                    'id': item.product.id,
                    'name': item.product.name,
                    'sku': item.product.sku,
                    'image': item.product.images.url if item.product.images else '',
                    'description': item.product.description
                }
            })
        
        subtotal = sum(item.total_price for item in cart_items)
        total = subtotal  # Assuming no additional fees
        context['enable_shipping']  = Configuration.objects.get(config="shipping-module").value
        context['user'] = self.request.user
        context['cart_items'] = updated_cart_items
        context['cart_subtotal'] = subtotal
        context['cart_total'] = total
        context['cart_count'] = sum(item.quantity for item in cart_items)
        
        return context

    def form_valid(self, form):
        user = self.request.user
        cart_items = TempOrder.objects.filter(user=user, processed = False)
        print("creating_order___module")
        order = Order.objects.create(
            customer=user,
            billing_address=form.cleaned_data['billing_address'],
            shipping_address=form.cleaned_data['shipping_address'],
            phone_number=form.cleaned_data['phone_number'],
            email=form.cleaned_data['email'],
            country=form.cleaned_data['country'],
            state_province=form.cleaned_data['state_province'],
            city=form.cleaned_data['city'],
            zip_code=form.cleaned_data['zip_code'],
            status=Order.Status.PENDING,
            subtotal=self.get_subtotal(cart_items),
            tax=0,  # Assuming no tax for simplicity
            shipping_cost=0,  # Assuming free shipping for simplicity
            total=self.get_total(cart_items),
            notes=form.cleaned_data.get('notes', ''),
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                quantity=item.quantity,
                price=item.price,
            )

        cart_items.delete()

        return redirect(self.get_success_url(order.id))

    def get_success_url(self, order_id):
        return reverse('order_confirmation', kwargs={'order_id': order_id})

    def get_subtotal(self, cart_items):
        return sum(item.total_price for item in cart_items)

    def get_total(self, cart_items):
        subtotal = self.get_subtotal(cart_items)
        tax = 0  # Assuming no tax for simplicity
        shipping_cost = 0  # Assuming free shipping for simplicity
        return subtotal + tax + shipping_cost

class OrderConfirmationView(LoginRequiredMixin, TemplateView):
    template_name = 'order_confirmation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = Order.objects.get(id=self.kwargs['order_id'])
        return context

class PaymentInitiateProcess(LoginRequiredMixin, View):
    login_url = '/login/'  # Redirect to login if user is not authenticated
    success_url = '/order-confirmation/'  # Redirect URL after successful payment initiation

    def post(self, request, *args, **kwargs):
        user = request.user

        cart_items = TempOrder.objects.filter(user=user, processed = False)

        if not cart_items.exists():
            return redirect('cart-empty')  # Handle empty cart scenario

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')

        shipping_address = {
            'first_name': request.POST.get('shipping_first_name', ''),
            'last_name': request.POST.get('shipping_last_name', ''),
            'phone': request.POST.get('shipping_phone', ''),
            'email': request.POST.get('shipping_email', ''),
            'country': request.POST.get('shipping_country', ''),
            'state': request.POST.get('shipping_state', ''),
            'city': request.POST.get('shipping_city', ''),
            'address': request.POST.get('shipping_address', ''),
            'zip_code': request.POST.get('shipping_zip', ''),
        }

        billing_address = {
            'first_name': request.POST.get('billing_first_name', shipping_address['first_name']),
            'last_name': request.POST.get('billing_last_name', shipping_address['last_name']),
            'phone': request.POST.get('billing_phone', shipping_address['phone']),
            'email': request.POST.get('billing_email', shipping_address['email']),
            'country': request.POST.get('billing_country', shipping_address['country']),
            'state': request.POST.get('billing_state', shipping_address['state']),
            'city': request.POST.get('billing_city', shipping_address['city']),
            'address': request.POST.get('billing_address', shipping_address['address']),
            'zip_code': request.POST.get('billing_zip', shipping_address['zip_code']),
        }

        order = Order.objects.create(
            customer=user,
            shipping_address=shipping_address,
            billing_address=billing_address,
            status=Order.Status.PENDING,
            subtotal=self.get_subtotal(cart_items),
            tax=0,  # Assuming no tax for simplicity
            shipping_cost=0,  # Assuming free shipping for simplicity
            total=self.get_total(cart_items),
        )

        for item in cart_items:
            try:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    product_sku=item.product.sku,
                    quantity=item.quantity,
                    price=item.price,
                    tax_rate=item.product.tax_rate if hasattr(item.product, 'tax_rate') else 0,
                )
            except Exception as e:
                logger.error(f"Error creating OrderItem for cart item {item}: {e}")
        # Clear the cart items
        # cart_items.delete()

        return redirect(self.get_success_url(order.id, order.order_number))

    def get_subtotal(self, cart_items):
        return sum(item.price * item.quantity for item in cart_items)

    def get_total(self, cart_items):
        subtotal = self.get_subtotal(cart_items)
        return subtotal  # Assuming no additional fees

    def get_success_url(self, order_id, order_number):
        return f'/initiate-payment/process/{order_id}/{order_number}'

from payments.views import initiate_cashfree_payment  # ensure this is imported properly

class ProcessPaymentView(View):
    def get(self, request, order_id, order_number):
        order = get_object_or_404(Order, id=order_id, order_number=order_number)
        payment_modules = settings.PAYMENT_MODULES

        context = {
            'order': order,
            'payment_modules': payment_modules
        }

        return render(request, 'advadmin/paymentmethod.html', context)

    def post(self, request, order_id, order_number):
        order = get_object_or_404(Order, id=order_id, order_number=order_number)
        payment_modules = settings.PAYMENT_MODULES

        if request.session.get(f'order_{order.order_number}_completed', False):
            messages.warning(request, "This order has already been processed.")
            return redirect('home')

        payment_method = request.POST.get('payment_method')
        print("payment_methodpayment_methodpayment_method", payment_method)

        if payment_method == 'cod':
            payment, created = Payment.objects.get_or_create(
                order=order,
                defaults={'payment_method': 'cod', 'amount': order.total, 'status': Payment.Status.PENDING}
            )
            if not created:
                payment.payment_method = 'cod'
                payment.amount = order.total
                payment.status = Payment.Status.PENDING
                payment.save()

            transaction = Transaction.objects.create(
                transaction_type=Transaction.Type.INCOME,
                category=Transaction.Category.SALES,
                status=Transaction.Status.PENDING,
                amount=order.total,
                description=f"Payment for Order #{order.order_number} via COD",
                reference=order.order_number,
                payment=payment,
                date=order.created_at.date()
            )

            order.payment_status = Order.PaymentStatus.PENDING
            order.status = Order.Status.PROCESSING
            order.save()

            TempOrder.objects.filter(user=request.user, processed=False).update(processed=True)
            request.session[f'order_{order.order_number}_completed'] = True
            return redirect('cod_order_success', pk=order.id)

        elif payment_method == 'gpay':
            return initiate_cashfree_payment(request, order)
            # try:
            #     return initiate_cashfree_payment(request, order)
            # except Exception as e:
            #     print("error::::::::::::::::::::::::::::", str(e))
            #     messages.error(request, f"Payment error: {str(e)}")
            #     return redirect('payment_failed')

        context = {
            'order': order,
            'payment_modules': payment_modules
        }
        return render(request, 'advadmin/paymentmethod.html', context)


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'advadmin/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q', '')
        if q:
            queryset = queryset.filter(
                Q(order_number__icontains=q) |
                Q(customer__username__icontains=q) |
                Q(status__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_paginated'] = True
        context['query'] = self.request.GET.get('q', '')
        for order in context['orders']:
            order.payment_details = order.payment
        return context

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'advadmin/order_detail.html'
    context_object_name = 'order'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_paginated'] = True
        context['query'] = self.request.GET.get('q', '')
        context['order_items'] = context['order'].items.all()
        context['payment'] = context['order'].payment
        return context

class OrderEditView(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'advadmin/order_edit.html'
    success_url = reverse_lazy('order_list')

class OrderDeleteView(LoginRequiredMixin, DeleteView):
    model = Order
    success_url = reverse_lazy('order_list')
    template_name = 'orders/order_confirm_delete.html'

class CodOrderSuccessView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'advadmin/order_success.html'
    context_object_name = 'order'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_paginated'] = True
        context['query'] = self.request.GET.get('q', '')
        context['order_items'] = context['order'].items.all()
        return context
    
class PaymentOrderSuccessView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'advadmin/order_success.html'
    context_object_name = 'order'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_paginated'] = True
        context['query'] = self.request.GET.get('q', '')
        context['order_items'] = context['order'].items.all()
        return context
    
class SubscriptionOrderSuccessView(LoginRequiredMixin, DetailView):
    """
    Shows a success page after gym membership subscription payment.
    Only the member who placed the subscription can see this page.
    """
    model = SubscriptionOrder
    template_name = 'payments/payment_subscription_success.html'  # <-- Using your new template
    context_object_name = 'subscription_order'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        # Ensure only the logged-in user can view their own subscription
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(customer=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_name'] = "Iron Suite"  # <-- Change to your gym name
        return context

class PaymentOrderFailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'advadmin/order_decline.html'
    context_object_name = 'order'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_paginated'] = True
        context['query'] = self.request.GET.get('q', '')
        context['order_items'] = context['order'].items.all()
        return context

class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'advadmin/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        transaction_type = self.kwargs.get('transaction_type')
        if transaction_type and transaction_type != 'None':
            queryset = queryset.filter(transaction_type=transaction_type)
        q = self.request.GET.get('q', '')
        if q:
            queryset = queryset.filter(
                Q(reference__icontains=q) |
                Q(description__icontains=q) |
                Q(status__icontains=q)
            )
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from and date_to:
            queryset = queryset.filter(date__range=[date_from, date_to])
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_paginated'] = True
        context['query'] = self.request.GET.get('q', '')
        context['transaction_type'] = self.kwargs.get('transaction_type')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        context['status'] = self.request.GET.get('status', '')
        context['category'] = self.request.GET.get('category', '')
        context['status_choices'] = Transaction.Status.choices
        context['category_choices'] = Transaction.Category.choices
        return context

class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = 'advadmin/transaction_detail.html'
    context_object_name = 'transaction'

def clear_order_session(request):
    if request.user.is_authenticated:
        key = f'user_{request.user.username}_order_completed'
        if key in request.session:
            del request.session[key]
    return HttpResponse(status=200)