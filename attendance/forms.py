from django import forms
from .models import Schedule

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['name', 'trainer', 'start_time', 'end_time', 'capacity', 'status']  # ❌ Removed 'weekday'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'trainer': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

# forms.py
from django import forms
from .models import ClassEnrollment

class ClassEnrollmentForm(forms.ModelForm):
    class Meta:
        model = ClassEnrollment
        fields = ['user', 'schedule']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'schedule': forms.Select(attrs={'class': 'form-select'}),
        }