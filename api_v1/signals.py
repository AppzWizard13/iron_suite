from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Alert
from .notifications import send_push_notification
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Alert)
def alert_created_handler(sender, instance, created, **kwargs):
    """Send push notification when a new alert is created"""
    print(f"Signal received! Created: {created}, Alert ID: {instance.id}")
    
    if created:
        try:
            user = instance.user
            
            # Debug: Print user model info
            print(f"User model: {type(user)}")
            print(f"User fields: {[f.name for f in user._meta.fields]}")
            print(f"User pk: {user.pk}")
            
            # Always use pk instead of id
            user_id = user.pk
            print(f"Processing alert for user pk: {user_id}")
            logger.info(f"Processing alert for user pk: {user_id}")
            
            # Customize title and message based on alert type
            if instance.alert_type == 'subscription_expired':
                title = "Subscription Expired"
                message = "Your subscription has expired. Please renew to continue using our services."
            else:
                title = "Alert Update"
                message = instance.message or "You have a new alert."
            
            print(f"About to call send_push_notification...")
            result = send_push_notification(user, title, message)
            print(f"Notification result: {result}")
            
            if result:
                logger.info(f"Push notification sent to user {user_id} for alert {instance.id}")
            else:
                logger.warning(f"Failed to send push notification to user {user_id}")
                
        except AttributeError as e:
            print(f"AttributeError in signal: {str(e)}")
            logger.error(f"AttributeError in alert_created_handler: {str(e)}")
            # Print the full traceback to see where the error occurs
            import traceback
            traceback.print_exc()
        except Exception as e:
            print(f"Error in signal: {str(e)}")
            logger.error(f"Error in alert_created_handler: {str(e)}")
            import traceback
            traceback.print_exc()
