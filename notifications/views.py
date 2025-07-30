from django.views import View
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView
from .models import NotificationConfig, NotificationLog
from django.utils.dateparse import parse_date
from django.db.models import Q
from .utils import send_whatsapp_message
User = get_user_model()

from django.views.generic import UpdateView, CreateView
from django.urls import reverse_lazy
from .models import NotificationConfig

from django.views.generic import UpdateView
from django.urls import reverse_lazy
from .models import NotificationConfig
from .forms import NotificationConfigForm

class NotificationConfigEditView(LoginRequiredMixin,UpdateView):
    model = NotificationConfig
    form_class = NotificationConfigForm
    template_name = 'notifications/notification_config_form.html'
    success_url = reverse_lazy('notification_log_list')

    def get_object(self):
        gym = self.request.user.gym
        obj, created = NotificationConfig.objects.get_or_create(gym=gym)
        return obj


class NotificationLogListView(LoginRequiredMixin, ListView):
    model = NotificationLog
    template_name = 'notifications/notification_logs.html'
    context_object_name = 'logs'
    paginate_by = 25

    def get_queryset(self):
        queryset = NotificationLog.objects.select_related('user').order_by('-sent_at')
        search_query = self.request.GET.get('search', '').strip()
        from_date = self.request.GET.get('from_date', '').strip()
        to_date = self.request.GET.get('to_date', '').strip()

        # Apply search filter
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(phone_number__icontains=search_query)
            )
        # Apply from_date filter
        if from_date:
            queryset = queryset.filter(sent_at__date__gte=parse_date(from_date))
        # Apply to_date filter
        if to_date:
            queryset = queryset.filter(sent_at__date__lte=parse_date(to_date))

        return queryset


    

class SendWhatsAppExpiryAlertsView(View):
    template_name = 'advadmin/send_expiry_alerts.html'

    def get(self, request):
        # Get config (assumes only one row)
        config = NotificationConfig.objects.first()
        if not config:
            messages.error(request, "NotificationConfig is not set. Please create it in admin.")
            return render(request, self.template_name, {'members': []})

        expiry_date = timezone.localdate() + timezone.timedelta(days=config.days_before_expiry)
        members = User.objects.filter(
            staff_role='Member',
            is_active=True,
            on_subscription=True,
            package_expiry_date=expiry_date
        )
        return render(request, self.template_name, {'members': members, 'config': config})

    def post(self, request):
        config = NotificationConfig.objects.first()
        if not config:
            messages.error(request, "NotificationConfig is not set. Please create it in admin.")
            return redirect('send_expiry_alerts')

        expiry_date = timezone.localdate() + timezone.timedelta(days=config.days_before_expiry)
        members = User.objects.filter(
            staff_role='Member',
            is_active=True,
            on_subscription=True,
            package_expiry_date=expiry_date
        )
        sent, failed = 0, 0

        for member in members:
            msg_body = config.message_template.format(
                name=member.first_name,
                expiry=member.package_expiry_date
            )
            success, error = send_whatsapp_message(member.phone_number, msg_body)
            NotificationLog.objects.create(
                user=member,
                phone_number=member.phone_number,
                success=success,
                error_message=error,
                message_body=msg_body
            )
            if success:
                sent += 1
            else:
                failed += 1

        messages.success(request, f"WhatsApp alerts sent to {sent} members. {failed} failures.")
        return redirect('send_expiry_alerts')
