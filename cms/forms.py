from django import forms
from .models import Ticket, ChatMessage
from django import forms
from .models import Ticket, SupportExecutive

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description']

from django import forms
from .models import Ticket, SupportExecutive

class AssignTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['support_executive']
        widgets = {
            'support_executive': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super(AssignTicketForm, self).__init__(*args, **kwargs)
        self.fields['support_executive'].queryset = SupportExecutive.objects.all()
        self.fields['support_executive'].label = "Assign to Support Executive"

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message']



from django import forms
from .models import SupportExecutive

class SupportExecutiveForm(forms.ModelForm):
    class Meta:
        model = SupportExecutive
        fields = ['user', 'department']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
        }