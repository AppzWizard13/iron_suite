from django.db import models
from django.conf import settings

from core.choices import EnquiryStatusChoice

class Enquiry(models.Model):
    enquiry_id = models.AutoField(primary_key=True)  # Auto-incremented ID
    customer_name = models.CharField(max_length=255)
    customer_number = models.CharField(max_length=15)  # Adjust length if needed
    service = models.CharField(max_length=255)  # Name of the service
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)  # Auto timestamp
    status = models.CharField(max_length=100, choices=EnquiryStatusChoice.choices, default='unread')

    def __str__(self):
        return f"{self.customer_name} - {self.service}"
