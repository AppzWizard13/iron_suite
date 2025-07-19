from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class PaymentAPILog(models.Model):
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
