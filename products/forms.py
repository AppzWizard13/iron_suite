from django import forms
from .models import *
from django.utils.safestring import mark_safe
from markdownx.widgets import MarkdownxWidget

class CategoryForm(forms.ModelForm):
    image = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Category
        fields = ['name', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class subcategoryForm(forms.ModelForm):
    class Meta:
        model = subcategory
        fields = ['name', 'category', 'description']

    def __init__(self, *args, **kwargs):
        super(subcategoryForm, self).__init__(*args, **kwargs)
        categories = Category.objects.all()

        if categories.exists():
            self.fields['category'].queryset = categories
        else:
            self.fields['category'].choices = [("", "No Category Found")]
            self.fields['category'].widget.attrs['disabled'] = 'disabled'  # Disable dropdown

class ProductForm(forms.ModelForm):
    image_1 = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    image_2 = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    image_3 = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    image_4 = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Product
        fields = [
            'name', 'is_active', 'images', 'image_1', 'image_2', 'image_3','image_4' ,'catalogues','sku', 
            'category', 'price', 'subcategory', 'specifications', 'description', 'additional_information','country_of_origin'
        ]
        widgets = {
            'specifications': MarkdownxWidget(attrs={'class': 'form-control'}),
            'description': MarkdownxWidget(attrs={'class': 'form-control'}),
            'additional_information': MarkdownxWidget(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'subcategory': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'catalogues': forms.TextInput(attrs={'class': 'form-control'}),
            'images': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'country_of_origin': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        exclude = ['gym']  # ✅ exclude gym so it doesn't expect user input
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'duration_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount_type': forms.Select(attrs={'class': 'form-control'}),
            'discount_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'features': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'e.g. {"personal_trainer": true, "diet_plan": false}'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
