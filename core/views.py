from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from .models import BusinessDetails
from .forms import BusinessDetailsForm
from django.views.generic import TemplateView
from django.views.generic import TemplateView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class BusinessDetailsCreateView(SuccessMessageMixin, CreateView):
    model = BusinessDetails
    form_class = BusinessDetailsForm
    template_name = 'advadmin/business_details_form.html'
    success_url = reverse_lazy('business_details')
    success_message = "Business details created successfully!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Business Details'
        return context

class BusinessDetailsUpdateView(SuccessMessageMixin, UpdateView):
    model = BusinessDetails
    form_class = BusinessDetailsForm
    template_name = 'advadmin/business_details_form.html'
    success_url = reverse_lazy('business_details')
    success_message = "Business details updated successfully!"

    def get_object(self, queryset=None):
        # Get the single instance or create new if doesn't exist
        obj, created = BusinessDetails.objects.get_or_create(pk=1)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Business Details'
        return context

from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from .models import BusinessDetails
from .forms import BusinessDetailsForm

class BusinessDetailsView(SuccessMessageMixin, UpdateView):
    model = BusinessDetails
    form_class = BusinessDetailsForm
    template_name = 'advadmin/business_details_form.html'
    success_url = reverse_lazy('business_details')
    success_message = "Business details %(verb)s successfully!"
    
    # Define verbs for message based on whether creating or updating
    verbs = {True: 'created', False: 'updated'}

    def get_object(self, queryset=None):
        # Get the single instance or create new if doesn't exist
        obj, created = BusinessDetails.objects.get_or_create(pk=1)
        self.created = created  # Store whether we're creating or updating
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Business Details'
        context['is_creating'] = getattr(self, 'created', False)
        return context

    def get_success_message(self, cleaned_data):
        return self.success_message % {'verb': self.verbs[self.created]}
    

from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    CreateView, ListView, UpdateView, DeleteView, DetailView
)
from django.conf import settings
from .models import Configuration
from .forms import ConfigurationForm

class ConfigurationCreateView(LoginRequiredMixin, CreateView):
    model = Configuration
    form_class = ConfigurationForm
    template_name = 'admin_panel/configuration_form.html'
    success_url = reverse_lazy('configuration_list')

    def form_valid(self, form):
        messages.success(self.request, "Configuration added successfully!")
        return super().form_valid(form)
    
    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/configuration_form.html']
        elif admin_mode == 'standard':
            return ['admin_panel/configuration_form.html']
        else:
            return ['admin_panel/configuration_form.html']

    def form_invalid(self, form):
        messages.error(self.request, "Error adding configuration. Please check the form.")
        return super().form_invalid(form)

class ConfigurationListView(LoginRequiredMixin, ListView):
    model = Configuration
    template_name = 'admin_panel/configuration_list.html'
    context_object_name = 'configurations'
    paginate_by = 20
    
    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/configuration_list.html']
        elif admin_mode == 'standard':
            return ['admin_panel/configuration_list.html']
        else:
            return ['admin_panel/configuration_list.html']

class ConfigurationDetailView(LoginRequiredMixin, DetailView):
    model = Configuration
    template_name = 'admin_panel/configuration_detail.html'
    context_object_name = 'config'

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/configuration_detail.html']
        elif admin_mode == 'standard':
            return ['admin_panel/configuration_detail.html']
        else:
            return ['admin_panel/configuration_detail.html']

class ConfigurationUpdateView(LoginRequiredMixin, UpdateView):
    model = Configuration
    form_class = ConfigurationForm
    template_name = 'admin_panel/configuration_form.html'
    success_url = reverse_lazy('configuration_list')

    def form_valid(self, form):
        messages.success(self.request, "Configuration updated successfully!")
        return super().form_valid(form)
    
    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/configuration_form.html']
        elif admin_mode == 'standard':
            return ['admin_panel/configuration_form.html']
        else:
            return ['admin_panel/configuration_form.html']

    def form_invalid(self, form):
        messages.error(self.request, "Error updating configuration. Please check the form.")
        return super().form_invalid(form)

class ConfigurationDeleteView(LoginRequiredMixin, DeleteView):
    model = Configuration
    success_url = reverse_lazy('configuration_list')
    template_name = None

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Configuration deleted successfully!")
        return super().delete(request, *args, **kwargs)
    

class ConfigurationDeleteView(LoginRequiredMixin, DeleteView):
    model = Configuration
    success_url = reverse_lazy('configuration_list')
    template_name = None

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Configuration deleted successfully!")
        return super().delete(request, *args, **kwargs)
    

from orders.models import (
    Cart, CartItem, Order, OrderItem, Payment,
    Transaction, TempOrder, GooglePayCredentials
)
from products.models import (
    Product
)

from accounts.models import (
    Customer, User
)
class SystemReset(TemplateView):
    template_name = 'advadmin/system-reset_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reset_options'] = [
            {'label': 'Order & Payment Reset', 'action': 'order_payment'},
            {'label': 'User Reset', 'action': 'user'},
            {'label': 'CMS Reset', 'action': 'cms'},
            {'label': 'Product Reset', 'action': 'product'},
            {'label': 'All Reset', 'action': 'all'},
        ]
        return context

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        reset_type = request.POST.get('reset_type')

        try:
            if reset_type == 'order_payment':
                Transaction.objects.all().delete()
                Payment.objects.all().delete()
                OrderItem.objects.all().delete()
                Order.objects.all().delete()
                TempOrder.objects.all().delete()
                CartItem.objects.all().delete()
                Cart.objects.all().delete()
                messages.success(request, "Order, Payment, TempOrder, and Cart data reset successfully.")

            elif reset_type == 'user':
                # Be cautious with deleting users.
                Customer.objects.all().delete()
                User.objects.exclude(is_superuser=True).delete()
                Cart.objects.all().delete()
                messages.success(request, "Customer and User data reset successfully.")

            elif reset_type == 'cms':
                # Placeholder: add your CMS models and their delete logic
                messages.success(request, "CMS data reset successfully (update with your CMS models).")

            elif reset_type == 'product':
                Product.objects.all().delete()
                messages.success(request, "All product data reset successfully.")

            elif reset_type == 'all':
                Transaction.objects.all().delete()
                Payment.objects.all().delete()
                OrderItem.objects.all().delete()
                Order.objects.all().delete()
                TempOrder.objects.all().delete()
                CartItem.objects.all().delete()
                Cart.objects.all().delete()
                Product.objects.all().delete()
                Customer.objects.all().delete()
                User.objects.exclude(is_superuser=True).delete()
                GooglePayCredentials.objects.all().delete()
                # Add your CMS models here if applicable
                messages.success(request, "Entire system data reset successfully.")

            else:
                messages.error(request, "Invalid reset type.")

        except Exception as e:
            messages.error(request, f"Error during reset: {str(e)}")

        return redirect(reverse('system_reset'))
