from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import MinValueValidator

from accounts.models import Vendor
from core.choices import DiscountTypeChoice



class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='subcategories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'SubCategories'
        ordering = ['name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"



class Product(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('piece', 'Piece'),
        ('dozen', 'Dozen'),
    ]
    
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    
    # Stock
    stock = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='kg')
    min_order_quantity = models.DecimalField(max_digits=6, decimal_places=2, default=1)
    
    # Fish specific
    is_fresh = models.BooleanField(default=True)
    is_cleaned = models.BooleanField(default=False)
    preparation_time = models.PositiveIntegerField(help_text='Preparation time in minutes', default=30)
    
    # Images
    image = models.ImageField(upload_to='products/')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Metrics
    views = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vendor', 'is_active']),
            models.Index(fields=['category', 'subcategory']),
        ]

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.price


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - Image"


class Discount(models.Model):
    
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DiscountTypeChoice.choices)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Conditions
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    usage_limit = models.PositiveIntegerField(null=True, blank=True, help_text='Total usage limit')
    usage_limit_per_user = models.PositiveIntegerField(default=1, help_text='Per user usage limit')
    
    # Validity
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    
    # Applicable to
    applicable_vendors = models.ManyToManyField(Vendor, blank=True, related_name='discounts')
    applicable_categories = models.ManyToManyField(Category, blank=True, related_name='discounts')
    
    is_active = models.BooleanField(default=True)
    used_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.discount_value}{' %' if self.discount_type == 'percentage' else ' ₹'}"


class DeliveryZone(models.Model):
    name = models.CharField(max_length=100)
    cities = models.TextField(help_text='Comma-separated list of cities')
    pincodes = models.TextField(help_text='Comma-separated list of pincodes')
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    min_order_value_for_free_delivery = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name