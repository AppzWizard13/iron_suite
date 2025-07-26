# orders/urls.py
from django.urls import path
from . import views


urlpatterns = [
    # path('payment/cashfree/webhook/', cashfree_webhook, name='cashfree_webhook'),
    path('members/expiry-alerts/', views.SendWhatsAppExpiryAlertsView.as_view(), name='send_expiry_alerts'),


]