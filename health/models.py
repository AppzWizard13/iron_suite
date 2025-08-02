from django.db import models
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
