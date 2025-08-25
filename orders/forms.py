# forms.py
from django import forms
from .models import Order
import json

class CheckoutForm(forms.Form):
    name = forms.CharField(label='Full Name', max_length=100)
    address = forms.CharField(label='Address', widget=forms.Textarea)
    phone = forms.CharField(label='Phone Number', max_length=20)




class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'order_number',
            'customer',
            'status',
            'payment_status',
            'shipping_address',
            'billing_address',
            'subtotal',
            'tax',
            'shipping_cost',
            'discount',
            'total',
            'notes',
        ]
        widgets = {
            'shipping_address': forms.Textarea(attrs={'placeholder': 'Enter JSON data'}),
            'billing_address': forms.Textarea(attrs={'placeholder': 'Enter JSON data'}),
        }

    def clean_shipping_address(self):
        data = self.cleaned_data['shipping_address']
        try:
            json.loads(data)
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid JSON format for shipping address.")
        return data

    def clean_billing_address(self):
        data = self.cleaned_data['billing_address']
        try:
            json.loads(data)
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid JSON format for billing address.")
        return data