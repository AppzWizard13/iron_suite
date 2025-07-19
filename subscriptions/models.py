from django.db import models
from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser
from orders.models import Payment
from products.models import Package

class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subscriptions')
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True, blank=True)

    def is_active(self):
        return self.status == 'active' and self.end_date >= timezone.now().date()

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.package.duration_days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.package.name} ({self.status})"
