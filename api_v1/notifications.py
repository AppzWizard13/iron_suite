import requests
import json
from django.conf import settings
from .models import UserFCMToken
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import logging

logger = logging.getLogger(__name__)

# Updated path for Firebase service account JSON
FIREBASE_SERVICE_ACCOUNT_PATH = settings.FIREBASE_SERVICE_ACCOUNT_PATH

def get_access_token():
    """Get OAuth2 access token for Firebase Cloud Messaging v1 API"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            FIREBASE_SERVICE_ACCOUNT_PATH,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        request = Request()
        credentials.refresh(request)
        return credentials.token
    except Exception as e:
        logger.error(f"Failed to get access token: {str(e)}")
        return None

def send_push_notification(user, title, message, data=None):
    """Send push notification using Firebase Cloud Messaging v1 API"""
    try:
        user_id = user.pk
        user_token = UserFCMToken.objects.get(user=user)
        fcm_token = user_token.fcm_token
        
        if not fcm_token:
            logger.warning(f"No FCM token found for user {user_id}")
            return None
        
        # Get OAuth2 access token
        access_token = get_access_token()
        if not access_token:
            logger.error("Failed to obtain access token")
            return None
        
        # FCM v1 endpoint
        url = 'https://fcm.googleapis.com/v1/projects/iron-board-d8887/messages:send'
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        
        payload = {
            'message': {
                'token': fcm_token,
                'notification': {
                    'title': title,
                    'body': message
                },
                'android': {
                    'notification': {
                        'sound': 'default'
                    }
                }
            }
        }
        
        if data:
            payload['message']['data'] = data
        
        print(f"Sending FCM v1 notification to {fcm_token[:20]}...")
        
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            result = response.json()
            print(f"FCM v1 Response: {result}")
            logger.info(f"Push notification sent to user {user_id}: {result}")
            return result
        else:
            logger.error(f"Failed to send notification. Status: {response.status_code}, Response: {response.text}")
            return None
            
    except UserFCMToken.DoesNotExist:
        logger.warning(f"No FCM token registered for user {user_id}")
        return None
    except Exception as e:
        logger.error(f"Error sending push notification to user {user_id}: {str(e)}")
        return None
