# orders/urls.py
from django.urls import path
from . import views


urlpatterns = [
    # path('payment/cashfree/webhook/', cashfree_webhook, name='cashfree_webhook'),
    # path('payment/cashfree/return/', cashfree_return, name='cashfree_return'),
    # path('payment/failed/', views.payment_failed, name='payment_failed'),
    path('members/upcoming-renewals/', views.UpcomingRenewalMemberListView.as_view(), name='upcoming_renewal_members'),


]