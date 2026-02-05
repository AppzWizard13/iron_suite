from django import forms
from .models import Order, SubscriptionOrder

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'payment_status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class SubscriptionOrderForm(forms.ModelForm):
    class Meta:
        model = SubscriptionOrder
        fields = ['status', 'payment_status']