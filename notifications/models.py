from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class NotificationConfig(models.Model):
    days_before_expiry = models.PositiveIntegerField(default=3)
    message_template = models.TextField(default="Dear {name}, your subscription expires on {expiry}. Please renew.")

    def __str__(self):
        return f"Config ({self.days_before_expiry} days): {self.message_template[:20]}"


class NotificationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    sent_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField()
    error_message = models.TextField(blank=True, null=True)
    message_body = models.TextField()
