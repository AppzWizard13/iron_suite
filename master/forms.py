from django import forms
from .models import Category, SubCategory, Product, Discount, DeliveryZone

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image', 'is_active']

class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['category', 'name', 'slug', 'description', 'image', 'is_active']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['vendor', 'views', 'rating', 'total_reviews', 'created_at', 'updated_at']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        exclude = ['used_count', 'created_at', 'updated_at']
        widgets = {
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'valid_to': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class DeliveryZoneForm(forms.ModelForm):
    class Meta:
        model = DeliveryZone
        fields = '__all__'
        widgets = {
            'cities': forms.Textarea(attrs={'rows': 2, 'placeholder': 'City1, City2...'}),
            'pincodes': forms.Textarea(attrs={'rows': 2, 'placeholder': '682001, 682002...'}),
        }
