from django import forms
from .models import CustomUser, Customer
from .utils import generate_username  # Import generate_username function.
from django.contrib.auth.hashers import make_password
from django.db.models import Max
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Max
from .models import CustomUser, SocialMedia

class CustomUserForm(UserCreationForm):
    password1 = forms.CharField(
        required=False,  # Make password optional
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'}),
        label="Password"
    )
    password2 = forms.CharField(
        required=False,  # Make password optional
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        label="Confirm Password"
    )

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'phone_number', 'email', 'staff_role',
            'address', 'city', 'state', 'pincode', 'date_of_birth', 'gender',
            'password1', 'password2', 'is_active', 'is_staff',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Last Name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Address', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter State'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Pincode'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Male', 'Male'), 
                ('Female', 'Female'), 
                ('Other', 'Other')
            ]),
            'staff_role': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Admin', 'Admin'), 
                ('Manager', 'Manager'), 
                ('Employee', 'Employee')
            ]),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If updating an existing user, make password fields optional
        if self.instance and self.instance.pk:
            self.fields['password1'].required = False
            self.fields['password2'].required = False

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Auto-generate member_id
        if not instance.member_id:
            max_member_id = CustomUser.objects.aggregate(Max('member_id'))['member_id__max'] or 0
            instance.member_id = max_member_id + 1  

        # Auto-generate username
        instance.username = f"MEMBER{str(instance.member_id).zfill(5)}"

        # Set password only if provided
        if self.cleaned_data.get('password1'):
            instance.set_password(self.cleaned_data['password1'])

        if commit:
            instance.save()
        return instance



User = get_user_model()

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Phone Number",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter phone number"}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter password"}),
    )

    class Meta:
        model = User
        fields = ["username", "password"]

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get("username")

        # Ensure phone number exists
        if phone_number and not User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("Phone number not found.")

        return cleaned_data

from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['customer_name', 'review_rating', 'review_content', 'review_date']
        widgets = {
            'review_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            print("self.instance.review_dateself.instance.review_date", self.instance.review_date)
            self.fields['review_date'].initial = self.instance.review_date


from django import forms
from .models import Banner

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = [
            'name', 'series', 'image',
            'tagline', 'title_main', 'title_highlight',
            'subtitle', 'button_text'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'series': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'tagline': forms.TextInput(attrs={'class': 'form-control'}),
            'title_main': forms.TextInput(attrs={'class': 'form-control'}),
            'title_highlight': forms.TextInput(attrs={'class': 'form-control'}),
            'subtitle': forms.TextInput(attrs={'class': 'form-control'}),
            'button_text': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(BannerForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'autofocus': True
        })
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise ValidationError("No user exists with this email address.")
        return email

class PasswordResetOTPForm(forms.Form):
    otp = forms.CharField(
        label="OTP",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 6-digit OTP'
        })
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        })
    )
    new_password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        
        return cleaned_data
    

from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.core.validators import FileExtensionValidator
User = get_user_model()

class ProfileUpdateForm(UserChangeForm):
    password = None  # Remove the password field
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )

    class Meta:
        model = User
        fields = [
            'first_name', 
            'last_name',
            'email',
            'phone_number',
            'staff_role',
            'address',
            'city',
            'state',
            'pincode',
            'date_of_birth',
            'gender',
            'profile_image'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }




from django import forms
from .models import SocialMedia
from django.contrib.auth import get_user_model

User = get_user_model()

class SocialMediaForm(forms.ModelForm):
    class Meta:
        model = SocialMedia
        fields = ['user', 'platform', 'url', 'is_active']
        widgets = {
            'url': forms.TextInput()  # Basic text input with no validation
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Set up the user field
        if self.request and not self.request.user.is_superuser:
            self.fields['user'].disabled = True
            self.fields['user'].initial = self.request.user
            self.fields['user'].widget = forms.HiddenInput()
        else:
            self.fields['user'].queryset = User.objects.all().order_by('username')
        
        # Remove all validators and patterns
        self.fields['url'].validators = []
        
        # Initialize based on existing value
        if self.instance and self.instance.platform == 'PHONE':
            self.fields['url'].label = "Phone Number"
            self.fields['url'].widget.attrs.update({
                'placeholder': 'Enter phone or any text'
            })
        else:
            self.fields['url'].label = "Profile URL"
            self.fields['url'].widget.attrs.update({
                'placeholder': 'Enter URL or any text'
            })

    def clean(self):
        # No validation performed at all
        return super().clean()
    
from django import forms
from django.contrib.auth import get_user_model
from .models import Customer
from django.utils.crypto import get_random_string

CustomUser = get_user_model()

class CustomerRegistrationForm(forms.ModelForm):
    username = forms.CharField(label="Username", required=True)
    phone = forms.CharField(max_length=20, required=False)
    shipping_address = forms.CharField(widget=forms.Textarea, required=False)
    billing_address = forms.CharField(widget=forms.Textarea, required=False)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    loyalty_points = forms.IntegerField(required=False, min_value=0)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    state = forms.CharField(max_length=100, required=False)
    country = forms.CharField(max_length=100, required=False)
    pincode = forms.CharField(max_length=10, required=False)

    class Meta:
        model = Customer
        fields = ['username', 'phone', 'shipping_address', 'billing_address', 'date_of_birth', 'loyalty_points', 'first_name', 'last_name', 'state', 'country', 'pincode']

    def clean_username(self):
        username = self.cleaned_data['username']
        if not CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("User with this username does not exist.")
        return username

    def save(self, commit=True):
        customer = super().save(commit=False)
        username = self.cleaned_data['username']
        user = CustomUser.objects.get(username=username)
        customer.user = user
        if not customer.customer_username:
            customer.customer_username = self.generate_unique_customer_username()
        if commit:
            customer.save()
        return customer

    def generate_unique_customer_username(self):
        base_username = "CUST"
        while True:
            random_string = get_random_string(length=5, allowed_chars='0123456789')
            customer_username = f"{base_username}{random_string}"
            if not Customer.objects.filter(customer_username=customer_username).exists():
                return customer_username
            


class MemberRegistrationForm(CustomUserForm):
    class Meta(CustomUserForm.Meta):
        base_fields = CustomUserForm.Meta.fields + ['package']
        fields = [f for f in base_fields if f not in ['is_active', 'is_staff', 'on_subscription']]

        widgets = CustomUserForm.Meta.widgets.copy()
        widgets['package'] = forms.Select(attrs={'class': 'form-control'})
        widgets['staff_role'] = forms.HiddenInput()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['staff_role'].initial = 'Member'
        self.fields['staff_role'].required = False
        self.fields['staff_role'].label = ""  # <<< hides the label text
        self.fields['package'].required = True
