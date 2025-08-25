from twilio.rest import Client
from django.conf import settings

def send_whatsapp_message(to_number, message_body):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    from_whatsapp_number = settings.TWILIO_WHATSAPP_FROM

    client = Client(account_sid, auth_token)
    # Prepend +91 if missing country code
    if not to_number.startswith('+'):
        to_number = '+91' + to_number

    try:
        client.messages.create(
            from_=from_whatsapp_number,
            body=message_body,
            to=f'whatsapp:{to_number}'
        )
        return True, ''
    except Exception as e:
        return False, str(e)
