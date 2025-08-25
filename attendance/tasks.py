# from apscheduler.schedulers.background import BackgroundScheduler
# from datetime import timedelta
# from django.utils import timezone

# def generate_qr_for_live_sessions():
#     from .models import Schedule, QRToken  # <-- moved here to avoid early import

#     now = timezone.now()
#     live_schedules = Schedule.objects.filter(
#         start_time__lte=now,
#         end_time__gte=now
#     )

#     for schedule in live_schedules:
#         existing_qr = QRToken.objects.filter(
#             schedule=schedule,
#             expires_at__gt=now,
#             used=False
#         ).exists()

#         if not existing_qr:
#             QRToken.objects.create(
#                 schedule=schedule,
#                 expires_at=now + timedelta(hours=4)
#             )
#             print(f"QR generated for: {schedule.name}")
