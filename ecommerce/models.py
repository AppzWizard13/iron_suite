from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from core.choices import (
    DriverStatusChoice, 
    RideStatusChoice, 
    VehicleTypeChoice,
    # Add these new choices to core.choices
    CustomerAddressTypeChoice,
    OrderStatusChoice,
    PaymentMethodChoice,
    PaymentStatusChoice,
    TransactionTypeChoice,
    TransactionStatusChoice,
    ReviewTypeChoice,
)
from master.models import Product, Vendor, Discount


class CustomerAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=20, choices=CustomerAddressTypeChoice.choices)
    contact_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=15)
    
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    landmark = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Customer Addresses'

    def __str__(self):
        return f"{self.user.username} - {self.address_type}"


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0.01)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

    @property
    def total_price(self):
        return self.product.final_price * float(self.quantity)


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Order(models.Model):
    # Order Details
    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ecommerce_orders')
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='vendor_orders')
    
    # Status
    status = models.CharField(max_length=20, choices=OrderStatusChoice.choices, default=OrderStatusChoice.PENDING)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Discount
    discount_code = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True, related_name='discount_orders')
    
    # Payment
    payment_method = models.CharField(max_length=20, choices=PaymentMethodChoice.choices)
    payment_status = models.CharField(max_length=20, choices=PaymentStatusChoice.choices, default=PaymentStatusChoice.PENDING)
    
    # Delivery Address
    delivery_address = models.ForeignKey(CustomerAddress, on_delete=models.PROTECT, related_name='address_orders')
    
    # Rider Assignment
    rider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='delivery_orders', limit_choices_to={'groups__name': 'Riders'})
    rider_assigned_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    # Notes
    order_notes = models.TextField(blank=True)
    special_instructions = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['vendor', 'status']),
            models.Index(fields=['rider', 'status']),
        ]

    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    
    quantity = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0.01)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Fish specific
    is_cleaned = models.BooleanField(default=False)
    special_preparation = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.order_number} - {self.product.name}"


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Order Status Histories'

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"


class Transaction(models.Model):
    transaction_id = models.CharField(max_length=100, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='transactions')
    order = models.ForeignKey(Order, on_delete=models.PROTECT, null=True, blank=True, related_name='transactions')
    
    transaction_type = models.CharField(max_length=20, choices=TransactionTypeChoice.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=TransactionStatusChoice.choices, default=TransactionStatusChoice.PENDING)
    
    # Payment Gateway Details
    payment_gateway = models.CharField(max_length=50, blank=True)
    gateway_transaction_id = models.CharField(max_length=200, blank=True)
    gateway_response = models.JSONField(null=True, blank=True)
    
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_id} - {self.user.username} - ₹{self.amount}"


class Invoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name='invoice')
    
    # Billing Details
    billing_name = models.CharField(max_length=200)
    billing_email = models.EmailField()
    billing_phone = models.CharField(max_length=15)
    billing_address = models.TextField()
    
    # Vendor Details
    vendor_name = models.CharField(max_length=200)
    vendor_gstin = models.CharField(max_length=15, blank=True)
    vendor_address = models.TextField()
    
    # Invoice Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Invoice File
    invoice_pdf = models.FileField(upload_to='invoices/', null=True, blank=True)
    
    # Timestamps
    invoice_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} - Order {self.order.order_number}"


class Rider(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rider_profile')
    # Personal Details
    phone = models.CharField(max_length=15)
    profile_photo = models.ImageField(upload_to='riders/photos/', blank=True, null=True)
    
    # Vehicle Details
    vehicle_type = models.CharField(max_length=20, choices=VehicleTypeChoice.choices, default=VehicleTypeChoice.BIKE)
    vehicle_number = models.CharField(max_length=20)
    vehicle_model = models.CharField(max_length=100, blank=True)
    
    # Documents
    license_number = models.CharField(max_length=50)
    license_photo = models.ImageField(upload_to='riders/licenses/', blank=True, null=True)
    
    # Location
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=DriverStatusChoice.choices, default=DriverStatusChoice.OFFLINE)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Metrics
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_deliveries = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.vehicle_number}"


class Review(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    review_type = models.CharField(max_length=20, choices=ReviewTypeChoice.choices)
    
    # Related objects
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField(blank=True)
    
    is_verified_purchase = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.review_type} - {self.rating}★"
