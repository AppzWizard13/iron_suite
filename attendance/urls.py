from django.urls import path
from . import views

urlpatterns = [
    path('view/attendance/', views.AttendanceAdminView.as_view(), name='view_attendance'),
    path('schedule/', views.ScheduleListView.as_view(), name='schedule_list'),
    path('schedule/create/', views.ScheduleCreateView.as_view(), name='schedule_create'),
    path('schedules/<int:pk>/edit/', views.ScheduleUpdateView.as_view(), name='schedule_edit'),
    path('schedules/<int:pk>/delete/', views.schedule_delete, name='schedule_delete'),
    path('enrollments/', views.EnrollmentListView.as_view(), name='enrollment_list'),
    path('qr-tokens/', views.QRTokenListView.as_view(), name='qr_token_list'),
    path('checkin-logs/', views.CheckInLogListView.as_view(), name='checkin_log_list'),
    path('attendance/report/', views.AttendanceReportView.as_view(), name='attendance_report'),
    path('enrollment/create/', views.EnrollmentCreateView.as_view(), name='enrollment_create'),

    path('qr-token/create/', views.QRTokenCreateView.as_view(), name='qr_token_create'),
    path('qr/live/', views.LiveQRView.as_view(), name='live_qr'),

    path('qr/livecheckin/', views.qr_checkin_view, name='qr_livecheckin'),
    path('qr/scan/', views.QRScanView.as_view(), name='qr_scan'),

    path('api/check-qr-status/<int:schedule_id>/', views.check_qr_status, name='check_qr_status'),
]
