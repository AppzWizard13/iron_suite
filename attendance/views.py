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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .forms import ScheduleForm, ClassEnrollmentForm
from .models import (
    Attendance, Schedule, ClassEnrollment, QRToken, CheckInLog
)
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Attendance
from .serializers import AttendanceSerializer

CustomUser = get_user_model()


class AttendanceAdminView(LoginRequiredMixin, ListView):
    """
    Admin view for listing attendance with filters, scoped to Vendor.
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
        queryset = queryset.filter(schedule__vendor=self.request.user.vendor)  # Multi-tenant filter

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

class AttendanceReportView(LoginRequiredMixin, ListView):
    """
    View for generating filtered attendance reports, scoped to Vendor.
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
        queryset = queryset.filter(schedule__vendor=self.request.user.vendor)  # Multi-tenant filter

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


class ScheduleListView(LoginRequiredMixin, ListView):
    """
    ListView for all schedules filtered by tenant (Vendor).
    """
    model = Schedule
    template_name = 'attendance/schedule_list.html'
    context_object_name = 'schedules'
    paginate_by = 20

    def get_queryset(self):
        """
        Filter schedules by the logged-in user's Vendor.
        """
        user = self.request.user
        return super().get_queryset().filter(Vendor=user.vendor)

    def get_context_data(self, **kwargs):
        """
        Add page name and pagination to context.
        """
        context = super().get_context_data(**kwargs)
        context['page_name'] = "schedule_list"
        context['page_obj'] = context.get('page_obj')
        return context

class ScheduleCreateView(LoginRequiredMixin,CreateView):
    """
    CreateView for schedules.
    """
    model = Schedule
    form_class = ScheduleForm
    template_name = 'attendance/schedule_form.html'
    success_url = reverse_lazy('schedule_list')

    def form_valid(self, form):
        # Automatically set the Vendor from the current user
        form.instance.Vendor = self.request.user.vendor
        return super().form_valid(form)



from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from attendance.models import Schedule

class ScheduleUpdateView(LoginRequiredMixin,UpdateView):
    model = Schedule
    fields = ['name', 'start_time', 'end_time', 'trainer', 'capacity', 'status']
    template_name = 'attendance/schedule_form.html'
    success_url = reverse_lazy('schedule_list')

    def form_valid(self, form):
        messages.success(self.request, "Schedule updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error updating the schedule.")
        return super().form_invalid(form)

from django.views.decorators.http import require_POST
from django.shortcuts import redirect, get_object_or_404
@require_POST
def schedule_delete(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    schedule.delete()
    messages.success(request, f"Schedule '{schedule.name}' deleted successfully.")
    return redirect('schedule_list')

    
class EnrollmentListView(LoginRequiredMixin, ListView):
    """
    ListView for class enrollments filtered by tenant (Vendor).
    """
    model = ClassEnrollment
    template_name = 'attendance/enrollment_list.html'
    context_object_name = 'enrollments'
    paginate_by = 20

    def get_queryset(self):
        """
        Prefetch user and schedule, and filter enrollments by Vendor.
        """
        return super().get_queryset().select_related('user', 'schedule').filter(
            schedule__vendor=self.request.user.vendor
        )

    def get_context_data(self, **kwargs):
        """
        Add page name and pagination context.
        """
        context = super().get_context_data(**kwargs)
        context['page_obj'] = context.get('page_obj')
        context['page_name'] = "enrollment_list"
        return context


class EnrollmentCreateView(LoginRequiredMixin,CreateView):
    model = ClassEnrollment
    form_class = ClassEnrollmentForm
    template_name = 'attendance/enrollment_form.html'
    success_url = reverse_lazy('enrollment_list')

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.Vendor = instance.schedule.Vendor  # Ensure Vendor is set before saving
        return super().form_valid(form)


class QRTokenListView(LoginRequiredMixin, ListView):
    """
    ListView for QR tokens filtered by tenant (Vendor).
    """
    model = QRToken
    template_name = 'attendance/qr_token_list.html'
    context_object_name = 'qr_tokens'
    paginate_by = 20

    def get_queryset(self):
        """
        Filter QR tokens by the logged-in user's Vendor via schedule.
        """
        user = self.request.user
        return super().get_queryset().select_related('schedule').filter(schedule__vendor=user.vendor)

    def get_context_data(self, **kwargs):
        """
        Add pagination and page name to context.
        """
        context = super().get_context_data(**kwargs)
        context['page_obj'] = context.get('page_obj')
        context['page_name'] = "qr_token_list"
        return context



class QRTokenCreateView(LoginRequiredMixin,CreateView):
    """
    CreateView for QR tokens.
    """
    model = QRToken
    fields = ['schedule']
    template_name = 'attendance/qr_token_form.html'
    success_url = reverse_lazy('qr_token_list')


class CheckInLogListView(LoginRequiredMixin, ListView):
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

class LiveQRView(LoginRequiredMixin,TemplateView):
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

class QRScanView(LoginRequiredMixin,TemplateView):
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





class AttendanceListView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Attendance.objects.filter(user=self.request.user)

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from accounts.models import Vendor
from .models import Schedule, QRToken, Attendance, CheckInLog
import json

class QRGeneratorView(View):
    def get(self, request):
        vendors = Vendor.objects.all()
        return render(request, 'advadmin/qr_generator.html', {'vendors': vendors})

    def post(self, request):
        try:
            vendor_id = request.POST.get('vendor_id')
            validity_days = request.POST.get('validity_days')

            if not vendor_id:
                return JsonResponse({'success': False, 'message': 'Vendor ID is required'})

            Vendor = get_object_or_404(Vendor, id=vendor_id)

            # Use entered validity days, fallback to 1 day if not provided
            try:
                validity_days = int(validity_days) if validity_days else 1
            except ValueError:
                validity_days = 1

            expires_at = timezone.now() + timedelta(days=validity_days)

            today = timezone.now().date()
            schedule, created = Schedule.objects.get_or_create(
                Vendor=Vendor,
                schedule_date=today,
                defaults={
                    'name': f'General Attendance - {today.strftime("%d %b %Y")}',
                    'start_time': timezone.now().time(),
                    'end_time': (timezone.now() + timedelta(hours=12)).time(),
                    'capacity': 1000,
                    'status': 'live'
                }
            )

            qr_token = QRToken.objects.create(
                schedule=schedule,
                Vendor=Vendor,
                expires_at=expires_at
            )

            qr_data_url = request.build_absolute_uri(f'/api/attendance/scan/{qr_token.token}/')

            return JsonResponse({
                'success': True,
                'qr_data': qr_data_url,
                'vendor_name': Vendor.name,
                'token': qr_token.token,
                'expires_at': qr_token.expires_at.isoformat(),
                'schedule_id': schedule.id,
                'validity_days': validity_days
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})


# **Main API for Mobile App** - Returns JSON only
class AttendanceScanAPI(APIView):
    """
    API endpoint for mobile app to scan QR and mark attendance
    Returns JSON responses only - no HTML templates
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, token):
        try:
            # Get QR token
            qr_token = get_object_or_404(QRToken, token=token)
            
            # Validate token
            if not qr_token.is_valid():
                return Response({
                    'success': False,
                    'message': 'QR code expired or invalid',
                    'error_code': 'INVALID_TOKEN'
                }, status=status.HTTP_400_BAD_REQUEST)

            user = request.user
            schedule = qr_token.schedule
            today = timezone.now().date()
            current_time = timezone.now()

            # Check if user already has attendance today
            existing_attendance = Attendance.objects.filter(
                user=user,
                schedule=schedule,
                date=today
            ).first()

            if existing_attendance:
                # Check if it's within 15 minutes (prevent duplicate check-in)
                time_diff = current_time - existing_attendance.check_in_time
                
                if time_diff.total_seconds() < 900:  # 15 minutes = 900 seconds
                    return Response({
                        'success': False,
                        'message': f'Attendance already marked at {existing_attendance.check_in_time.strftime("%I:%M %p")}',
                        'check_in_time': existing_attendance.check_in_time.strftime("%I:%M %p"),
                        'status': 'already_marked',
                        'error_code': 'ALREADY_MARKED'
                    }, status=status.HTTP_200_OK)
                
                # After 15 minutes, consider it as checkout
                elif not existing_attendance.check_out_time:
                    existing_attendance.mark_checkout()
                    
                    # Log the checkout
                    CheckInLog.objects.create(
                        user=user,
                        token=qr_token,
                        attendance=existing_attendance,
                        Vendor=qr_token.Vendor,
                        ip_address=self.get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        gps_lat=request.data.get('latitude'),
                        gps_lng=request.data.get('longitude')
                    )

                    return Response({
                        'success': True,
                        'message': 'Successfully checked out!',
                        'check_in_time': existing_attendance.check_in_time.strftime("%I:%M %p"),
                        'check_out_time': existing_attendance.check_out_time.strftime("%I:%M %p"),
                        'duration': str(existing_attendance.duration).split('.')[0],
                        'status': 'checked_out',
                        'vendor_name': qr_token.Vendor.name
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'success': False,
                        'message': 'You have already completed attendance for today',
                        'status': 'completed',
                        'error_code': 'ALREADY_COMPLETED'
                    }, status=status.HTTP_200_OK)

            # Create new attendance (check-in)
            attendance = Attendance.objects.create(
                user=user,
                schedule=schedule,
                Vendor=qr_token.Vendor,
                date=today,
                status='checked_in'
            )

            # Log the check-in
            CheckInLog.objects.create(
                user=user,
                token=qr_token,
                attendance=attendance,
                Vendor=qr_token.Vendor,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                gps_lat=request.data.get('latitude'),
                gps_lng=request.data.get('longitude')
            )

            return Response({
                'success': True,
                'message': 'Attendance marked successfully!',
                'check_in_time': attendance.check_in_time.strftime("%I:%M %p"),
                'vendor_name': qr_token.Vendor.name,
                'status': 'checked_in',
                'user_name': user.get_full_name() or user.username
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error marking attendance: {str(e)}',
                'error_code': 'SERVER_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

# Optional: Get QR info without marking attendance (for preview)
class QRInfoAPI(APIView):
    """
    Get QR code information without marking attendance
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, token):
        try:
            qr_token = get_object_or_404(QRToken, token=token)
            
            return Response({
                'success': True,
                'vendor_name': qr_token.Vendor.name,
                'schedule_name': qr_token.schedule.name,
                'valid_until': qr_token.expires_at.isoformat(),
                'is_valid': qr_token.is_valid(),
                'status': qr_token.schedule.status
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
