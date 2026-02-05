# workout/models.py
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from core.choices import ActivityTypeChoice, GoalChoice, LevelChoice, WeekdayChoice, WorkoutStatusChoice
User = get_user_model()

class FitnessLevel(models.Model):
    """Fitness levels: Beginner, Medium, Advanced, Master"""

    name = models.CharField(max_length=20, choices=LevelChoice.choices, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.get_name_display()

class Goal(models.Model):
    """Goals: Weight Loss, Weight Gain, Competition, Basic Maintenance"""

    name = models.CharField(max_length=30, choices=GoalChoice.choices, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.get_name_display()

class Equipment(models.Model):
    """Equipment/Exercise types"""
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, blank=True)  # e.g., 'Cardio', 'Strength', 'Bodyweight'
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Exercise(models.Model):
    """Individual exercises"""
    name = models.CharField(max_length=100)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='exercises')
    muscle_groups = models.CharField(max_length=200)  # e.g., 'Chest, Triceps'
    instructions = models.TextField()
    safety_notes = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.equipment.name})"
    
    class Meta:
        ordering = ['name']

class WeeklyTemplate(models.Model):
    """Weekly workout template created by trainer"""
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weekly_templates')
    name = models.CharField(max_length=200)
    fitness_level = models.ForeignKey(FitnessLevel, on_delete=models.CASCADE)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Template metadata
    total_sessions_per_week = models.IntegerField(default=6)
    estimated_duration_per_session = models.CharField(max_length=20, default="45-60min")
    
    def __str__(self):
        return f"{self.name} - {self.fitness_level} {self.goal}"
    
    class Meta:
        ordering = ['-created_at']

class DayTemplate(models.Model):
    """Daily workout template within a weekly template"""
    
    weekly_template = models.ForeignKey(WeeklyTemplate, on_delete=models.CASCADE, related_name='day_templates')
    day = models.CharField(max_length=10, choices=WeekdayChoice.choices)
    name = models.CharField(max_length=200)  # e.g., "Full-Body Circuit A", "Push Day"
    is_rest_day = models.BooleanField(default=False)
    estimated_duration = models.CharField(max_length=20, default="45-55min")
    warm_up_instructions = models.TextField(default="5-10min mobility + light cardio")
    cool_down_instructions = models.TextField(default="5-10min stretching/breathing")
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.weekly_template.name} - {self.get_day_display()}: {self.name}"
    
    class Meta:
        unique_together = ['weekly_template', 'day']
        ordering = ['weekly_template', 'day']

class ActivityTemplate(models.Model):
    """Individual activity within a day template"""

    
    day_template = models.ForeignKey(DayTemplate, on_delete=models.CASCADE, related_name='activities')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ActivityTypeChoice.choices, default='exercise')
    order = models.PositiveIntegerField()  # Order within the day
    
    # Exercise parameters
    sets = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    reps = models.CharField(max_length=20)  # e.g., "8-10", "AMRAP", "30s"
    weight_percentage = models.CharField(max_length=20, blank=True)  # e.g., "75-80%", "@RPE6"
    rest_time = models.CharField(max_length=20, blank=True)  # e.g., "90s", "2-3min"
    estimated_duration = models.CharField(max_length=20, default="10-12min")
    
    # Instructions and notes
    form_cues = models.TextField(blank=True)  # e.g., "Keep chest up, full depth"
    rpe_target = models.CharField(max_length=20, blank=True)  # e.g., "RPE 6-7"
    progression_notes = models.TextField(blank=True)
    special_instructions = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.exercise.name} - {self.sets}x{self.reps}"
    
    class Meta:
        ordering = ['day_template', 'order']
        unique_together = ['day_template', 'order']

class UserWorkoutAssignment(models.Model):
    """Assignment of weekly template to user"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workout_assignments')
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_workouts')
    weekly_template = models.ForeignKey(WeeklyTemplate, on_delete=models.CASCADE)
    
    assigned_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=WorkoutStatusChoice.choices, default='assigned')
    
    # Customizations for individual user
    custom_notes = models.TextField(blank=True)
    modifications = models.JSONField(default=dict, blank=True)  # Store any modifications
    
    def __str__(self):
        return f"{self.user.username} - {self.weekly_template.name}"
    
    class Meta:
        ordering = ['-assigned_date']

class WorkoutSession(models.Model):
    """Individual workout session completed by user"""
    assignment = models.ForeignKey(UserWorkoutAssignment, on_delete=models.CASCADE, related_name='sessions')
    day_template = models.ForeignKey(DayTemplate, on_delete=models.CASCADE)
    date = models.DateField()
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    is_skipped = models.BooleanField(default=False)
    
    # Session feedback
    overall_rpe = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], null=True, blank=True)
    energy_level = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.assignment.user.username} - {self.day_template.name} ({self.date})"
    
    class Meta:
        ordering = ['-date']
        unique_together = ['assignment', 'day_template', 'date']

class ActivityLog(models.Model):
    """Log of individual activities completed by user"""
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='activity_logs')
    activity_template = models.ForeignKey(ActivityTemplate, on_delete=models.CASCADE)
    
    # Actual performed values
    sets_completed = models.PositiveIntegerField()
    reps_completed = models.CharField(max_length=20)
    weight_used = models.CharField(max_length=50, blank=True)
    actual_rpe = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], null=True, blank=True)
    
    is_completed = models.BooleanField(default=False)
    is_modified = models.BooleanField(default=False)
    modification_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.activity_template.exercise.name} - {self.sets_completed}x{self.reps_completed}"
    
    class Meta:
        ordering = ['session', 'activity_template__order']
