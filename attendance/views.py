from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.timezone import make_aware
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, TemplateView

from .models import Attendance, Schedule, ClassEnrollment, QRToken, CheckInLog
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from .models import Schedule, ClassEnrollment, QRToken, CheckInLog
from .forms import ScheduleForm
from django.views.generic import CreateView
from .models import ClassEnrollment

CustomUser = get_user_model()


class AttendanceAdminView(ListView):
    model = Attendance
    template_name = 'attendance/view_attendance.html'
    context_object_name = 'attendance_list'
    paginate_by = 20

    def get_queryset(self):
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



class AttendanceReportView(ListView):
    model = Attendance
    template_name = 'attendance/attendance_report.html'
    context_object_name = 'attendance_list'
    paginate_by = 20

    def get_queryset(self):
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




class ScheduleListView(ListView):
    model = Schedule
    template_name = 'attendance/schedule_list.html'
    context_object_name = 'schedules'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = context.get('page_obj')  # Ensures pagination works if included
        return context



class ScheduleCreateView(CreateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = 'attendance/schedule_form.html'
    success_url = reverse_lazy('schedule_list')
    

class EnrollmentListView(ListView):
    model = ClassEnrollment
    template_name = 'attendance/enrollment_list.html'
    context_object_name = 'enrollments'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().select_related('user', 'schedule')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = context.get('page_obj')
        return context
    

from .forms import ClassEnrollmentForm

class EnrollmentCreateView(CreateView):
    model = ClassEnrollment
    form_class = ClassEnrollmentForm
    template_name = 'attendance/enrollment_form.html'
    success_url = reverse_lazy('enrollment_list')


class QRTokenListView(ListView):
    model = QRToken
    template_name = 'attendance/qr_token_list.html'
    context_object_name = 'qr_tokens'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().select_related('schedule')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = context.get('page_obj')
        return context
    
from django.views.generic import CreateView
from .models import QRToken
from django.urls import reverse_lazy

class QRTokenCreateView(CreateView):
    model = QRToken
    fields = ['schedule']
    template_name = 'attendance/qr_token_form.html'
    success_url = reverse_lazy('qr_token_list')


class CheckInLogListView(ListView):
    model = CheckInLog
    template_name = 'attendance/checkin_log_list.html'
    context_object_name = 'checkin_logs'
    paginate_by = 20

    def get_queryset(self):
        return super().get_queryset().select_related('user', 'token')

from django.views.generic import TemplateView
from django.utils import timezone
from .models import Schedule, QRToken

class LiveQRView(TemplateView):
    template_name = 'attendance/live_qr.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.localtime()
        current_time = now.time()
        print("Current Time:", current_time)

        # Get all currently live schedules
        live_schedules = Schedule.objects.filter(
            status='live',
            start_time__lte=current_time,
            end_time__gte=current_time
        ).order_by('start_time')

        print("Live Schedules:", live_schedules)

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


from django.views.generic import TemplateView

class QRScanView(TemplateView):
    template_name = 'attendance/scan_qr.html'
from django.shortcuts import render
from django.utils import timezone
from .models import QRToken, Attendance
from django.contrib.auth.decorators import login_required

@login_required
def qr_checkin_view(request):
    token_value = request.GET.get('token')

    if not token_value:
        return render(request, "attendance/success_or_error.html", {
            "success": False,
            "message": "Invalid request. No token provided.",
            "login_url": "/accounts/login/"
        }, status=400)

    try:
        qr_token = QRToken.objects.select_related('schedule').get(token=token_value)
    except QRToken.DoesNotExist:
        return render(request, "attendance/success_or_error.html", {
            "success": False,
            "message": "Invalid or expired token.",
            "login_url": "/accounts/login/"
        }, status=404)

    if not qr_token.is_valid():
        return render(request, "attendance/success_or_error.html", {
            "success": False,
            "message": "Token has expired or is no longer valid.",
            "login_url": "/accounts/login/"
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


from django.http import JsonResponse
from .models import QRToken, Schedule
from django.utils import timezone
from django.views.decorators.http import require_GET

@require_GET
@login_required
def check_qr_status(request, schedule_id):
    now = timezone.localtime()
    try:
        schedule = Schedule.objects.get(id=schedule_id, status='live')
    except Schedule.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Schedule not found.'}, status=404)

    # Get latest valid token
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
            'qr_url': f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={request.build_absolute_uri('/checkin/')}?token={token.token}"
        })
    else:
        return JsonResponse({'status': 'waiting'})
