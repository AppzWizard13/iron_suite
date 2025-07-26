# views.py
from django.views import View
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from twilio.rest import Client
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()


class SendWhatsAppExpiryAlertsView(View):
    template_name = 'advadmin/send_expiry_alerts.html'  

    def get(self, request):
        # Fetch members whose expiry is in exactly 3 days
        expiry_date = timezone.localdate() + timedelta(days=3)
        members = User.objects.filter(
            staff_role='Member',
            is_active=True,
            on_subscription=True,
            package_expiry_date=expiry_date
        )
        return render(request, self.template_name, {'members': members})

    def post(self, request):
        expiry_date = timezone.localdate() + timedelta(days=3)
        members = User.objects.filter(
            staff_role='Member',
            is_active=True,
            on_subscription=True,
            package_expiry_date=expiry_date
        )

        # Twilio credentials
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        from_whatsapp_number = settings.TWILIO_WHATSAPP_FROM

        client = Client(account_sid, auth_token)
        sent, failed = 0, 0

        for member in members:
            to_number = member.phone_number
            if not to_number.startswith('+'):  
                to_number = '+91' + to_number  

            msg_body = (
                f"Dear {member.first_name}, your subscription expires on {member.package_expiry_date}. "
                "Please renew soon to continue the service."
            )
            try:
                client.messages.create(
                    from_=from_whatsapp_number,
                    body=msg_body,
                    to=f'whatsapp:{to_number}'
                )
                sent += 1
            except Exception as e:
                # Optionally log error e
                failed += 1

        messages.success(request, f"WhatsApp alerts sent to {sent} members. {failed} failures.")
        return redirect('send_expiry_alerts')  # Change to your URL name

