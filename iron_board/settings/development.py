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

ENABLE_QR_SCHEDULER = False  # Set to False to disable


USERNAME_PREFIX = "MEMBER-DEV"
SUBSCRIPTION_ORDER_PREFIX = "SUB-ORD-DEV"
