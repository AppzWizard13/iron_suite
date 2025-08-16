# urls.py

from django.urls import path, include

from .views import MeasurementTodayView, SendOTPAPIView, VerifyOTPAPIView, LoginAPIView, SignOutAPIView, GoogleLogin, MeasurementProgressView
from .views import UserProfileAPIView, TodayWorkoutAPIView, UpcomingWorkoutsAPIView, WeeklyWorkoutScheduleAPIView

urlpatterns = [
    path('api/send-otp/', SendOTPAPIView.as_view(), name='send_otp_api'),
    path('api/verify-otp/', VerifyOTPAPIView.as_view(), name='verify_otp_api'),
    path('api-v1/login/', LoginAPIView.as_view(), name='api_login'),
    path('api/signout/', SignOutAPIView.as_view(), name='signout'),

    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('accounts/', include('allauth.urls')),  # for Oauth2 flows
    path('dj-rest-auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('api/user/profile/', UserProfileAPIView.as_view(), name='user_profile'),


    path('api/measurements/week/', MeasurementTodayView.as_view(), name='measurement-today'),
    path('api/measurements/progress/', MeasurementProgressView.as_view(), name='measurement-progress'),



    path('api/workouts/today/', TodayWorkoutAPIView.as_view(), name='api_today_workout'),
    path('api/workouts/upcoming/', UpcomingWorkoutsAPIView.as_view(), name='api_upcoming_workouts'),
    path('api/workouts/weekly-schedule/', WeeklyWorkoutScheduleAPIView.as_view(), name='api_weekly_schedule'),


    
]
