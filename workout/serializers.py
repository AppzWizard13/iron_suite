# workout/serializers.py
from rest_framework import serializers
from .models import UserWorkoutAssignment, DayTemplate, ActivityTemplate, Exercise, Equipment, WeeklyTemplate

class ExerciseSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'muscle_groups', 'instructions', 'equipment_name']

class ActivityTemplateSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    
    class Meta:
        model = ActivityTemplate
        fields = [
            'id', 'exercise', 'order', 'sets', 'reps', 'weight_percentage',
            'rest_time', 'estimated_duration', 'form_cues', 'rpe_target'
        ]

class DayTemplateSerializer(serializers.ModelSerializer):
    activities = ActivityTemplateSerializer(many=True, read_only=True)
    day_display = serializers.CharField(source='get_day_display', read_only=True)
    
    class Meta:
        model = DayTemplate
        fields = [
            'id', 'day', 'day_display', 'name', 'is_rest_day', 
            'estimated_duration', 'warm_up_instructions', 
            'cool_down_instructions', 'notes', 'activities'
        ]

class WeeklyTemplateSerializer(serializers.ModelSerializer):
    fitness_level_display = serializers.CharField(source='fitness_level.get_name_display', read_only=True)
    goal_display = serializers.CharField(source='goal.get_name_display', read_only=True)
    trainer_name = serializers.CharField(source='trainer.get_full_name', read_only=True)
    
    class Meta:
        model = WeeklyTemplate
        fields = [
            'id', 'name', 'description', 'fitness_level_display', 
            'goal_display', 'trainer_name', 'total_sessions_per_week',
            'estimated_duration_per_session'
        ]

class UserWorkoutAssignmentSerializer(serializers.ModelSerializer):
    weekly_template = WeeklyTemplateSerializer(read_only=True)
    
    class Meta:
        model = UserWorkoutAssignment
        fields = [
            'id', 'weekly_template', 'start_date', 'end_date', 
            'status', 'custom_notes', 'assigned_date'
        ]
