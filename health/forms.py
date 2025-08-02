from django import forms
from django.contrib.auth import get_user_model
from health.models import WorkoutProgram, WorkoutTemplate

User = get_user_model()

class TemplateAssignForm(forms.Form):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'size': 10,  # Show more users at once; adjust as needed
        }),
        label="Select Members"
    )
    template = forms.ModelChoiceField(
        queryset=WorkoutTemplate.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Workout Template"
    )
    start_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': "Select Start Date"
            }
        ),
        label="Plan Start Date"
    )

from django import forms
from health.models import WorkoutProgram

class WorkoutProgramForm(forms.ModelForm):
    class Meta:
        model = WorkoutProgram
        fields = [
            'name',
            'category',
            'type',
            'level',
            'sets',
            'reps',
            'notes',
            'equipment',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Workout Name',
                'autocomplete': 'off',
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'sets': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'step': 1,
                'placeholder': 'Sets',
                'autocomplete': 'off',
            }),
            'reps': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 8-12',
                'autocomplete': 'off',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes (optional)',
                'autocomplete': 'off',
            }),
            'equipment': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
        }
