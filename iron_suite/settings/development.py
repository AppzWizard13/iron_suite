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
print("ccccccccccccccccccccccccccccccccccccccccccccccccccc", [os.path.join(BASE_DIR, 'templates')])
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
