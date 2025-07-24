from django.apps import apps
from django.contrib import admin

app_config = apps.get_app_config('attendance')

for model in app_config.get_models():
    if model not in admin.site._registry:
        admin.site.register(model)
