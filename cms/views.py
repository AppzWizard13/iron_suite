from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from .models import Ticket, ChatMessage
from .forms import TicketForm, ChatMessageForm, AssignTicketForm
from django.contrib import messages

class TicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'advadmin/ticket_list.html'
    context_object_name = 'tickets'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        filter_type = self.kwargs.get('filter_type')
        
        # Filter tickets assigned to the current user
        if not self.request.user.staff_role == "Admin":
            queryset = queryset.filter(support_executive__user=self.request.user)
        
        # Apply status filters based on URL parameter
        if filter_type == 'ongoing':
            queryset = queryset.filter(status__in=['open', 'in_progress'])
        elif filter_type == 'resolved':
            queryset = queryset.filter(status__in=['resolved', 'closed'])
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_filter'] = self.kwargs.get('filter_type', 'all')
        
        # Get counts for each filter type
        context['filter_counts'] = {
            'all': self.model.objects.filter(support_executive__user=self.request.user).count(),
            'ongoing': self.model.objects.filter(
                support_executive__user=self.request.user,
                status__in=['Open', 'In Progress']
            ).count(),
            'resolved': self.model.objects.filter(
                support_executive__user=self.request.user,
                status__in=['Resolved', 'Closed']
            ).count()
        }
        return context

from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Ticket, ChatMessage
from .forms import ChatMessageForm

class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'advadmin/ticket_detail.html'
    context_object_name = 'ticket'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ChatMessageForm()
        # Get all tickets assigned to the current user
        context['assigned_tickets'] = Ticket.objects.filter(
        ).order_by('-created_at')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            chat_message = form.save(commit=False)
            chat_message.ticket = self.object
            chat_message.sender = request.user
            if self.object.status == "open":
                self.object.status = "in_progress"  # Use assignment operator here
                print("status updating to In progress")
                self.object.save()
                
            chat_message.save()
            return redirect('ticket_detail', pk=self.object.pk)
        return self.render_to_response(self.get_context_data(form=form))


class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'advadmin/ticket_form.html'
    success_url = reverse_lazy('ticket_list')

    def form_valid(self, form):
        # Generate a unique ticket_id
        last_ticket = Ticket.objects.order_by('-id').first()
        if last_ticket and last_ticket.ticket_id:
            last_ticket_number = int(last_ticket.ticket_id.replace('SPRT', ''))
            new_ticket_number = last_ticket_number + 1
        else:
            new_ticket_number = 1

        # Format the ticket_id to ensure it has 6 digits
        ticket_id = f"SPRT{new_ticket_number:06d}"

        # Assign the ticket_id and customer to the new ticket
        form.instance.ticket_id = ticket_id
        form.instance.customer = self.request.user

        return super().form_valid(form)
    
class TicketEditView(LoginRequiredMixin, UpdateView):
    model = Ticket
    form_class = AssignTicketForm
    template_name = 'advadmin/assign_ticket.html'
    success_url = reverse_lazy('ticket_list')

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.http import HttpResponseRedirect
from .models import Ticket

class TicketDeleteView(LoginRequiredMixin, DeleteView):
    model = Ticket
    success_url = reverse_lazy('ticket_list')

    def get(self, request, *args, **kwargs):
        # Directly call the delete method without showing a confirmation template
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # Call the parent class's delete method to perform the deletion
        response = super().delete(request, *args, **kwargs)
        # Add a success message
        messages.success(request, 'Ticket deleted successfully.')
        return response
    
from django.contrib.auth.decorators import login_required

@login_required
def resolve_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    print("request.methodrequest.method", request.method)
    if request.method == 'GET':
        print("cccccccccccccccccccccccccc")
        ticket.status = 'resolved'
        ticket.save()
        return redirect('ticket_detail', pk=pk)
    return redirect('ticket_detail', pk=pk)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from .models import SupportExecutive
from .forms import SupportExecutiveForm

class SupportExecutiveListView(LoginRequiredMixin, ListView):
    model = SupportExecutive
    template_name = 'advadmin/support_executive_list.html'
    context_object_name = 'support_executives'

class SupportExecutiveCreateView(LoginRequiredMixin, CreateView):
    model = SupportExecutive
    form_class = SupportExecutiveForm
    template_name = 'advadmin/support_executive_form.html'
    success_url = reverse_lazy('support_executive_list')

class SupportExecutiveEditView(LoginRequiredMixin, UpdateView):
    model = SupportExecutive
    form_class = SupportExecutiveForm
    template_name = 'advadmin/support_executive_form.html'
    success_url = reverse_lazy('support_executive_list')

class SupportExecutiveDeleteView(LoginRequiredMixin, DeleteView):
    model = SupportExecutive
    template_name = 'advadmin/support_executive_confirm_delete.html'
    success_url = reverse_lazy('support_executive_list')