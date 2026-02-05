from django.utils import timezone
from django.shortcuts import redirect, reverse
from django.views.generic import ListView, DeleteView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

from .models import (
    CustomerAddress, Cart, Wishlist, Order, OrderItem,
    OrderStatusHistory, Transaction, Invoice, Rider, Review
)
from core.choices import OrderStatusChoice, PaymentStatusChoice


class CustomerAddressListView(LoginRequiredMixin, ListView):
    model = CustomerAddress
    template_name = 'advadmin/customer_address_list.html'
    context_object_name = 'addresses'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # Vendor filtering
        if not user.is_superuser and hasattr(user, 'vendor'):
            queryset = queryset.filter(user__vendor=user.vendor)
        
        search_query = self.request.GET.get('q')
        sort_param = self.request.GET.get('sort')
        
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(contact_name__icontains=search_query) |
                Q(city__icontains=search_query) |
                Q(phone__icontains=search_query)
            )
        
        if sort_param == 'name':
            queryset = queryset.order_by('contact_name')
        elif sort_param == '-name':
            queryset = queryset.order_by('-contact_name')
        elif sort_param == 'city':
            queryset = queryset.order_by('city')
        elif sort_param == '-city':
            queryset = queryset.order_by('-city')
        else:
            queryset = queryset.order_by('-created_at')
            
        return queryset.select_related('user').prefetch_related('user__vendor')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = "customer_addresses"
        return context


class CustomerAddressDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomerAddress
    slug_field = "id"
    slug_url_kwarg = "id"
    success_url = reverse_lazy('ecommerce:customer_address_list')

    def delete(self, request, *args, **kwargs):
        messages.warning(request, 'Customer address deleted successfully.')
        return super().delete(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class ToggleCustomerAddressActive(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            address_id = data.get('address_id')
            action = data.get('action')
            
            address = CustomerAddress.objects.get(id=address_id)
            address.is_active = (action == 'activate')
            address.save(update_fields=['is_active', 'updated_at'])
            
            return JsonResponse({
                'success': True,
                'message': f'Address {"activated" if address.is_active else "deactivated"} successfully',
                'is_active': address.is_active
            })
        except CustomerAddress.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Address not found'}, status=404)
        except Exception as e:
            logger.error(f"Toggle address active failed: {e}")
            return JsonResponse({'success': False, 'message': 'Action failed'}, status=500)


class CartListView(LoginRequiredMixin, ListView):
    model = Cart
    template_name = 'advadmin/cart_list.html'
    context_object_name = 'carts'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # Vendor filtering
        if not user.is_superuser and hasattr(user, 'vendor'):
            queryset = queryset.filter(product__vendor=user.vendor)
        
        search_query = self.request.GET.get('q')
        sort_param = self.request.GET.get('sort')
        
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(product__name__icontains=search_query) |
                Q(product__sku__icontains=search_query)
            )
        
        if sort_param == 'user':
            queryset = queryset.order_by('user__username')
        elif sort_param == '-user':
            queryset = queryset.order_by('-user__username')
        elif sort_param == '-total':
            queryset = queryset.order_by('-total_price')
        else:
            queryset = queryset.order_by('-updated_at')
            
        return queryset.select_related('user', 'product__vendor')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = "carts"
        return context


class CartDeleteView(LoginRequiredMixin, DeleteView):
    model = Cart
    slug_field = "id"
    slug_url_kwarg = "id"
    success_url = reverse_lazy('ecommerce:cart_list')

    def delete(self, request, *args, **kwargs):
        messages.warning(request, 'Cart item deleted successfully.')
        return super().delete(request, *args, **kwargs)


class WishlistListView(LoginRequiredMixin, ListView):
    model = Wishlist
    template_name = 'advadmin/wishlist_list.html'
    context_object_name = 'wishlists'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # Vendor filtering
        if not user.is_superuser and hasattr(user, 'vendor'):
            queryset = queryset.filter(product__vendor=user.vendor)
        
        search_query = self.request.GET.get('q')
        sort_param = self.request.GET.get('sort')
        
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(product__name__icontains=search_query) |
                Q(product__sku__icontains=search_query)
            )
        
        if sort_param == 'user':
            queryset = queryset.order_by('user__username')
        elif sort_param == '-user':
            queryset = queryset.order_by('-user__username')
        else:
            queryset = queryset.order_by('-created_at')
            
        return queryset.select_related('user', 'product__vendor')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = "wishlists"
        return context


class WishlistDeleteView(LoginRequiredMixin, DeleteView):
    model = Wishlist
    slug_field = "id"
    slug_url_kwarg = "id"
    success_url = reverse_lazy('ecommerce:wishlist_list')

    def delete(self, request, *args, **kwargs):
        messages.warning(request, 'Wishlist item deleted successfully.')
        return super().delete(request, *args, **kwargs)


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'advadmin/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        if not user.is_superuser and hasattr(user, 'vendor'):
            queryset = queryset.filter(vendor=user.vendor)
        
        search_query = self.request.GET.get('q')
        status_filter = self.request.GET.get('status')
        sort_param = self.request.GET.get('sort')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if search_query:
            queryset = queryset.filter(
                Q(order_number__icontains=search_query) |
                Q(user__username__icontains=search_query) |
                Q(vendor__name__icontains=search_query) |
                Q(delivery_address__contact_name__icontains=search_query)
            )
        
        if sort_param == 'number':
            queryset = queryset.order_by('order_number')
        elif sort_param == '-number':
            queryset = queryset.order_by('-order_number')
        elif sort_param == '-total':
            queryset = queryset.order_by('-total_amount')
        else:
            queryset = queryset.order_by('-created_at')
            
        return queryset.select_related(
            'user', 'vendor', 'delivery_address', 'discount_code'
        ).prefetch_related('orderitem_set')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = "orders"
        context['statuses'] = OrderStatusChoice.choices
        context['payment_statuses'] = getattr(PaymentStatusChoice, 'choices', [])
        context['riders'] = Rider.objects.filter(is_active=True).select_related('user')[:20]
        return context


class OrderDeleteView(LoginRequiredMixin, DeleteView):
    model = Order
    slug_field = "order_number"
    slug_url_kwarg = "order_number"
    success_url = reverse_lazy('ecommerce:order_list')

    def delete(self, request, *args, **kwargs):
        messages.warning(request, 'Order deleted successfully.')
        return super().delete(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class ToggleOrderStatus(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            order_number = data.get('order_number')
            status = data.get('status')
            
            if status not in dict(OrderStatusChoice.choices):
                return JsonResponse({'success': False, 'message': 'Invalid status'}, status=400)
            
            order = Order.objects.select_related('vendor').get(order_number=order_number)
            order.status = status
            order.save(update_fields=['status', 'updated_at'])
            
            return JsonResponse({
                'success': True,
                'status_display': order.get_status_display(),
                'status': status
            })
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found'}, status=404)
        except Exception as e:
            logger.error(f"Toggle order status failed: {e}")
            return JsonResponse({'success': False, 'message': 'Action failed'}, status=500)


class OrderItemListView(LoginRequiredMixin, ListView):
    model = OrderItem
    template_name = 'advadmin/order_item_list.html'
    context_object_name = 'order_items'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # Vendor filtering
        if not user.is_superuser and hasattr(user, 'vendor'):
            queryset = queryset.filter(order__vendor=user.vendor)
        
        search_query = self.request.GET.get('q')
        
        if search_query:
            queryset = queryset.filter(
                Q(product__name__icontains=search_query) |
                Q(order__order_number__icontains=search_query) |
                Q(product__sku__icontains=search_query)
            )
        
        return queryset.select_related(
            'order__user', 'order__vendor', 'product__vendor'
        ).order_by('-order__created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = "order_items"
        return context


class OrderItemDeleteView(LoginRequiredMixin, DeleteView):
    model = OrderItem
    slug_field = "id"
    slug_url_kwarg = "id"
    success_url = reverse_lazy('ecommerce:order_item_list')

    def delete(self, request, *args, **kwargs):
        messages.warning(request, 'Order item deleted successfully.')
        return super().delete(request, *args, **kwargs)


class OrderStatusHistoryListView(LoginRequiredMixin, ListView):
    model = OrderStatusHistory
    template_name = 'advadmin/order_status_history_list.html'
    context_object_name = 'histories'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # Vendor filtering
        if not user.is_superuser and hasattr(user, 'vendor'):
            queryset = queryset.filter(order__vendor=user.vendor)
        
        search_query = self.request.GET.get('q')
        
        if search_query:
            queryset = queryset.filter(
                Q(order__order_number__icontains=search_query) |
                Q(status__icontains=search_query)
            )
        
        return queryset.select_related(
            'order__user', 'order__vendor', 'updated_by'
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = "order_status_history"
        return context


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'advadmin/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # Vendor filtering
        if not user.is_superuser and hasattr(user, 'vendor'):
            queryset = queryset.filter(order__vendor=user.vendor)
        
        search_query = self.request.GET.get('q')
        sort_param = self.request.GET.get('sort')
        
        if search_query:
            queryset = queryset.filter(
                Q(transaction_id__icontains=search_query) |
                Q(user__username__icontains=search_query) |
                Q(order__order_number__icontains=search_query)
            )
        
        if sort_param == 'amount':
            queryset = queryset.order_by('-amount')
        elif sort_param == '-amount':
            queryset = queryset.order_by('amount')
        else:
            queryset = queryset.order_by('-created_at')
            
        return queryset.select_related('user', 'order__vendor')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = "transactions"
        return context


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'advadmin/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # Vendor filtering
        if not user.is_superuser and hasattr(user, 'vendor'):
            queryset = queryset.filter(order__vendor=user.vendor)
        
        search_query = self.request.GET.get('q')
        
        if search_query:
            queryset = queryset.filter(
                Q(invoice_number__icontains=search_query) |
                Q(order__order_number__icontains=search_query)
            )
        
        return queryset.select_related('order__user', 'order__vendor').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = "invoices"
        return context


class RiderListView(LoginRequiredMixin, ListView):
    model = Rider
    template_name = 'advadmin/rider_list.html'
    context_object_name = 'riders'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        sort_param = self.request.GET.get('sort')
        
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(vehicle_number__icontains=search_query) |
                Q(phone__icontains=search_query)
            )
        
        if sort_param == 'name':
            queryset = queryset.order_by('user__first_name', 'user__last_name')
        elif sort_param == '-name':
            queryset = queryset.order_by('-user__first_name')
        elif sort_param == 'rating':
            queryset = queryset.order_by('-rating')
        else:
            queryset = queryset.order_by('-created_at')
            
        return queryset.select_related('user').prefetch_related('user__rider')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = "riders"
        return context


class RiderDeleteView(LoginRequiredMixin, DeleteView):
    model = Rider
    slug_field = "id"
    slug_url_kwarg = "id"
    success_url = reverse_lazy('ecommerce:rider_list')

    def delete(self, request, *args, **kwargs):
        messages.warning(request, 'Rider deleted successfully.')
        return super().delete(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class ToggleRiderActive(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            rider_id = data.get('rider_id')
            action = data.get('action')
            
            rider = Rider.objects.get(id=rider_id)
            rider.is_active = (action == 'activate')
            rider.save(update_fields=['is_active', 'updated_at'])
            
            return JsonResponse({
                'success': True,
                'message': f'Rider {"activated" if rider.is_active else "deactivated"} successfully',
                'is_active': rider.is_active
            })
        except Rider.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Rider not found'}, status=404)
        except Exception as e:
            logger.error(f"Toggle rider active failed: {e}")
            return JsonResponse({'success': False, 'message': 'Action failed'}, status=500)


class ReviewListView(LoginRequiredMixin, ListView):
    model = Review
    template_name = 'advadmin/review_list.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # Vendor filtering
        if not user.is_superuser and hasattr(user, 'vendor'):
            queryset = queryset.filter(
                Q(product__vendor=user.vendor) | Q(vendor=user.vendor)
            )
        
        search_query = self.request.GET.get('q')
        rating_filter = self.request.GET.get('rating')
        
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(review_text__icontains=search_query) |
                Q(product__name__icontains=search_query)
            )
        
        if rating_filter:
            queryset = queryset.filter(rating=rating_filter)
            
        return queryset.select_related(
            'order', 'user', 'product', 'vendor', 'rider'
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = "reviews"
        return context


class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    model = Review
    slug_field = "id"
    slug_url_kwarg = "id"
    success_url = reverse_lazy('ecommerce:review_list')

    def delete(self, request, *args, **kwargs):
        messages.warning(request, 'Review deleted successfully.')
        return super().delete(request, *args, **kwargs)


class AssignRiderView(LoginRequiredMixin, View):
    """Assign rider to order via POST from admin modal"""
    
    def post(self, request, *args, **kwargs):
        order_number = request.POST.get('order_number')
        rider_id = request.POST.get('rider_id')

        if not order_number or not rider_id:
            messages.error(request, "Missing order number or rider selection.")
            return redirect('ecommerce:order_list')

        try:
            order = Order.objects.select_related('vendor', 'rider').get(order_number=order_number)
        except Order.DoesNotExist:
            messages.error(request, f"Order {order_number} not found.")
            return redirect('ecommerce:order_list')

        try:
            rider = Rider.objects.select_related('user').get(id=rider_id, is_active=True)
        except Rider.DoesNotExist:
            messages.error(request, "Selected rider not found or inactive.")
            return redirect('ecommerce:order_list')

        # Check if order is eligible for rider assignment
        if order.status in ['delivered', 'cancelled']:
            messages.error(request, "Cannot assign rider to completed/cancelled order.")
            return redirect('ecommerce:order_list')

        # Assign rider
        order.rider = rider
        order.rider_assigned_at = timezone.now()
        order.save(update_fields=['rider', 'rider_assigned_at', 'updated_at'])

        messages.success(
            request, 
            f"Rider {rider.user.get_full_name()} assigned to order #{order.order_number}."
        )
        return redirect('ecommerce:order_list')
