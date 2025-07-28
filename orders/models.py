from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from accounts.models import Customer, Gym
from products.models import Package, Product
from django.conf import settings
from django_multitenant.mixins import TenantModelMixin

User = get_user_model()

class Cart(models.Model, TenantModelMixin):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='cart')
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='carts')
    tenant_id = 'gym_id'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    def __str__(self):
        return f"Cart #{self.id} - {self.customer}"

    def save(self, *args, **kwargs):
        if self.customer and not self.gym:
            self.gym = self.customer.gym
        super().save(*args, **kwargs)


class CartItem(models.Model, TenantModelMixin):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='cart_items')
    tenant_id = 'gym_id'
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_addition = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.price_at_addition

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart #{self.cart.id}"

    def save(self, *args, **kwargs):
        if self.cart and not self.gym:
            self.gym = self.cart.gym
        super().save(*args, **kwargs)


class Order(models.Model, TenantModelMixin):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'
        RETURN = 'return', 'Return'

    class PaymentStatus(models.TextChoices):
        INITIATED = 'initiated', 'Initiated'
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        REFUNDED = 'refunded', 'Refunded'

    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='orders')
    tenant_id = 'gym_id'

    order_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.INITIATED)
    shipping_address = models.JSONField()
    billing_address = models.JSONField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            today = timezone.now().strftime('%Y%m%d')
            last_order = Order.objects.filter(order_number__contains=f'ORD-{today}').order_by('order_number').last()
            new_num = int(last_order.order_number.split('-')[-1]) + 1 if last_order else 1
            self.order_number = f'ORD-{today}-{new_num:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number} - {self.get_status_display()}"


class OrderItem(models.Model, TenantModelMixin):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='order_items')
    tenant_id = 'gym_id'

    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255)
    product_sku = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    @property
    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} x {self.product_name} in Order #{self.order.order_number}"

    def save(self, *args, **kwargs):
        if self.order and not self.gym:
            self.gym = self.order.gym
        super().save(*args, **kwargs)


class SubscriptionOrder(models.Model, TenantModelMixin):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACTIVE = 'active', 'Active'
        EXPIRED = 'expired', 'Expired'
        CANCELLED = 'cancelled', 'Cancelled'

    class PaymentStatus(models.TextChoices):
        INITIATED = 'initiated', 'Initiated'
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        REFUNDED = 'refunded', 'Refunded'
        FAILED = 'failed', 'Failed'

    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='subscription_orders')
    tenant_id = 'gym_id'

    order_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='subscription_orders')
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, related_name='orders')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.INITIATED)
    payment_gateway = models.CharField(max_length=50, default='cashfree')
    start_date = models.DateField()
    end_date = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=18)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_recurring = models.BooleanField(default=False)
    auto_renew = models.BooleanField(default=False)
    invoice_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            today = timezone.now().strftime('%Y%m%d')
            last_order = SubscriptionOrder.objects.filter(
                order_number__contains=f'{settings.SUBSCRIPTION_ORDER_PREFIX}{today}'
            ).order_by('order_number').last()
            new_num = int(last_order.order_number.rsplit('-', 1)[-1]) + 1 if last_order else 1
            self.order_number = f'{settings.SUBSCRIPTION_ORDER_PREFIX}{today}-{new_num:04d}'
        if not self.end_date and self.package:
            self.end_date = self.start_date + timedelta(days=self.package.duration_days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"SubscriptionOrder #{self.order_number} - {self.get_status_display()}"


class TempOrder(models.Model, TenantModelMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='temp_orders')
    tenant_id = 'gym_id'
    quantity = models.PositiveIntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"TempOrder {self.id} - User: {self.user}, Product: {self.product}"
