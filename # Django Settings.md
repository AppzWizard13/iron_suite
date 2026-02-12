# Django Settings
SECRET_KEY=django-insecure-3d226ba27fa2c207f0be94158f1c390fe4d94efa
DEBUG=1
SITE_NAME=IronBoard

# Database Settings (Matches your docker-compose db service)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=myoceanbasket_db
DB_USER=myoceanbasket_admin
DB_PASSWORD=xPL7y6qe1gLHAg2B9SWvW06vXSC8lxSe
DB_HOST=db
DB_PORT=5432

# Cloudinary Settings
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Integrations
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=your_phone
CASHFREE_APP_ID=your_id
CASHFREE_SECRET_KEY=your_key

# Google OAuth (IDs from your settings.py)
GOOGLE_OAUTH_CLIENT_ID=944738807710-absp2l77vio1fckr0o5970ck4ql2ip7q.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your_google_secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/accounts/google/login/callback/


# OR if you have a settings folder:
DJANGO_SETTINGS_MODULE=myoceanbasket.settings.development
