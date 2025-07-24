from datetime import datetime

from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.views.generic import (
    ListView, CreateView, TemplateView
)

from .forms import ScheduleForm, ClassEnrollmentForm
from .models import (
    Attendance, Schedule, ClassEnrollment, QRToken, CheckInLog
)

CustomUser = get_user_model()


class AttendanceAdminView(ListView):
    """
    Admin view for listing attendance with filters.
    """
    model = Attendance
    template_name = 'attendance/view_attendance.html'
    context_object_name = 'attendance_list'
    paginate_by = 20

    def get_queryset(self):
        """
        Optionally filter attendance by user, date, or status.
        """
        queryset = super().get_queryset().select_related('user', 'schedule')
        q = self.request.GET.get('q')
        date = self.request.GET.get('date')
        status = self.request.GET.get('status')

        if q:
            queryset = queryset.filter(
                Q(user__username__icontains=q) |
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(user__phone_number__icontains=q)
            )
        if date:
            queryset = queryset.filter(check_in_time__date=date)
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-check_in_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = "view_attendance"
        return context
class AttendanceReportView(ListView):
    """
    View for generating filtered attendance reports.
    """
    model = Attendance
    template_name = 'attendance/attendance_report.html'
    context_object_name = 'attendance_list'
    paginate_by = 20

    def get_queryset(self):
        """
        Optionally filter attendance by user, date, or status.
        """
        queryset = super().get_queryset().select_related('user', 'schedule')
        q = self.request.GET.get('q')
        date = self.request.GET.get('date')
        status = self.request.GET.get('status')

        if q:
            queryset = queryset.filter(
                Q(user__username__icontains=q) |
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(user__phone_number__icontains=q)
            )

        if date:
            try:
                parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
                queryset = queryset.filter(check_in_time__date=parsed_date)
            except ValueError:
                pass

        if status:
            queryset = queryset.filter(status=status)

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = "attendance_report"
        return context


class ScheduleListView(ListView):
    """
    ListView for all schedules.
    """
    model = Schedule
    template_name = 'attendance/schedule_list.html'
    context_object_name = 'schedules'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        """
        Add pagination to context.
        """
        context = super().get_context_data(**kwargs)
        context['page_obj'] = context.get('page_obj')
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = "schedule_list"
        return context

class ScheduleCreateView(CreateView):
    """
    CreateView for schedules.
    """
    model = Schedule
    form_class = ScheduleForm
    template_name = 'attendance/schedule_form.html'
    success_url = reverse_lazy('schedule_list')


class EnrollmentListView(ListView):
    """
    ListView for class enrollments.
    """
    model = ClassEnrollment
    template_name = 'attendance/enrollment_list.html'
    context_object_name = 'enrollments'
    paginate_by = 20

    def get_queryset(self):
        """
        Prefetch user and schedule.
        """
        return super().get_queryset().select_related('user', 'schedule')

    def get_context_data(self, **kwargs):
        """
        Add pagination to context.
        """
        context = super().get_context_data(**kwargs)
        context['page_obj'] = context.get('page_obj')
        return context
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = "enrollment_list"
        return context


class EnrollmentCreateView(CreateView):
    """
    CreateView for class enrollments.
    """
    model = ClassEnrollment
    form_class = ClassEnrollmentForm
    template_name = 'attendance/enrollment_form.html'
    success_url = reverse_lazy('enrollment_list')


class QRTokenListView(ListView):
    """
    ListView for QR tokens.
    """
    model = QRToken
    template_name = 'attendance/qr_token_list.html'
    context_object_name = 'qr_tokens'
    paginate_by = 20

    def get_queryset(self):
        """
        Prefetch schedule.
        """
        return super().get_queryset().select_related('schedule')

    def get_context_data(self, **kwargs):
        """
        Add pagination to context.
        """
        context = super().get_context_data(**kwargs)
        context['page_obj'] = context.get('page_obj')
        context['page_name'] = "qr_token_list"
        return context


class QRTokenCreateView(CreateView):
    """
    CreateView for QR tokens.
    """
    model = QRToken
    fields = ['schedule']
    template_name = 'attendance/qr_token_form.html'
    success_url = reverse_lazy('qr_token_list')


class CheckInLogListView(ListView):
    """
    ListView for check-in logs.
    """
    model = CheckInLog
    template_name = 'attendance/checkin_log_list.html'
    context_object_name = 'checkin_logs'
    paginate_by = 20

    def get_queryset(self):
        """
        Prefetch related user and token.
        """
        return super().get_queryset().select_related('user', 'token')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = "checkin_log_list"
        return context

class LiveQRView(TemplateView):
    """
    Shows currently live schedules and associated QR tokens.
    """
    template_name = 'attendance/live_qr.html'

    def get_context_data(self, **kwargs):
        """
        Collect live schedules and their latest valid QR tokens.
        """
        context = super().get_context_data(**kwargs)
        now = timezone.localtime()
        current_time = now.time()

        # Get all currently live schedules
        live_schedules = Schedule.objects.filter(
            status='live',
            start_time__lte=current_time,
            end_time__gte=current_time
        ).order_by('start_time')

        schedule_tokens = []
        for schedule in live_schedules:
            token = QRToken.objects.filter(
                schedule=schedule,
                expires_at__gte=now,
                used=False
            ).order_by('-generated_at').first()

            schedule_tokens.append({
                'schedule': schedule,
                'token': token
            })

        context['schedule_tokens'] = schedule_tokens
        return context
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = "live_qr"
        return context

class QRScanView(TemplateView):
    """
    View for QR scan display.
    """
    template_name = 'attendance/scan_qr.html'


@login_required
def qr_checkin_view(request):
    """
    Handles user check-in via QR code.
    """
    token_value = request.GET.get('token')

    if not token_value:
        return render(request, "attendance/success_or_error.html", {
            "success": False,
            "message": "Invalid request. No token provided.",
            "login_url": "/login/"
        }, status=400)

    try:
        qr_token = QRToken.objects.select_related('schedule').get(token=token_value)
    except QRToken.DoesNotExist:
        return render(request, "attendance/success_or_error.html", {
            "success": False,
            "message": "Invalid or expired token.",
            "login_url": "/login/"
        }, status=404)

    if not qr_token.is_valid():
        return render(request, "attendance/success_or_error.html", {
            "success": False,
            "message": "Token has expired or is no longer valid.",
            "login_url": "/login/"
        }, status=403)

    user = request.user
    schedule = qr_token.schedule

    # Check for existing attendance
    attendance, created = Attendance.objects.get_or_create(
        user=user,
        schedule=schedule,
        date=timezone.localdate(),
        defaults={'status': 'checked_in'}
    )

    if not created:
        return render(request, "attendance/success_or_error.html", {
            "success": False,
            "message": "You have already checked in for this class.",
            "details": {
                "Class": schedule.name,
                "Date": str(timezone.localdate()),
                "User": user.get_full_name() or user.username
            },
            "login_url": "/accounts/login/"
        })

    # Mark token as used
    qr_token.mark_used()

    return render(request, "attendance/success_or_error.html", {
        "success": True,
        "message": "Check-in successful!",
        "details": {
            "Class": schedule.name,
            "Date": str(timezone.localdate()),
            "User": user.get_full_name() or user.username
        },
        "login_url": "/accounts/login/"
    })


@require_GET
@login_required
def check_qr_status(request, schedule_id):
    """
    Returns the QR token and info for a live schedule as JSON.
    """
    now = timezone.localtime()
    try:
        schedule = Schedule.objects.get(id=schedule_id, status='live')
    except Schedule.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Schedule not found.'}, status=404)

    token = QRToken.objects.filter(
        schedule=schedule,
        expires_at__gte=now,
        used=False
    ).order_by('-generated_at').first()

    if token:
        return JsonResponse({
            'status': 'ok',
            'token': token.token,
            'expires_at': token.expires_at.strftime('%Y-%m-%d %H:%M:%S'),
            'qr_url': f"https://api.qrserver.com/v1/create-qr-code/"
                      f"?size=200x200&data={request.build_absolute_uri('/checkin/')}?token={token.token}"
        })
    else:
        return JsonResponse({'status': 'waiting'})
