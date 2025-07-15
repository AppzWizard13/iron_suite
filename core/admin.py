from django.contrib import admin
from .models import BusinessDetails

@admin.register(BusinessDetails)
class BusinessDetailsAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'info_email', 'sales_mobile')
    fieldsets = (
        ('Company Identity', {
            'fields': (
                'company_name', 'company_tagline',
                'company_logo', 'company_favicon', 'company_logo_svg'
            )
        }),
        ('Location Information', {
            'fields': ('offline_address', 'map_location')
        }),
        ('Contact Information', {
            'fields': (
                ('info_mobile', 'info_email'),
                ('complaint_mobile', 'complaint_email'),
                ('sales_mobile', 'sales_email')
            )
        }),
        ('Social Media & CEO', {
            'fields': ('company_facebook', 'company_instagram', 'company_email_ceo')
        }),
    )