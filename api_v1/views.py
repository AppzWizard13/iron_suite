from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import random
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
from django.contrib.auth import login
# Get User model
from django.contrib.auth import (
    login, logout, authenticate, get_user_model
)
User = get_user_model()
CustomUser = User

class SendOTPAPIView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')

        if not phone_number:
            return Response({"detail": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response({"detail": "No user found with this phone number."}, status=status.HTTP_404_NOT_FOUND)

        otp = str(random.randint(100000, 999999))
        valid_until = timezone.now() + timedelta(minutes=5)

        request.session['otp'] = otp
        request.session['otp_valid_until'] = valid_until.isoformat()
        request.session['phone_number'] = phone_number

        configs = Configuration.objects.filter(config__in=["enable-emailotp", "enable-smsotp"])
        config_values = {config.config: config.value for config in configs}
        enable_email = config_values.get("enable-emailotp", "False").lower() in ("true", "1", "yes")
        enable_sms = config_values.get("enable-smsotp", "False").lower() in ("true", "1", "yes")

        if enable_email:
            self.send_otp_via_email(user.email, otp)

        if enable_sms:
            self.send_otp_via_sms(phone_number, otp)

        return Response({"detail": "OTP sent successfully."}, status=status.HTTP_200_OK)

    def send_otp_via_email(self, email, otp):
        subject = f"OTP for {settings.SITE_NAME}"
        body = (
            f"Dear User,\n\n"
            f"Your OTP for logging in to {settings.SITE_NAME} is:\n\n"
            f"OTP: {otp}\n\n"
            f"This OTP is valid for 5 minutes.\n\n"
            f"Best regards,\n{settings.SITE_NAME} Team"
        )
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=True)

    def send_otp_via_sms(self, phone_number, otp):
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=f"Your OTP is: {otp}. Valid for 5 minutes.",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
        except Exception as e:
            print("SMS sending error:", e)


class VerifyOTPAPIView(APIView):
    def post(self, request):
        user_otp = request.data.get('otp')
        phone_number = request.session.get('phone_number')
        stored_otp = request.session.get('otp')
        otp_valid_until = request.session.get('otp_valid_until')

        if not all([user_otp, stored_otp, otp_valid_until]):
            return Response({"detail": "Session expired or OTP not sent."}, status=status.HTTP_400_BAD_REQUEST)

        if timezone.now() > timezone.datetime.fromisoformat(otp_valid_until):
            return Response({"detail": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

        if user_otp != stored_otp:
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        request.session.pop('otp', None)
        request.session.pop('otp_valid_until', None)
        request.session.pop('phone_number', None)

        return Response({
            "detail": "OTP verified. Login successful.",
            "user_id": user.id,
            "email": user.email,
            "phone_number": user.phone_number
        }, status=status.HTTP_200_OK)
