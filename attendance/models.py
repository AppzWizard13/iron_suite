from django.db import models
from django.conf import settings
from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import timedelta, date
import datetime
from django.utils.timezone import now
from accounts.models import Vendor
from core.choices import SessionStatusChoice, AttendanceStatusChoice
from django_multitenant.mixins import TenantModelMixin


# ✅ Avoid lambda: use a named function for token generation
def generate_token():
    return get_random_string(64)


def default_expiry():
    return timezone.now() + timedelta(hours=4)


class Schedule(models.Model,TenantModelMixin):

    name = models.CharField(max_length=100)  # e.g., "Zumba", "HIIT"
    Vendor = models.ForeignKey(  # 👈 This is the tenant reference
            Vendor,
            on_delete=models.CASCADE,
            related_name='schedules'
        )
    tenant_id = 'vendor_id' 
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trainer_schedules'
    )
    schedule_date = models.DateField(default=now) # ✅ Added field to separate date
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.PositiveIntegerField(default=30)
    status = models.CharField(max_length=10, choices=SessionStatusChoice.choices, default='upcoming')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} • {self.schedule_date.strftime('%d %b')} • {self.start_time.strftime('%I:%M %p')}"

    def spots_left(self):
        return max(self.capacity - self.enrollments.count(), 0)

    def update_status(self):
        now = timezone.localtime()
        schedule_datetime = self.schedule_date

        start_dt = timezone.make_aware(datetime.datetime.combine(schedule_datetime, self.start_time))
        end_dt = timezone.make_aware(datetime.datetime.combine(schedule_datetime, self.end_time))

        if now < start_dt:
            self.status = 'upcoming'
        elif start_dt <= now <= end_dt:
            self.status = 'live'
        else:
            self.status = 'ended'

        self.save(update_fields=['status'])

class QRToken(models.Model, TenantModelMixin):
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name='qr_tokens'
    )
    Vendor = models.ForeignKey(  # 👈 Required for TenantModelMixin to resolve tenant directly
        Vendor,
        on_delete=models.CASCADE,
        related_name='qr_tokens'
    )
    tenant_id = 'vendor_id'  # 👈 This must point to a real field on this model

    token = models.CharField(max_length=64, unique=True, default=generate_token)
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expiry)
    used = models.BooleanField(default=False)

    def is_valid(self):
        now = timezone.now()
        return (self.generated_at <= now <= self.expires_at) and not self.used and self.schedule.status == 'live'

    def mark_used(self):
        if not self.used:
            self.used = True
            self.save(update_fields=['used'])

    def save(self, *args, **kwargs):
        # Ensure `Vendor` is synced from `schedule`
        if self.schedule and not self.Vendor:
            self.Vendor = self.schedule.Vendor
        super().save(*args, **kwargs)

    def __str__(self):
        return f"QR {self.token[:8]}… for {self.schedule.name}"


class Attendance(models.Model, TenantModelMixin):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.SET_NULL,
        null=True,
        related_name='attendances'
    )
    Vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    tenant_id = 'vendor_id'  # 👈 Required for multitenancy

    date = models.DateField(default=date.today)
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=AttendanceStatusChoice.choices, default=AttendanceStatusChoice.CHECKED_IN)
    duration = models.DurationField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'schedule', 'date')

    def __str__(self):
        return f"{self.user.username} – {self.schedule.name} – {self.date}"

    def mark_checkout(self):
        if not self.check_out_time:
            self.check_out_time = timezone.now()
            self.status = 'checked_out'
            self.duration = self.check_out_time - self.check_in_time
            self.save(update_fields=['check_out_time', 'status', 'duration'])

    def save(self, *args, **kwargs):
        if self.schedule and not self.Vendor:
            self.Vendor = self.schedule.Vendor
        super().save(*args, **kwargs)

class CheckInLog(models.Model, TenantModelMixin):
    user = models.user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.ForeignKey(QRToken, on_delete=models.CASCADE)
    attendance = models.ForeignKey(Attendance, on_delete=models.SET_NULL, null=True, blank=True)
    Vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='checkin_logs')
    tenant_id = 'vendor_id'

    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    gps_lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    gps_lng = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    scanned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} @ {self.scanned_at.strftime('%I:%M %p')}"

    def save(self, *args, **kwargs):
        if self.token and not self.Vendor:
            self.Vendor = self.token.Vendor
        super().save(*args, **kwargs)


class ClassEnrollment(models.Model, TenantModelMixin):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    Vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='class_enrollments'
    )
    tenant_id = 'vendor_id'

    enrolled_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'schedule')

    def __str__(self):
        return f"{self.user.username} → {self.schedule.name}"



