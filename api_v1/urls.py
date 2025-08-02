from django.urls import path
from .views import SendOTPAPIView, VerifyOTPAPIView, LoginAPIView

urlpatterns = [
    path('api/send-otp/', SendOTPAPIView.as_view(), name='send_otp_api'),
    path('api/verify-otp/', VerifyOTPAPIView.as_view(), name='verify_otp_api'),
    path('api-v1/login/', LoginAPIView.as_view(), name='api_login'),
]
