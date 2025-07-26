from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import timedelta, date
import datetime
from django.utils.timezone import now


# ✅ Avoid lambda: use a named function for token generation
def generate_token():
    return get_random_string(64)


def default_expiry():
    return timezone.now() + timedelta(hours=4)


class Schedule(models.Model):
    SESSION_STATUS = [
        ('upcoming', 'Upcoming'),
        ('live', 'Live'),
        ('ended', 'Ended'),
    ]

    name = models.CharField(max_length=100)  # e.g., "Zumba", "HIIT"
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
    status = models.CharField(max_length=10, choices=SESSION_STATUS, default='upcoming')
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


class QRToken(models.Model):
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name='qr_tokens'
    )
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

    def __str__(self):
        return f"QR {self.token[:8]}… for {self.schedule.name}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('auto_checked_out', 'Auto Checked Out'),
    ]

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
    date = models.DateField(default=date.today)
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='checked_in')
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


class CheckInLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.ForeignKey(QRToken, on_delete=models.CASCADE)
    attendance = models.ForeignKey(Attendance, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    gps_lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    gps_lng = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    scanned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} @ {self.scanned_at.strftime('%I:%M %p')}"


class ClassEnrollment(models.Model):
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
    enrolled_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'schedule')

    def __str__(self):
        return f"{self.user.username} → {self.schedule.name}"
