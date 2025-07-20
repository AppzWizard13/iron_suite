import logging
import atexit
from datetime import timedelta, time

from django.conf import settings

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import pytz
import requests
from django.utils import timezone
from attendance.models import Schedule, QRToken

# Configure global logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def self_ping():
    """
    Send GET requests to multiple URLs to keep servers awake.
    """
    ping_urls = [
        'https://xxsapequipments.onrender.com/',
        'https://aspinxp.onrender.com/',
        'https://akshaywedsnisha.onrender.com'
    ]
    for url in ping_urls:
        try:
            response = requests.get(url)
            logger.info(f"Pinging URL: {url}")
            if response.status_code == 200:
                logger.info(f"Self-ping successful! URL: {url}")
            else:
                logger.warning(f"Self-ping failed for {url} with status code {response.status_code}")
        except Exception as e:
            logger.error(f"Error during self-ping to {url}: {e}")


def generate_qr_for_live_sessions():
    """
    Generate a QR token for each live session that has not already generated a
    valid, unused QR within the session interval.
    """
    ist = pytz.timezone('Asia/Kolkata')
    now = timezone.now().astimezone(ist)
    current_time = now.time()
    current_time_str = current_time.strftime('%H:%M')
    live_schedules = Schedule.objects.filter(status='live')

    active_schedules = []

    for schedule in live_schedules:
        start_time = (
            schedule.start_time
            if isinstance(schedule.start_time, time)
            else time.fromisoformat(str(schedule.start_time))
        )
        end_time = (
            schedule.end_time
            if isinstance(schedule.end_time, time)
            else time.fromisoformat(str(schedule.end_time))
        )

        logger.info(
            f"Schedule: {getattr(schedule, 'name', str(schedule))}\n"
            f"  start_time: {start_time}, end_time: {end_time}, "
            f"current_time: {current_time_str}"
        )
        if start_time <= current_time <= end_time:
            active_schedules.append(schedule)

    logger.info(
        "Active schedules: %s", [getattr(s, 'name', str(s)) for s in active_schedules]
    )

    for schedule in active_schedules:
        existing_qr = QRToken.objects.filter(
            schedule=schedule,
            expires_at__gt=now,
            used=False
        ).exists()

        if not existing_qr:
            QRToken.objects.create(
                schedule=schedule,
                expires_at=now + timedelta(hours=4)
            )
            logger.info(f"✅ QR generated for: {getattr(schedule, 'name', str(schedule))}")


def remove_unscanned_qr_before_end():
    """
    Delete unused QR tokens for schedules ending within the next 5 minutes.
    Runs every 30 seconds to clean up soon-to-expire QR tokens proactively.
    """
    ist = pytz.timezone('Asia/Kolkata')
    now = timezone.now().astimezone(ist)
    five_minutes_ahead = (now + timedelta(minutes=5)).time()
    current_time = now.time()

    live_schedules = Schedule.objects.filter(status='live')

    for schedule in live_schedules:
        end_time = (
            schedule.end_time
            if isinstance(schedule.end_time, time)
            else time.fromisoformat(str(schedule.end_time))
        )

        # If the schedule ends in or within the next 5 minutes
        if current_time <= end_time <= five_minutes_ahead:
            deleted, _ = QRToken.objects.filter(
                schedule=schedule,
                used=False
            ).delete()
            logger.info(
                f"🗑️ Removed {deleted} unscanned QR tokens for: {getattr(schedule, 'name', str(schedule))}"
            )

def remove_unwanted_qr_tokens():
    """
    Remove QR tokens that are expired and unused from the database to maintain cleanliness.
    """
    ist = pytz.timezone('Asia/Kolkata')
    now = timezone.now().astimezone(ist)

    # Delete expired and unused QR tokens
    deleted, _ = QRToken.objects.filter(
        expires_at__lt=now,
        used=False
    ).delete()

    logger.info(
        f"🗑️ Removed {deleted} unwanted QR tokens (expired and unused) from the database."
    )


def start():
    if not getattr(settings, 'ENABLE_QR_SCHEDULER', True):
        logger.info("QR Scheduler is disabled by settings.")
        return

    scheduler = BackgroundScheduler()
    # scheduler.add_job(self_ping, IntervalTrigger(seconds=15))
    scheduler.add_job(generate_qr_for_live_sessions, IntervalTrigger(seconds=5))
    scheduler.add_job(remove_unscanned_qr_before_end, IntervalTrigger(seconds=30))
    scheduler.add_job(remove_unwanted_qr_tokens, IntervalTrigger(minutes=5))
    scheduler.start()
    logger.info("Scheduler started.")
    atexit.register(lambda: scheduler.shutdown())