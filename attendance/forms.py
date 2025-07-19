from django import forms
from .models import Schedule, ClassEnrollment
from accounts.models import CustomUser


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['name', 'trainer', 'start_time', 'end_time', 'capacity', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'trainer': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['trainer'].queryset = self.get_active_trainers()

    @staticmethod
    def get_active_trainers():
        return CustomUser.objects.filter(staff_role='Trainer', is_active=True)


class ClassEnrollmentForm(forms.ModelForm):
    class Meta:
        model = ClassEnrollment
        fields = ['user', 'schedule']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'schedule': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = self.get_active_members()

    @staticmethod
    def get_active_members():
        return CustomUser.objects.filter(staff_role='Member', is_active=True, on_subscription=False)
