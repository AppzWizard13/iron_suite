from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
import atexit
import requests  # Make sure to import requests

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# Updated self_ping function to ping multiple URLs
def self_ping():
    """
    Function to send GET requests to self-ping multiple server endpoints.
    """
    ping_urls = [
        'https://xxsapequipments.onrender.com/',
        'https://aspinxp.onrender.com/',
        'https://akshaywedsnisha.onrender.com'
    ]
    
    for url in ping_urls:
        try:
            response = requests.get(url)
            print(f"Pinging URL: {url}")
            if response.status_code == 200:
                logger.info(f"Self-ping successful! URL: {url}")
            else:
                logger.warning(f"Self-ping failed for {url} with status code {response.status_code}")
        except Exception as e:
            logger.error(f"Error during self-ping to {url}: {e}")

from datetime import timedelta, time
from django.utils import timezone
from attendance.models import Schedule, QRToken
import pytz

def generate_qr_for_live_sessions():
    ist = pytz.timezone('Asia/Kolkata')
    now = timezone.now().astimezone(ist)
    current_time = now.time()  # This is a time object for comparison
    current_time_str = current_time.strftime('%H:%M')  # For logging
    # Get all live schedules (assuming 'status' field exists)
    live_schedules = Schedule.objects.filter(status='live')
    
    active_schedules = []
    
    for schedule in live_schedules:
        # Convert start_time and end_time to time objects if they aren't already
        start_time = schedule.start_time if isinstance(schedule.start_time, time) else time.fromisoformat(str(schedule.start_time))
        end_time = schedule.end_time if isinstance(schedule.end_time, time) else time.fromisoformat(str(schedule.end_time))
        
        # Check if current time is within the schedule's time range
        print("start_time", start_time)
        print("end_time", end_time)
        print(f"Current time in IST: {current_time_str}")
        if start_time <= current_time <= end_time:
            active_schedules.append(schedule)
    
    print("Active schedules:", [s.name for s in active_schedules])

    for schedule in active_schedules:
        # Check if an active QR code already exists
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
            print(f"✅ QR generated for: {schedule.name}")


# Function to start the scheduler
def start():
    scheduler = BackgroundScheduler()

    # Add self-ping to the scheduler, for example, every 15 seconds
    # scheduler.add_job(self_ping, IntervalTrigger(seconds=15))  # Self-ping every 15 seconds
    scheduler.add_job(generate_qr_for_live_sessions, IntervalTrigger(seconds=5))  # Self-ping every 15 seconds
    
    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler started.")

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

# Call start() to run the scheduler
if __name__ == "__main__":
    start()






