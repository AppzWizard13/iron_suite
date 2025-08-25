from django import forms
from .models import BusinessDetails

class BusinessDetailsForm(forms.ModelForm):
    # Removed DAY_CHOICES and MultipleChoiceField for closed_days
    
    # Customizing time fields to use time picker
    opening_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        help_text="Opening time (same for all working days)"
    )
    closing_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        help_text="Closing time (same for all working days)"
    )
    
    # Changed closed_days to CharField with max_length=20
    closed_days = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Sunday, Monday or Sun, Mon'
        }),
        help_text="Enter closed days (max 20 characters)"
    )
    
    class Meta:
        model = BusinessDetails
        fields = '__all__'
        widgets = {
            'offline_address': forms.Textarea(attrs={'rows': 3}),
            'company_tagline': forms.TextInput(attrs={'placeholder': 'Your company tagline'}),
            'gstn': forms.TextInput(attrs={'placeholder': 'xxxxxxxxxxxxxxx'}),
            'company_instagram': forms.TextInput(attrs={'placeholder': 'xxxxxxxxxxxxxxx'}),
            'company_facebook': forms.TextInput(attrs={'placeholder': 'xxxxxxxxxxxxxxx'}),
            'company_email_ceo': forms.TextInput(attrs={'placeholder': 'xxxxxxxxxxxxxxx'}),
            'info_mobile': forms.TextInput(attrs={'placeholder': '+1234567890'}),
            'complaint_mobile': forms.TextInput(attrs={'placeholder': '+1234567890'}),
            'sales_mobile': forms.TextInput(attrs={'placeholder': '+1234567890'}),
            'map_location': forms.URLInput(attrs={'placeholder': 'https://maps.google.com/...'}),
            'company_logo': forms.FileInput(attrs={'accept': 'image/*'}),
            'company_logo_svg': forms.FileInput(attrs={'accept': 'image/svg+xml'}),
            'company_favicon': forms.FileInput(attrs={'accept': 'image/*'}),
            'breadcrumb_image': forms.FileInput(attrs={'accept': 'image/*'}),
            'about_page_image': forms.FileInput(attrs={'accept': 'image/*'}),
        }
        help_texts = {
            'company_logo_svg': 'Upload SVG version of your logo for better quality',
            'company_favicon': 'Recommended size: 32x32 or 16x16 pixels (ICO/PNG format)',
            'map_location': 'Embed URL from Google Maps',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ensure required fields
        for field in ['company_name', 'info_mobile', 'info_email', 'gstn','company_instagram', 'company_facebook', 'company_email_ceo',
                      'complaint_mobile', 'complaint_email',
                      'sales_mobile', 'sales_email', 'company_logo_svg','breadcrumb_image', 'about_page_image']:
            self.fields[field].required = True

        # Ensure the time fields have values
        if self.instance and self.instance.pk:  # Check if instance exists
            if self.instance.opening_time:
                self.fields['opening_time'].initial = self.instance.opening_time.strftime('%H:%M')
            if self.instance.closing_time:
                self.fields['closing_time'].initial = self.instance.closing_time.strftime('%H:%M')
        else:
            # Set default values explicitly
            self.fields['opening_time'].initial = '09:00'
            self.fields['closing_time'].initial = '17:00'
        
    def clean(self):
        cleaned_data = super().clean()
        opening_time = cleaned_data.get('opening_time')
        closing_time = cleaned_data.get('closing_time')
        
        # Validate that closing time is after opening time
        if opening_time and closing_time and opening_time >= closing_time:
            raise forms.ValidationError(
                "Closing time must be after opening time"
            )
        
        return cleaned_data
    
    def clean_closed_days(self):
        # No need to convert list to string anymore since we're using CharField directly
        closed_days = self.cleaned_data.get('closed_days', '')
        if len(closed_days) > 20:
            raise forms.ValidationError(
                "Closed days must be 20 characters or less"
            )
        return closed_days
    

from django import forms
from .models import Configuration

class ConfigurationForm(forms.ModelForm):
    class Meta:
        model = Configuration
        fields = ['config', 'value']
        widgets = {
            'config': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.TextInput(attrs={'class': 'form-control'}),
        }