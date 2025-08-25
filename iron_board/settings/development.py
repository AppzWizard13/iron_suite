from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Database override if needed
# DATABASES['default'].update({
#     'ENGINE': 'django.db.backends.sqlite3',
#     'NAME': BASE_DIR / 'db.sqlite3',
# })

# Example: Use console backend for emails in dev
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ENABLE_QR_SCHEDULER = False   # Set to False to disable


USERNAME_PREFIX = "MEMBER-DEV-TEST"
SUBSCRIPTION_ORDER_PREFIX = "SUB-ORD-DEV-TEST"

# Alert testing code 
# from django.contrib.auth import get_user_model
# from api_v1.models import Alert

# User = get_user_model()

# # Get the first user (or create one if none exists)
# user = User.objects.get(username='MEMBER00010')
# if user:
#     print(f"Using user with member_id: {user.member_id}")
    
#     # Create an alert
#     alert = Alert.objects.create(
#         user=user,
#         alert_type='general',
#         message='Test alert to check signals'
#     )
    
#     print(f"Alert created with ID: {alert.id}")
# else:
#     print("No users found. Create a user first.")
