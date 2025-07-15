from django.db import models
from django.utils import timezone

class PaymentAPILog(models.Model):
    PAYMENT_ACTIONS = [
        ('INITIATE', 'Initiate Payment'),
        ('FETCH_SESSION', 'Fetch Session'),
        ('GET_ORDER', 'Get Existing Order'),
        ('CREATE_LINK', 'Create Payment Link'),
        ('WEBHOOK', 'Webhook'),
        ('ERROR', 'Error'),
    ]

    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    action = models.CharField(max_length=50, choices=PAYMENT_ACTIONS)
    request_url = models.URLField(max_length=500)
    request_payload = models.TextField(blank=True, null=True)
    response_status = models.IntegerField(blank=True, null=True)
    response_body = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    link_id = models.CharField(max_length=100, blank=True, null=True)  # Optional for tracking Cashfree link_id

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_action_display()} | Order: {self.order_id} | {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
