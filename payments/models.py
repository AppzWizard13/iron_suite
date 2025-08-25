from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

from accounts.models import Gym
User = get_user_model()

class PaymentAPILog(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='paymentapolog')
    tenant_id = 'gym_id'
    PAYMENT_ACTIONS = [
        ('INITIATE', 'Initiate Payment'),
        ('FETCH_SESSION', 'Fetch Session'),
        ('GET_ORDER', 'Get Existing Order'),
        ('CREATE_LINK', 'Create Payment Link'),
        ('WEBHOOK', 'Webhook'),
        ('ERROR', 'Error'),
    ]

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

    action = models.CharField(max_length=50, choices=PAYMENT_ACTIONS)
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
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='payment')
    tenant_id = 'gym_id'
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='payments_payment_content_types',  # <--- ADDED
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    payment_method = models.CharField(max_length=50, default='google_pay')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    transaction_id = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='payments')

    def __str__(self):
        return f"Payment #{self.id} - {self.get_status_display()} ({self.content_object})"


class Transaction(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='transaction')
    tenant_id = 'gym_id'
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

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='payments_transaction_content_types',  # <--- ADDED
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    transaction_type = models.CharField(max_length=10, choices=Type.choices)
    category = models.CharField(max_length=20, choices=Category.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.INITIATED)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    reference = models.CharField(max_length=100, blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if hasattr(self, 'content_object') and hasattr(self.content_object, 'status'):
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
        return f"{self.get_transaction_type_display()} - {self.get_category_display()} - ${self.amount}"