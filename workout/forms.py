# workout/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import *

class WeeklyTemplateForm(forms.ModelForm):
    class Meta:
        model = WeeklyTemplate
        fields = ['name', 'fitness_level', 'goal', 'description', 'total_sessions_per_week', 'estimated_duration_per_session']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter template name (e.g., Beginner Weight Loss Program)'
            }),
            'fitness_level': forms.Select(attrs={'class': 'form-select'}),
            'goal': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe the purpose and target audience for this workout template'
            }),
            'total_sessions_per_week': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 7,
                'value': 6
            }),
            'estimated_duration_per_session': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 45-60min, 30-45min',
                'value': '45-55min'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 3:
            raise forms.ValidationError("Template name must be at least 3 characters long.")
        return name

class DayTemplateForm(forms.ModelForm):
    class Meta:
        model = DayTemplate
        fields = ['day', 'name', 'is_rest_day', 'estimated_duration', 'notes']
        widgets = {
            'day': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Upper Body Strength, Full Body Circuit A'
            }),
            'is_rest_day': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'estimated_duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '45-55min',
                'value': '45-55min'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Special instructions, warm-up notes, or modifications'
            }),
        }

class ActivityTemplateForm(forms.ModelForm):
    class Meta:
        model = ActivityTemplate
        fields = [
            'exercise', 'activity_type', 'sets', 'reps', 'weight_percentage', 
            'rest_time', 'estimated_duration', 'form_cues', 'rpe_target', 
            'progression_notes', 'special_instructions'
        ]
        widgets = {
            'exercise': forms.Select(attrs={'class': 'form-select'}),
            'activity_type': forms.Select(attrs={'class': 'form-select'}),
            'sets': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
                'placeholder': '3'
            }),
            'reps': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '8-10, 12, AMRAP, 30s'
            }),
            'weight_percentage': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '75-80%, @RPE7, bodyweight'
            }),
            'rest_time': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '60s, 2-3min, 90s'
            }),
            'estimated_duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '10-12min',
                'value': '10-12min'
            }),
            'form_cues': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'e.g., Keep chest up, full depth, squeeze scapula'
            }),
            'rpe_target': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'RPE 6-7, RPE 8, moderate effort'
            }),
            'progression_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'How to progress this exercise over time'
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any special notes or modifications'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Order exercises by name for better usability
        self.fields['exercise'].queryset = Exercise.objects.select_related('equipment').order_by('name')
        
    def clean_sets(self):
        sets = self.cleaned_data['sets']
        if sets < 1 or sets > 10:
            raise forms.ValidationError("Sets must be between 1 and 10.")
        return sets

class AssignTemplateForm(forms.ModelForm):
    class Meta:
        model = UserWorkoutAssignment
        fields = ['user', 'start_date', 'end_date', 'custom_notes']
        widgets = {
            'user': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Select a user to assign this template to'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'custom_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any specific instructions or modifications for this user'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active users, ordered by name
        self.fields['user'].queryset = User.objects.filter(
            is_active=True
        ).order_by('first_name', 'last_name', 'username')
        
        # Make end_date optional but provide help text
        self.fields['end_date'].required = False
        self.fields['end_date'].help_text = "Leave blank for indefinite assignment"

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if end_date <= start_date:
                raise forms.ValidationError("End date must be after start date.")
        
        return cleaned_data

# Additional forms for better functionality

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'equipment', 'muscle_groups', 'instructions', 'safety_notes', 'video_url']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Exercise name (e.g., Barbell Bench Press)'
            }),
            'equipment': forms.Select(attrs={'class': 'form-select'}),
            'muscle_groups': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Chest, Triceps, Front Deltoids'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Step-by-step instructions for performing this exercise'
            }),
            'safety_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Important safety considerations and contraindications'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipment'].queryset = Equipment.objects.order_by('name')
        self.fields['video_url'].required = False
        self.fields['safety_notes'].required = False

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['name', 'category', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Equipment name (e.g., Barbell, Dumbbell)'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Strength, Cardio, Bodyweight'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description of the equipment and its uses'
            }),
        }

class WorkoutSessionForm(forms.ModelForm):
    class Meta:
        model = WorkoutSession
        fields = ['overall_rpe', 'energy_level', 'notes']
        widgets = {
            'overall_rpe': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
                'placeholder': 'Rate 1-10'
            }),
            'energy_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'placeholder': 'Rate 1-5'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'How did the workout feel? Any issues or observations?'
            }),
        }

# Dynamic formset for creating activities within day templates
from django.forms import formset_factory

ActivityTemplateFormSet = formset_factory(
    ActivityTemplateForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False
)

# Search and filter forms
class ExerciseSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search exercises...'
        })
    )
    equipment = forms.ModelChoiceField(
        queryset=Equipment.objects.all(),
        required=False,
        empty_label="All Equipment",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    muscle_group = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by muscle group...'
        })
    )

class TemplateFilterForm(forms.Form):
    fitness_level = forms.ModelChoiceField(
        queryset=FitnessLevel.objects.all(),
        required=False,
        empty_label="All Fitness Levels",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    goal = forms.ModelChoiceField(
        queryset=Goal.objects.all(),
        required=False,
        empty_label="All Goals",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search templates...'
        })
    )
