# orders/urls.py
from django.urls import path
from . import views
from .views import cashfree_webhook,  cashfree_return

urlpatterns = [
    path('payment/cashfree/webhook/', cashfree_webhook, name='cashfree_webhook'),
    path('payment/cashfree/return/', cashfree_return, name='cashfree_return'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),


]