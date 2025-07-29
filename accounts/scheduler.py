import logging
import atexit
from datetime import timedelta, time

from django.conf import settings
from django.contrib.auth import get_user_model

from accounts.utils import generate_invoice_pdf
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

import pytz
import requests
from django.utils import timezone
from attendance.models import Schedule, QRToken
from notifications.models import NotificationConfig, NotificationLog
from notifications.utils import send_whatsapp_message
from orders.models import SubscriptionOrder
from django.utils import timezone

# Configure global logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
User = get_user_model()


import logging
from accounts.utils import generate_invoice_pdf

logger = logging.getLogger(__name__)

def generate_missing_invoices_job():
    orders = SubscriptionOrder.objects.filter(
        payment_status=SubscriptionOrder.PaymentStatus.COMPLETED,
        invoice_number__isnull=True
    )
    print(f"🔍 Found {orders.count()} orders needing invoices.")

    for order in orders:
        print(f"➡️ Processing order: {order.order_number}")

        try:
            invoice_number, pdf_path = generate_invoice_pdf(order)
            print(f"📄 Generated invoice_number={invoice_number}, pdf_path={pdf_path}")

            if not invoice_number:
                logger.warning(f"⚠️ Invoice PDF generation failed for order {order.order_number}")
                continue

            order.invoice_number = invoice_number
            order.save()
            print(f"✅ Invoice saved for order: {order.order_number}")
            logger.info(f"Invoice generated and saved for order {order.order_number}")

        except Exception as e:
            print(f"❌ Error generating invoice for {order.order_number}: {str(e)}")
            logger.exception(f"Failed to generate invoice for {order.order_number}: {str(e)}")





def send_whatsapp_expiry_alerts_job():
    config = NotificationConfig.objects.first()
    if not config:
        return  # or log error

    expiry_date = timezone.localdate() + timezone.timedelta(days=config.days_before_expiry)
    members = User.objects.filter(
        staff_role='Member',
        is_active=True,
        on_subscription=True,
        package_expiry_date=expiry_date
    )

    for member in members:
        msg_body = config.message_template.format(
            name=member.first_name,
            expiry=member.package_expiry_date
        )
        success, error = send_whatsapp_message(member.phone_number, msg_body)
        NotificationLog.objects.create(
            user=member,
            phone_number=member.phone_number,
            success=success,
            error_message=error,
            message_body=msg_body
        )


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

def expire_user_subscriptions():
    """
    Find all users whose subscription has expired as of today and set their
    `on_subscription` field to False.

    This ensures that users with expired `package_expiry_date` are no longer
    marked as active subscribers.
    """
    today = timezone.now().date()
    expired_users = User.objects.filter(
        on_subscription=True,
        package_expiry_date__lt=today
    )
    count = expired_users.update(on_subscription=False)
    logger.info(f"Expired {count} user subscriptions by setting on_subscription to False.")


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
    # scheduler.add_job(generate_qr_for_live_sessions, IntervalTrigger(minutes=5))
    # scheduler.add_job(remove_unscanned_qr_before_end, IntervalTrigger(minutes=5))
    # scheduler.add_job(remove_unwanted_qr_tokens, IntervalTrigger(minutes=5))
    # scheduler.add_job(expire_user_subscriptions, IntervalTrigger(hours=1))
    scheduler.add_job(generate_missing_invoices_job, IntervalTrigger(seconds=20))
    # WhatsApp reminders at 7:00 AM and 3:00 PM IST (UTC+5:30)
    scheduler.add_job(
        send_whatsapp_expiry_alerts_job,
        CronTrigger(hour=7, minute=0, timezone='Asia/Kolkata'),
        name='Morning WhatsApp Reminders'
    )
    scheduler.add_job(
        send_whatsapp_expiry_alerts_job,
        CronTrigger(hour=15, minute=0, timezone='Asia/Kolkata'),
        name='Evening WhatsApp Reminders'
    )

    # scheduler.add_job(
    #     generate_missing_invoices_job,
    #     CronTrigger(hour=0, minute=1, timezone='Asia/Kolkata'),
    #     name='Generate PDF Invoices',
    #     replace_existing=True
    # )
    scheduler.start()
    logger.info("Scheduler started.")
    atexit.register(lambda: scheduler.shutdown())