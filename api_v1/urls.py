from django.urls import path
from .views import SendOTPAPIView, VerifyOTPAPIView

urlpatterns = [
    path('api/send-otp/', SendOTPAPIView.as_view(), name='send_otp_api'),
    path('api/verify-otp/', VerifyOTPAPIView.as_view(), name='verify_otp_api'),
]
