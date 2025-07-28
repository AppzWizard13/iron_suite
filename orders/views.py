import logging
import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import (
    View, TemplateView, FormView, DetailView, ListView, UpdateView, DeleteView
)

from core.models import Configuration
from orders.forms import CheckoutForm, OrderForm
from payments.models import Payment, Transaction
from payments.views import initiate_cashfree_payment  # Make sure it's imported properly
from .models import Order, OrderItem, Product, Cart, CartItem, SubscriptionOrder, TempOrder

logger = logging.getLogger(__name__)

class CartDetailView(LoginRequiredMixin, TemplateView):
    """
    Display detailed view of the customer's cart.
    """
    template_name = 'cart/cart_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, _ = Cart.objects.get_or_create(customer=self.request.user.customer)
        context['cart'] = cart
        return context


class UpdateCartItemView(LoginRequiredMixin, View):
    """
    Update quantity for a specific item in the cart.
    """

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
    """
    Remove a specific item from the cart.
    """

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
    """
    Get the number of items in the user's cart.
    """

    def get(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        cart_count = 0
        if user:
            cart_count = (
                TempOrder.objects.filter(user=user, processed=False)
                .aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0
            )
        return JsonResponse({'cart_count': cart_count})


class AddToCartView(View):
    """
    Display or update the temporary cart using AJAX via GET and POST.
    GET: Returns cart contents for current user.
    POST: Updates cart (add, update, delete).
    """

    def get(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        cart_items = TempOrder.objects.filter(user=user, processed=False)

        updated_cart_items = [{
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
        } for item in cart_items]

        subtotal = sum(item.get('price', 0) * item.get('quantity', 1) for item in updated_cart_items)
        total = subtotal  # No additional fees assumed

        context = {
            'enable_shipping': Configuration.objects.get(config="shipping-module"),
            'enable_tax': Configuration.objects.get(config="tax-module"),
            'cart_items': updated_cart_items,
            'cart_subtotal': subtotal,
            'cart_total': total,
            'cart_count': sum(item.quantity for item in cart_items),
        }
        return render(request, 'advadmin/cart.html', context)

    def post(self, request, *args, **kwargs):
        """
        Accepts action: add_qty, update_qty, delete. Manages TempOrder for user.
        """
        try:
            data = json.loads(request.body)
            product_sku = data.get('product_sku')
            quantity = int(data.get('quantity', 1))
            action = data.get('action')

            user = request.user if request.user.is_authenticated else None

            product = get_object_or_404(Product, sku=product_sku)
            existing_item = TempOrder.objects.filter(
                user=user, product=product, processed=False
            ).first()

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

            cart_items = TempOrder.objects.filter(user=user, processed=False)
            updated_cart_items = [{
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
            } for item in cart_items]

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
    """
    Checkout view that creates an Order from the `TempOrder` items on form submission.
    """
    template_name = 'advadmin/checkout.html'
    form_class = CheckoutForm
    success_url = '/order-confirmation/{order_id}/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        cart_items = TempOrder.objects.filter(user=user, processed=False)

        updated_cart_items = [{
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
        } for item in cart_items]

        subtotal = sum(item.total_price for item in cart_items)
        total = subtotal  # No additional fees assumed

        context.update({
            'enable_shipping': Configuration.objects.get(config="shipping-module").value,
            'user': user,
            'cart_items': updated_cart_items,
            'cart_subtotal': subtotal,
            'cart_total': total,
            'cart_count': sum(item.quantity for item in cart_items),
        })
        return context

    def form_valid(self, form):
        user = self.request.user
        cart_items = TempOrder.objects.filter(user=user, processed=False)

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
            tax=0,  # No tax assumed
            shipping_cost=0,  # Free shipping assumed
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
        return subtotal  # No fees/tax assumed


class OrderConfirmationView(LoginRequiredMixin, TemplateView):
    """
    Displays a confirmation page for a specific order after checkout.
    """
    template_name = 'order_confirmation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = get_object_or_404(Order, id=self.kwargs['order_id'])
        return context


class PaymentInitiateProcess(LoginRequiredMixin, View):
    """
    Initiate an order and redirect to payment process.
    """
    login_url = '/login/'
    success_url = '/order-confirmation/'

    def post(self, request, *args, **kwargs):
        user = request.user
        cart_items = TempOrder.objects.filter(user=user, processed=False)
        if not cart_items.exists():
            return redirect('cart-empty')

        # Billing and shipping extraction utility can be a separate method if reused
        shipping_address = {k: request.POST.get(f'shipping_{k}', '') for k in
                            ('first_name', 'last_name', 'phone', 'email', 'country', 'state', 'city', 'address', 'zip')}
        billing_address = {k: request.POST.get(f'billing_{k}', shipping_address.get(k, '')) for k in
                           ('first_name', 'last_name', 'phone', 'email', 'country', 'state', 'city', 'address', 'zip')}

        order = Order.objects.create(
            customer=user,
            shipping_address=shipping_address,
            billing_address=billing_address,
            status=Order.Status.PENDING,
            subtotal=self.get_subtotal(cart_items),
            tax=0,
            shipping_cost=0,
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
                    tax_rate=getattr(item.product, 'tax_rate', 0)
                )
            except Exception as e:
                logger.error(f"Error creating OrderItem for cart item {item}: {e}")
        return redirect(self.get_success_url(order.id, order.order_number))

    def get_subtotal(self, cart_items):
        return sum(item.price * item.quantity for item in cart_items)

    def get_total(self, cart_items):
        subtotal = self.get_subtotal(cart_items)
        return subtotal

    def get_success_url(self, order_id, order_number):
        return f'/initiate-payment/process/{order_id}/{order_number}'


class ProcessPaymentView(View):
    """
    View for processing payment selection and redirection for an order.
    """

    def get(self, request, order_id, order_number):
        order = get_object_or_404(Order, id=order_id, order_number=order_number)
        context = {
            'order': order,
            'payment_modules': settings.PAYMENT_MODULES,
        }
        return render(request, 'advadmin/paymentmethod.html', context)

    def post(self, request, order_id, order_number):
        order = get_object_or_404(Order, id=order_id, order_number=order_number)
        payment_modules = settings.PAYMENT_MODULES

        if request.session.get(f'order_{order.order_number}_completed', False):
            messages.warning(request, "This order has already been processed.")
            return redirect('home')

        payment_method = request.POST.get('payment_method')
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
            Transaction.objects.create(
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

        # Fallback to payment method selection
        context = {
            'order': order,
            'payment_modules': payment_modules
        }
        return render(request, 'advadmin/paymentmethod.html', context)


class OrderListView(LoginRequiredMixin, ListView):
    """
    Displays a list of orders with searching and pagination.
    """
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
            order.payment_details = getattr(order, 'payment', None)
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    """
    Detailed view for a specific order.
    """
    model = Order
    template_name = 'advadmin/order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_paginated'] = True
        context['query'] = self.request.GET.get('q', '')
        context['order_items'] = self.object.items.all()
        context['payment'] = getattr(self.object, 'payment', None)
        return context


class OrderEditView(LoginRequiredMixin, UpdateView):
    """
    Allows editing an order.
    """
    model = Order
    form_class = OrderForm
    template_name = 'advadmin/order_edit.html'
    success_url = reverse_lazy('order_list')


class OrderDeleteView(LoginRequiredMixin, DeleteView):
    """
    Allows deletion of an order.
    """
    model = Order
    success_url = reverse_lazy('order_list')
    template_name = 'orders/order_confirm_delete.html'


class CodOrderSuccessView(LoginRequiredMixin, DetailView):
    """
    Displays order success page for COD payments.
    """
    model = Order
    template_name = 'advadmin/order_success.html'
    context_object_name = 'order'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_paginated'] = True
        context['query'] = self.request.GET.get('q', '')
        context['order_items'] = self.object.items.all()
        return context


class PaymentOrderSuccessView(LoginRequiredMixin, DetailView):
    """
    Displays order success page for successful online payment.
    """
    model = Order
    template_name = 'advadmin/order_success.html'
    context_object_name = 'order'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_paginated'] = True
        context['query'] = self.request.GET.get('q', '')
        context['order_items'] = self.object.items.all()
        return context


class SubscriptionOrderSuccessView(LoginRequiredMixin, DetailView):
    """
    Displays order success for a SubscriptionOrder.
    """
    model = SubscriptionOrder
    template_name = 'advadmin/payment_subscription_success.html'
    context_object_name = 'subscription_order'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(customer=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_name'] = "Your Gym Name"
        return context


class PaymentOrderFailView(LoginRequiredMixin, DetailView):
    """
    Displays failed payment (decline) page for an order.
    """
    model = Order
    template_name = 'advadmin/order_decline.html'
    context_object_name = 'order'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_paginated'] = True
        context['query'] = self.request.GET.get('q', '')
        context['order_items'] = self.object.items.all()
        return context


class TransactionListView(LoginRequiredMixin, ListView):
    """
    Displays a list of transactions with filtering and pagination.
    """
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
        context.update({
            'is_paginated': True,
            'query': self.request.GET.get('q', ''),
            'transaction_type': self.kwargs.get('transaction_type'),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
            'status': self.request.GET.get('status', ''),
            'category': self.request.GET.get('category', ''),
            'status_choices': Transaction.Status.choices,
            'category_choices': Transaction.Category.choices,
        })
        return context


class TransactionDetailView(LoginRequiredMixin, DetailView):
    """
    Displays the detail view for a transaction.
    """
    model = Transaction
    template_name = 'advadmin/transaction_detail.html'
    context_object_name = 'transaction'


def clear_order_session(request):
    """
    Remove the order completed session key for the user.
    """
    if request.user.is_authenticated:
        key = f'user_{request.user.username}_order_completed'
        if key in request.session:
            del request.session[key]
    return HttpResponse(status=200)


class SubscriptionOrderListView(ListView):
    """
    List view for Subscription Orders with filtering, sorting, and pagination.
    """
    model = SubscriptionOrder
    template_name = 'advadmin/orders/subscription_order_list.html'
    context_object_name = 'orders'
    paginate_by = 20  # Default page size

    def get_queryset(self):
        """
        Apply filters, sorting, and select_related for efficiency.
        Accepts 'q' (search), 'status', 'date', and 'sort' from GET params.
        """
        user = self.request.user
        queryset = super().get_queryset().filter(gym=user.gym)  # Filter by tenant

        # Filters
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(customer__first_name__icontains=q) |
                Q(customer__last_name__icontains=q) |
                Q(customer__member_id__icontains=q)
            )

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        date = self.request.GET.get('date')
        if date:
            queryset = queryset.filter(created_at__date=date)

        # Dynamic page size
        paginate_by = self.request.GET.get('paginate_by')
        if paginate_by and paginate_by.isdigit() and int(paginate_by) > 0:
            self.paginate_by = int(paginate_by)

        # Sorting
        sort = self.request.GET.get('sort', 'start_date_desc')
        order_map = {
            'status': 'status',
            'status_desc': '-status',
            'start_date': 'start_date',
            'start_date_desc': '-start_date',
            'created_at': 'created_at',
            'created_at_desc': '-created_at'
        }
        queryset = queryset.order_by(order_map.get(sort, '-created_at'))

        return queryset.select_related('customer', 'package')

    def get_context_data(self, **kwargs):
        """
        Add filters, status choices, and page size options to template context.
        """
        context = super().get_context_data(**kwargs)
        context.update({
            'status_choices': [t[0] for t in SubscriptionOrder.Status.choices],
            'active_filters': {
                'q': self.request.GET.get('q', ''),
                'status': self.request.GET.get('status', ''),
                'date': self.request.GET.get('date', ''),
                'sort': self.request.GET.get('sort', 'start_date_desc')
            },
            'paginate_by': self.request.GET.get('paginate_by', self.paginate_by),
            'page_sizes': [10, 20, 50, 100],
            'model_name': 'subscriptionorder',
            'page_name': 'subscription_orders'
        })
        return context
