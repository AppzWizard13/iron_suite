from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

from accounts.models import Vendor
from core.choices import PaymentActionChoice, PaymentStatusChoice, TransactionTypeChoice, TransactionCategoryChoice, TransactionStatusChoice
User = get_user_model()

class PaymentAPILog(models.Model):
    Vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='paymentapolog')
    tenant_id = 'vendor_id'


    # Legacy FK (do not use for new logs)
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True,
        help_text="Legacy foreign key to Order (do not use for new logs)."
    )
    # New generic FK (use for new logs)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The type of the logged object (Order or SubscriptionOrder)."
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True,
        help_text="The ID of the logged object."
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    action = models.CharField(max_length=50, choices= PaymentActionChoice.choices)
    request_url = models.URLField(max_length=500)
    request_payload = models.TextField(blank=True, null=True)
    response_status = models.IntegerField(blank=True, null=True)
    response_body = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    link_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def order_id(self):
        if self.order:
            return self.order.id
        if self.content_type and self.object_id and (
            self.content_type.model == 'order' or
            self.content_type.model == 'subscriptionorder'
        ):
            return self.object_id
        return None

    def __str__(self):
        if self.order_id:
            return (
                f"{self.get_action_display()} | Order/Sub: {self.order_id} | "
                f"{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
            )
        return (
            f"{self.get_action_display()} | (No linked order) | "
            f"{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )

class Payment(models.Model):
    Vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='payment')
    tenant_id = 'vendor_id'


    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='payments_payment_content_types',  # <--- ADDED
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    payment_method = models.CharField(max_length=50, default='google_pay')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PaymentStatusChoice.choices, default=PaymentStatusChoice.PENDING)
    transaction_id = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='payments')

    def __str__(self):
        return f"Payment #{self.id} - {self.get_status_display()} ({self.content_object})"


from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import RegexValidator

class Transaction(models.Model):
    Vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='transaction')
    tenant_id = 'vendor_id'
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='payments_transaction_content_types',
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    transaction_type = models.CharField(max_length=10, choices=TransactionTypeChoice.choices)
    category = models.CharField(max_length=20, choices=TransactionCategoryChoice.choices)
    status = models.CharField(max_length=10, choices=TransactionStatusChoice.choices, default=TransactionStatusChoice.INITIATED)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    reference = models.CharField(max_length=100, blank=True)
    date = models.DateField()
    
    # Customer Information Fields
    customer_name = models.CharField(max_length=200, blank=True, help_text="Customer's full name")
    customer_email = models.EmailField(blank=True, help_text="Customer's email address")
    customer_phone = models.CharField(
        max_length=20, 
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        help_text="Customer's phone number with country code"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Check if this is being called from webhook/manual update
        skip_auto_status = kwargs.pop('skip_auto_status', False)
        
        # Auto-populate customer fields from content_object if available and not already set
        if hasattr(self, 'content_object') and self.content_object:
            # Extract customer info from related object
            if hasattr(self.content_object, 'customer'):
                customer = self.content_object.customer
                if not self.customer_name and hasattr(customer, 'name'):
                    self.customer_name = customer.name
                elif not self.customer_name and hasattr(customer, 'get_full_name'):
                    self.customer_name = customer.get_full_name()
                elif not self.customer_name and hasattr(customer, 'username'):
                    self.customer_name = customer.username
                
                if not self.customer_email and hasattr(customer, 'email'):
                    self.customer_email = customer.email
                
                if not self.customer_phone and hasattr(customer, 'phone'):
                    self.customer_phone = customer.phone
                elif not self.customer_phone and hasattr(customer, 'phone_number'):
                    self.customer_phone = str(customer.phone_number)
            
            # Only auto-set transaction properties if not skipping and this is a new record
            if not skip_auto_status and not self.pk and hasattr(self.content_object, 'status'):
                payment_status = getattr(self.content_object, 'status', None)
                if payment_status == 'completed':
                    self.transaction_type = self.Type.INCOME
                    self.category = self.Category.SALES
                    self.status = self.Status.COMPLETED
                elif payment_status == 'refunded':
                    self.transaction_type = self.Type.EXPENSE
                    self.category = self.Category.REFUND
                    self.status = self.Status.REFUNDED
                elif payment_status == 'pending':
                    self.status = self.Status.PENDING
                elif payment_status == 'initiated':
                    self.status = self.Status.INITIATED
        
        super().save(*args, **kwargs)

    def __str__(self):
        customer_info = f" - {self.customer_name}" if self.customer_name else ""
        return f"{self.get_transaction_type_display()} - {self.get_category_display()} - ₹{self.amount}{customer_info}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['Vendor', 'date']),
            models.Index(fields=['customer_email']),
            models.Index(fields=['transaction_type', 'status']),
            models.Index(fields=['created_at']),
        ]
