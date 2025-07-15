from django.db import models
from accounts.models import Customer
from products.models import Product
from django.contrib.auth import get_user_model
User = get_user_model()

class Cart(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    def __str__(self):
        return f"Cart #{self.id} - {self.customer}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_addition = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.price_at_addition

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart #{self.cart.id}"


class Order(models.Model):
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


    order_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.INITIATED)
    shipping_address = models.JSONField()  # Updated to use models.JSONField
    billing_address = models.JSONField()   # Updated to use models.JSONField
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
            from datetime import datetime
            today = datetime.now().strftime('%Y%m%d')
            last_order = Order.objects.filter(order_number__contains=f'ORD-{today}').order_by('order_number').last()
            if last_order:
                last_num = int(last_order.order_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.order_number = f'ORD-{today}-{new_num:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number} - {self.get_status_display()}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255)  # Store name in case product is deleted
    product_sku = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    @property
    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} x {self.product_name} in Order #{self.order.order_number}"




class Transaction(models.Model):
    class Type(models.TextChoices):
        INCOME = 'income', 'Income'
        EXPENSE = 'expense', 'Expense'

    class Category(models.TextChoices):
        SALES = 'sales', 'Sales'
        REFUND = 'refund', 'Refund'
        SALARY = 'salary', 'Salary'
        RENT = 'rent', 'Rent'
        UTILITIES = 'utilities', 'Utilities'
        MARKETING = 'marketing', 'Marketing'
        INVENTORY = 'inventory', 'Inventory'
        OTHER = 'other', 'Other'

    class Status(models.TextChoices):
        INITIATED = 'initiated', 'Initiated'
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        REFUNDED = 'refunded', 'Refunded'

    transaction_type = models.CharField(max_length=10, choices=Type.choices)
    category = models.CharField(max_length=20, choices=Category.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.INITIATED)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    reference = models.CharField(max_length=100, blank=True)  # Could be order number, invoice number, etc.
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Automatically set category and status based on payment status
        if self.payment:
            if self.payment.status == 'completed':
                self.transaction_type = self.Type.INCOME
                self.category = self.Category.SALES
                self.status = self.Status.COMPLETED
            elif self.payment.status == 'refunded':
                self.transaction_type = self.Type.EXPENSE
                self.category = self.Category.REFUND
                self.status = self.Status.REFUNDED
            elif self.payment.status == 'pending':
                self.status = self.Status.PENDING
            elif self.payment.status == 'initiated':
                self.status = self.Status.INITIATED

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.get_category_display()} - ${self.amount}"


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'

    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name='payment')
    payment_method = models.CharField(max_length=50, default='google_pay')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    transaction_id = models.CharField(max_length=100, blank=True)  # Google Pay transaction ID
    gateway_response = models.JSONField(null=True, blank=True)  # Raw response from Google Pay
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Order #{self.order.order_number} - {self.get_status_display()}"


class TempOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"TempOrder {self.id} - User: {self.user}, Product: {self.product}"
    



class GooglePayCredentials(models.Model):
    merchant_id = models.CharField(max_length=100)
    merchant_name = models.CharField(max_length=100)
    environment = models.CharField(max_length=20, choices=[('TEST', 'Test'), ('PRODUCTION', 'Production')])
    api_key = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Google Pay Credentials for {self.merchant_name} ({self.environment})"


