from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from django.utils.timezone import now

from products.models import Package  # Fix the NameError issue


# users/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from django.core.validators import FileExtensionValidator
from django_multitenant.models import TenantModelMixin       # Import the Gym (tenant) model
from products.models import Package
from django.db import models


class Gym(models.Model):  # 👈 GOOD
    name = models.CharField(max_length=255, unique=True)
    location = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    proprietor_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    
class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("The Phone Number field must be set")
        extra_fields.pop("username", None)
        extra_fields.setdefault("is_active", True)
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(phone_number, password, **extra_fields)

class CustomUser(AbstractUser, TenantModelMixin):
    username = models.CharField(max_length=20, unique=True, blank=True, null=True)  
    phone_number = models.CharField(max_length=15, unique=True)
    member_id = models.BigAutoField(primary_key=True)  
    join_date = models.DateField(auto_now_add=True)
    package_expiry_date = models.DateField(null=True)
    tenant_id = "gym_id"


    STAFF_ROLES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Employee', 'Employee'),
        ('Customer', 'Customer'),
        ('Member', 'Member'),
        ('Trainer', 'Trainer'),
    ]
    staff_role = models.CharField(max_length=100, choices=STAFF_ROLES)

    email = models.EmailField(unique=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)

    profile_image = models.ImageField(
        upload_to='profile_pics/', 
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    package = models.ForeignKey(Package, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    on_subscription = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(Group, related_name="customuser_set", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions_set", blank=True)

    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='users')    # <--- Multi-tenancy here!
    multitenant_shared_fields = ["gym"]                                            # <--- Required by django-multitenant

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = f"MEMBER{str(self.member_id).zfill(5)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"



class Review(models.Model):
    customer_name = models.CharField(max_length=255)
    review_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5 rating
    review_content = models.TextField()
    review_date = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.customer_name} - {self.review_rating} Stars"


class Banner(models.Model):
    name = models.CharField(max_length=255)
    series = models.IntegerField()
    image = models.ImageField(upload_to='banners/')

    # New fields for text content
    tagline = models.CharField(max_length=255, blank=True, help_text="E.g. SHAPE YOUR BODY")
    title_main = models.CharField(max_length=255, help_text="E.g. BE")
    title_highlight = models.CharField(max_length=255, help_text="E.g. STRONG")
    subtitle = models.CharField(max_length=255, help_text="E.g. TRAINING HARD")
    button_text = models.CharField(max_length=100, blank=True, default='Get Info')

    def __str__(self):
        return self.name


from django.db import models
from django.contrib.auth import get_user_model
import random
import string
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            self.otp = ''.join(random.choices(string.digits, k=6))
            self.expires_at = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at
    


from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class SocialMedia(models.Model):
    SOCIAL_MEDIA_CHOICES = [
        ('GMAIL', 'Gmail'),
        ('FACEBOOK', 'Facebook'),
        ('INSTAGRAM', 'Instagram'),
        ('LINKEDIN', 'LinkedIn'),
        ('PHONE', 'Phone'),
        ('TWITTER', 'Twitter'),
        ('YOUTUBE', 'YouTube'),
        ('WHATSAPP', 'WhatsApp'),
        ('HOME_PAGE_WHATSAPP', 'Home Page WhatsApp'),
        ('HOME_PAGE_PHONE', 'Home Page Phone'),
        ('HOME_PAGE_INSTAGRAM', 'Home Page Instagram'),
        ('HOME_PAGE_GMAIL', 'Home Page Gmail'),
        # Add more as needed
    ]
    
    platform = models.CharField(
        max_length=20,
        choices=SOCIAL_MEDIA_CHOICES,
        verbose_name='Social Media Platform'
    )
    url = models.CharField(
        max_length=255,  # Changed from URLField to CharField
        verbose_name='Link or Phone Number'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='social_media',
        verbose_name='User'
    )
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Social Media Link'
        verbose_name_plural = 'Social Media Links'
        ordering = ['platform']

    def __str__(self):
        return f"{self.get_platform_display()} - {self.user.username}"
    

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

CustomUser = get_user_model()

class Customer(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Changed to ForeignKey
    phone = models.CharField(max_length=20, blank=True)
    shipping_address = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    loyalty_points = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    customer_username = models.CharField(max_length=150, unique=True, blank=True)

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def save(self, *args, **kwargs):
        if not self.customer_username:
            self.customer_username = self.generate_unique_username()
        super().save(*args, **kwargs)

    def generate_unique_username(self):
        base_username = "CUST"
        while True:
            random_string = get_random_string(length=5, allowed_chars='0123456789')
            username = f"{base_username}{random_string}"
            if not Customer.objects.filter(customer_username=username).exists():
                return username

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.email})"