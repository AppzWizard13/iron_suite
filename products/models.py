from django.db import models
from django.utils.timezone import now  # Fix the NameError issue

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)

    def __str__(self):
        return self.name


class subcategory(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    description = models.TextField()

    def __str__(self):
        return self.name


import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Product(models.Model):
    # EXISTING FIELDS (preserved exactly)
    product_uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    images = models.ImageField(upload_to='product_images/')
    image_1 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image_2 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image_3 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image_4 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    catalogues = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    subcategory = models.ForeignKey(subcategory, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    specifications = models.TextField()
    description = models.TextField()
    additional_information = models.TextField()

    # NEW INDUSTRIAL FIELDS (additions)
    # Identification
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    mpn = models.CharField(max_length=50, blank=True, null=True)  # Manufacturer Part Number
    
    # Manufacturing
    manufacturer = models.CharField(max_length=100, blank=True)
    country_of_origin = models.CharField(max_length=50, blank=True)
    material_composition = models.TextField(blank=True)
    warranty = models.CharField(max_length=100, blank=True)
    
    # Inventory
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    low_stock_threshold = models.IntegerField(default=5)
    weight_kg = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    dimensions = models.CharField(max_length=50, blank=True)  # "LxWxH in cm"
    
    # Shipping
    is_free_shipping = models.BooleanField(default=False)
    handling_time_days = models.PositiveSmallIntegerField(default=1)
    
    # Technical (customize for your industry)
    voltage = models.CharField(max_length=20, blank=True)
    power_rating = models.CharField(max_length=20, blank=True)
    ip_rating = models.CharField(max_length=10, blank=True)  # IP67 etc.
    
    # Metadata
    slug = models.SlugField(max_length=255, blank=True)
    meta_title = models.CharField(max_length=100, blank=True)
    meta_description = models.TextField(blank=True)
    
    # Dates
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(default=now)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['name']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.name} (SKU: {self.sku})" if self.sku else self.name

    def save(self, *args, **kwargs):
        if not self.sku:  # Auto-generate SKU if not provided
            self.sku = f"{self.category.name[:3]}-{uuid.uuid4().hex[:6]}".upper()
        super().save(*args, **kwargs)

from django.db import models

class Package(models.Model):
    PACKAGE_TYPE_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('custom', 'Custom'),
    ]

    DISCOUNT_TYPE_CHOICES = [
        ('none', 'None'),
        ('flat', 'Flat Amount'),
        ('percent', 'Percentage'),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    type = models.CharField(
        max_length=20,
        choices=PACKAGE_TYPE_CHOICES,
        default='monthly'
    )
    duration_days = models.PositiveIntegerField(
        help_text="Total duration of the package in days"
    )

    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Original price of the package"
    )

    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        default='none'
    )

    discount_value = models.DecimalField(
        max_digits=8, decimal_places=2,
        default=0.0,
        help_text="Value of the discount (flat or %)"
    )

    features = models.JSONField(
        default=dict,
        blank=True,
        help_text="A dictionary of custom features like { 'personal_trainer': true, 'diet_plan': false }"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def final_price(self):
        if self.discount_type == 'flat':
            return max(self.price - self.discount_value, 0)
        elif self.discount_type == 'percent':
            return max(self.price * (1 - (self.discount_value / 100)), 0)
        return self.price

    def __str__(self):
        return f"{self.name} ({self.type}) - ₹{self.final_price:.2f}"
