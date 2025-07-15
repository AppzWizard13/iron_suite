import logging
from django.conf import settings
from django.db.models import Max
from .models import CustomUser

logger = logging.getLogger(__name__)

def generate_username():
    try:
        max_id = CustomUser.objects.aggregate(Max('employee_id'))['employee_id__max'] or 0
        next_id = max_id + 1
        username_prefix = getattr(settings, 'USERNAME_PREFIX', 'EMP')  # Fallback to 'EMP'
        return f"{username_prefix}{next_id:05d}"  # Format: EMP00001, EMP00002
    except Exception as e:
        logger.exception("Error generating username")
        return "EMP00001"  # Default fallback