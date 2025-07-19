from django.views.generic import (
    CreateView, UpdateView, TemplateView, ListView, DetailView, DeleteView
)
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import redirect

from payments.models import Payment, Transaction
from .models import BusinessDetails, Configuration
from .forms import BusinessDetailsForm, ConfigurationForm

from orders.models import (
    Cart, CartItem, Order, OrderItem, TempOrder
)
from products.models import Product
from accounts.models import Customer, User


class BusinessDetailsCreateView(SuccessMessageMixin, CreateView):
    """
    View for creating BusinessDetails instances.
    """
    model = BusinessDetails
    form_class = BusinessDetailsForm
    template_name = 'advadmin/business_details_form.html'
    success_url = reverse_lazy('business_details')
    success_message = "Business details created successfully!"

    def get_context_data(self, **kwargs):
        """
        Add title for context.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Business Details'
        return context


class BusinessDetailsUpdateView(SuccessMessageMixin, UpdateView):
    """
    View for updating the single BusinessDetails instance.
    """
    model = BusinessDetails
    form_class = BusinessDetailsForm
    template_name = 'advadmin/business_details_form.html'
    success_url = reverse_lazy('business_details')
    success_message = "Business details updated successfully!"

    def get_object(self, queryset=None):
        """
        Get or create the unique BusinessDetails instance.
        """
        obj, _ = BusinessDetails.objects.get_or_create(pk=1)
        return obj

    def get_context_data(self, **kwargs):
        """
        Add title for context.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Business Details'
        return context


class BusinessDetailsView(SuccessMessageMixin, UpdateView):
    """
    Combined create/update view for BusinessDetails.
    Determines if details must be created or updated.
    """
    model = BusinessDetails
    form_class = BusinessDetailsForm
    template_name = 'advadmin/business_details_form.html'
    success_url = reverse_lazy('business_details')
    success_message = "Business details %(verb)s successfully!"
    verbs = {True: 'created', False: 'updated'}

    def get_object(self, queryset=None):
        """
        Get or create the unique BusinessDetails instance; 
        sets self.created flag.
        """
        obj, created = BusinessDetails.objects.get_or_create(pk=1)
        self.created = created
        return obj

    def get_context_data(self, **kwargs):
        """
        Add title and creation state to context.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Business Details'
        context['is_creating'] = getattr(self, 'created', False)
        return context

    def get_success_message(self, cleaned_data):
        """
        Return the appropriate success message.
        """
        return self.success_message % {'verb': self.verbs[self.created]}


class ConfigurationCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating new configuration entries.
    """
    model = Configuration
    form_class = ConfigurationForm
    template_name = 'admin_panel/configuration_form.html'
    success_url = reverse_lazy('configuration_list')

    def form_valid(self, form):
        """
        On valid form, show success.
        """
        messages.success(self.request, "Configuration added successfully!")
        return super().form_valid(form)

    def get_template_names(self):
        """
        Select template based on admin panel mode.
        """
        admin_mode = getattr(self.request, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/configuration_form.html']
        return ['admin_panel/configuration_form.html']

    def form_invalid(self, form):
        """
        Show error if form is invalid.
        """
        messages.error(
            self.request,
            "Error adding configuration. Please check the form."
        )
        return super().form_invalid(form)


class ConfigurationListView(LoginRequiredMixin, ListView):
    """
    List all configurations.
    """
    model = Configuration
    template_name = 'admin_panel/configuration_list.html'
    context_object_name = 'configurations'
    paginate_by = 20

    def get_template_names(self):
        """
        Select template based on admin panel mode.
        """
        admin_mode = getattr(self.request, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/configuration_list.html']
        return ['admin_panel/configuration_list.html']


class ConfigurationDetailView(LoginRequiredMixin, DetailView):
    """
    Show configuration details.
    """
    model = Configuration
    template_name = 'admin_panel/configuration_detail.html'
    context_object_name = 'config'

    def get_template_names(self):
        """
        Select template based on admin panel mode.
        """
        admin_mode = getattr(self.request, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/configuration_detail.html']
        return ['admin_panel/configuration_detail.html']


class ConfigurationUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing configuration.
    """
    model = Configuration
    form_class = ConfigurationForm
    template_name = 'admin_panel/configuration_form.html'
    success_url = reverse_lazy('configuration_list')

    def form_valid(self, form):
        """
        On form valid, show success.
        """
        messages.success(self.request, "Configuration updated successfully!")
        return super().form_valid(form)

    def get_template_names(self):
        """
        Select template based on admin panel mode.
        """
        admin_mode = getattr(self.request, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/configuration_form.html']
        return ['admin_panel/configuration_form.html']

    def form_invalid(self, form):
        """
        Show error if form is invalid.
        """
        messages.error(
            self.request,
            "Error updating configuration. Please check the form."
        )
        return super().form_invalid(form)


class ConfigurationDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete a configuration entry.
    """
    model = Configuration
    success_url = reverse_lazy('configuration_list')
    template_name = None

    def get(self, request, *args, **kwargs):
        """
        Allow GET method for confirmationless deletes.
        """
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Delete and show success message.
        """
        messages.success(request, "Configuration deleted successfully!")
        return super().delete(request, *args, **kwargs)


class SystemReset(TemplateView):
    """
    System reset view for various types of system-wide resets.
    """
    template_name = 'advadmin/system-reset_view.html'

    def get_context_data(self, **kwargs):
        """
        Provide reset options to the template context.
        """
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
        """
        Perform reset action based on posted reset_type.
        """
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
                messages.success(
                    request,
                    "Order, Payment, TempOrder, and Cart data reset successfully."
                )
            elif reset_type == 'user':
                Customer.objects.all().delete()
                User.objects.exclude(is_superuser=True).delete()
                Cart.objects.all().delete()
                messages.success(request, "Customer and User data reset successfully.")
            elif reset_type == 'cms':
                # Placeholder: add your CMS models and their delete logic
                messages.success(
                    request,
                    "CMS data reset successfully (update with your CMS models)."
                )
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
                # Add your CMS models here if applicable
                messages.success(request, "Entire system data reset successfully.")
            else:
                messages.error(request, "Invalid reset type.")
        except Exception as e:
            messages.error(request, f"Error during reset: {str(e)}")
        return redirect(reverse('system_reset'))
