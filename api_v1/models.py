from django.db import models
from django.conf import settings
from django.utils import timezone

class UserFCMToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fcm_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - FCM Token"

class Alert(models.Model):
    ALERT_TYPES = [
        ('subscription_expired', 'Subscription Expired'),
        ('subscription_reminder', 'Subscription Reminder'),
        ('general', 'General Alert'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES, default='general')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Alert for {self.user.username}: {self.alert_type}"
