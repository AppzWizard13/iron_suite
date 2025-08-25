# orders/urls.py
from django.urls import path
from . import views
from .views import cashfree_webhook,  cashfree_return, choose_package

urlpatterns = [
    path('payment/cashfree/webhook/', cashfree_webhook, name='cashfree_webhook'),
    path('payment/cashfree/return/', cashfree_return, name='cashfree_return'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('buy/<str:member_id>/', views.choose_package, name='choose_package'),
    path('members/payment/', views.initiate_subscription_payment, name='initiate_subscription_payment'),
    path('members/payment/init/', views.buy_subscription_package, name='buy_subscription_package'),
   

]