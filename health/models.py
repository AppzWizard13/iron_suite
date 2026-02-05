from django.db import models
from django.conf import settings
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django_multitenant.models import TenantModelMixin
from datetime import date


# Get User model
from django.contrib.auth import get_user_model
User = get_user_model()

class WorkoutCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Equipment(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class WorkoutLevel(models.TextChoices):
    BEGINNER = 'Beginner'
    INTERMEDIATE = 'Intermediate'
    ADVANCED = 'Advanced'

class WorkoutProgram(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(WorkoutCategory, on_delete=models.CASCADE)
    equipment = models.ManyToManyField(Equipment, blank=True)
    type = models.CharField(max_length=50, choices=[('Compound', 'Compound'), ('Isolation', 'Isolation'), ('Cardio', 'Cardio'), ('Bodyweight', 'Bodyweight'), ('Isometric', 'Isometric')])
    level = models.CharField(max_length=20, choices=WorkoutLevel.choices)
    sets = models.IntegerField(default=3)
    reps = models.CharField(max_length=20, default="10-12")
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class WorkoutTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class WorkoutTemplateDay(models.Model):
    template = models.ForeignKey(WorkoutTemplate, on_delete=models.CASCADE, related_name='days')
    day_number = models.PositiveIntegerField()  # 1 = Monday, 2 = Tuesday...
    workout = models.ForeignKey(WorkoutProgram, on_delete=models.CASCADE)
    sets = models.IntegerField(default=3)
    reps = models.CharField(max_length=20, default="10-12")
    notes = models.TextField(blank=True, null=True)

class MemberWorkoutAssignment(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    template = models.ForeignKey(WorkoutTemplate, on_delete=models.CASCADE)
    start_date = models.DateField()
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.user.username} - {self.template.name}"

class BodyMeasurement(models.Model):
    """
    Stores weight progress for each Vendor customer.
    Includes BMI and week tracking for historical graph purposes.
    """

    Vendor = models.ForeignKey(
        'accounts.Vendor',
        on_delete=models.CASCADE,
        related_name='measurements'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='measurements'
    )

    date = models.DateField(default=timezone.now, db_index=True)

    week_of_year = models.PositiveSmallIntegerField(editable=False, db_index=True)
    year = models.PositiveSmallIntegerField(editable=False, db_index=True)

    # Week count since user joined the Vendor
    week_index_since_join = models.PositiveIntegerField(editable=False, db_index=True)

    weight_kg = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(20), MaxValueValidator(400)]
    )

    height_cm = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(50), MaxValueValidator(300)]
    )

    bmi = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(10), MaxValueValidator(60)],
        editable=False  # Prevent editing from forms/admin
    )

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['Vendor', 'user', 'date']),
            models.Index(fields=['Vendor', 'user', 'year', 'week_of_year']),
            models.Index(fields=['Vendor', 'user', 'week_index_since_join']),
        ]

    def save(self, *args, **kwargs):
        # Ensure Vendor is set from user if not provided
        if not self.vendor_id and getattr(self.user, 'vendor_id', None):
            self.vendor_id = self.user.vendor_id

        # Set year/week from date
        iso_year, iso_week, _ = self.date.isocalendar()
        self.year = iso_year
        self.week_of_year = iso_week

        # Calculate weeks since join
        if getattr(self.user, "join_date", None):
            days_since_join = (self.date - self.user.join_date).days
            self.week_index_since_join = (days_since_join // 7) + 1
        else:
            self.week_index_since_join = 1

        # Calculate BMI if height and weight present
        if self.height_cm and self.weight_kg:
            height_m = float(self.height_cm) / 100
            self.bmi = round(float(self.weight_kg) / (height_m ** 2), 1)
        else:
            self.bmi = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.date} (Week {self.week_index_since_join}) - {self.weight_kg} kg (BMI: {self.bmi})"
