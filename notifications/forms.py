from django import forms
from .models import NotificationConfig

class NotificationConfigForm(forms.ModelForm):
    class Meta:
        model = NotificationConfig
        fields = ['days_before_expiry', 'message_template']
        widgets = {
            'days_before_expiry': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'message_template': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': "Dear {name}, your subscription expires on {expiry}. Please renew."}),
        }
        labels = {
            'days_before_expiry': 'Days Before Expiry',
            'message_template': 'Message Template',
        }