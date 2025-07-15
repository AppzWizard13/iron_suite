from django.db import models

class BusinessDetails(models.Model):
    DAY_CHOICES = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    ]
    
    # Company Information
    company_name = models.CharField(max_length=255)
    company_tagline = models.CharField(max_length=255, blank=True)
    company_logo = models.ImageField(upload_to='company/')
    company_favicon = models.ImageField(upload_to='company/')
    company_logo_svg = models.FileField(upload_to='company/')
    breadcrumb_image = models.FileField(upload_to='company/')
    about_page_image = models.FileField(upload_to='company/')
    
    # Location Information
    offline_address = models.TextField()
    map_location = models.URLField(help_text="Google Maps embed URL")
    
    # Contact Information
    info_mobile = models.CharField(max_length=20)
    info_email = models.EmailField()
    complaint_mobile = models.CharField(max_length=20)
    complaint_email = models.EmailField()
    sales_mobile = models.CharField(max_length=20)
    sales_email = models.EmailField()
    gstn = models.CharField(max_length=20)
    
    # Social Media
    company_instagram = models.URLField(blank=True)
    company_facebook = models.URLField(blank=True)
    company_email_ceo = models.EmailField(blank=True)
    
    # Business Hours (same for all days)
    opening_time = models.TimeField(default='09:00:00')  # Add default
    closing_time = models.TimeField(default='17:00:00')  # Add default
    
    # Days closed (store as comma-separated day codes, e.g. "Sun,Mon")
    closed_days = models.CharField(
        max_length=20,
        blank=True,
        help_text="Comma-separated days (e.g. Sun,Mon)"
    )

    def __str__(self):
        return self.company_name

    def get_business_hours(self):
        hours = []
        closed_days = [d.strip() for d in self.closed_days.split(',')] if self.closed_days else []
        
        for day_code, day_name in self.DAY_CHOICES:
            if day_code in closed_days:
                hours.append(f"{day_name}: Closed")
            else:
                hours.append(
                    f"{day_name}: {self.opening_time.strftime('%I:%M %p')} - "
                    f"{self.closing_time.strftime('%I:%M %p')}"
                )
        return hours

    def is_day_closed(self, day_code):
        if not self.closed_days:
            return False
        return day_code in [d.strip() for d in self.closed_days.split(',')]

    class Meta:
        verbose_name = "Business Detail"
        verbose_name_plural = "Business Details"

class Configuration(models.Model):
    config = models.CharField(max_length=255, unique=True, verbose_name="Configuration Key")
    value = models.CharField(max_length=255, verbose_name="Configuration Value")
    
    class Meta:
        verbose_name = "Configuration"
        verbose_name_plural = "Configurations"
        ordering = ['config']
    
    def __str__(self):
        return f"{self.config}: {self.value}"