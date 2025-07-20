from .base import *

DEBUG = False

# Specify your production host(s)
ALLOWED_HOSTS = ['https://iron-suite.onrender.com','*']

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://iron-suite.onrender.com',
]

# Make sure to override SECRET_KEY in environment or .env for security
ENABLE_QR_SCHEDULER = True  # Set to False to disable
# Example: Force HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
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

USERNAME_PREFIX = "MEMBER-PROD"
SUBSCRIPTION_ORDER_PREFIX = "SUB-ORD-PROD"