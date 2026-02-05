from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from accounts.models import CustomUser
from core.choices import TicketStatusChoice
User = get_user_model()

class SupportExecutive(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class Ticket(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    support_executive = models.ForeignKey(SupportExecutive, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=TicketStatusChoice.choices, default=TicketStatusChoice.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ticket_id = models.CharField(max_length=50, unique=True, blank=True, null=True)  # New field

    def __str__(self):
        return f"{self.title} - {self.status}"

class ChatMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='chat_messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.message[:50]}"