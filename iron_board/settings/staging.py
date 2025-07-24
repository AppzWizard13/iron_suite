from .base import *

DEBUG = True

# Specify your production host(s)
ALLOWED_HOSTS = ['*']


# Make sure to override SECRET_KEY in environment or .env for security
ENABLE_QR_SCHEDULER = False  # Set to False to disable
# Example: Force HTTPS
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# Add other production-specific security settings as needed.

# Optionally, configure production database here
# DATABASES['default'] = {
#     'ENGINE': 'django.db.backends.postgresql',
#     'NAME': os.getenv('DB_NAME'),
#     'USER': os.getenv('DB_USER'),
#     'PASSWORD': os.getenv('DB_PASSWORD'),
#     'HOST': os.getenv('DB_HOST'),
#     'PORT': os.getenv('DB_PORT'),
# }

USERNAME_PREFIX = "MEMBER-STAG"
SUBSCRIPTION_ORDER_PREFIX = "SUB-ORD-STAG"