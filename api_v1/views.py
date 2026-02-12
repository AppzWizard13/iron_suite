from datetime import timedelta
import random
from accounts import models
from accounts.views import DashboardView
from attendance.models import Attendance
from core.choices import TransactionCategoryChoice, TransactionTypeChoice
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from orders.models import Order, SubscriptionOrder
from payments.models import Payment, PaymentAPILog
from products.models import Package
from rest_framework.permissions import IsAuthenticated

from django.conf import settings
from django.contrib.auth import (
    authenticate, get_user_model, login, logout
)
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import permissions, status
from rest_framework.decorators import renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from health.models import BodyMeasurement
from health.serializers import BodyMeasurementTodaySerializer
import logging

logger = logging.getLogger(__name__)  # Django logger


from core.models import Configuration

User = get_user_model()


@renderer_classes([JSONRenderer])
class SendOTPAPIView(APIView):
    """
    Sends an OTP to the user's phone number (via SMS and/or Email)
    depending on system configuration.
    """
    permission_classes = [AllowAny]
    http_method_names = ['post', 'options']

    def post(self, request):
        """
        Handle POST request to send OTP to user's registered phone number.
        """
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return self._error_response(
                message="Phone number is required.",
                error_code="PHONE_NUMBER_REQUIRED",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return self._error_response(
                message="No user found with this phone number.",
                error_code="USER_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )

        otp = str(random.randint(100000, 999999))
        valid_until = timezone.now() + timedelta(minutes=5)

        # SESSION DEBUG
        print(f"[DEBUG] Setting session for OTP. Session key: {request.session.session_key}")

        request.session['otp'] = otp
        request.session['otp_valid_until'] = valid_until.isoformat()
        request.session['phone_number'] = phone_number
        request.session.modified = True

        print(f"[DEBUG] OTP Stored: {request.session['otp']}")
        print(f"[DEBUG] OTP Valid Until: {request.session['otp_valid_until']}")
        print(f"[DEBUG] Phone Number: {request.session['phone_number']}")

        config_values = {
            config.config: config.value
            for config in Configuration.objects.filter(config__in=["enable-emailotp", "enable-smsotp"])
        }
        enable_email = config_values.get("enable-emailotp", "false").lower() in ("true", "1", "yes")
        enable_sms = config_values.get("enable-smsotp", "false").lower() in ("true", "1", "yes")

        if enable_email:
            self.send_otp_via_email(user.email, otp)
        if enable_sms:
            self.send_otp_via_sms(phone_number, otp)

        return self._success_response(
            message="OTP sent successfully.",
            data={"valid_for_minutes": 5}
        )

    def send_otp_via_email(self, email, otp):
        """
        Send OTP via email to the user.
        """
        subject = f"OTP for {getattr(settings, 'SITE_NAME', 'Your Site')}"
        body = (
            f"Dear User,\n\n"
            f"Your OTP for logging in to {getattr(settings, 'SITE_NAME', 'the site')} is:\n\n"
            f"OTP: {otp}\n\n"
            f"This OTP is valid for 5 minutes.\n\n"
            f"Best regards,\n{getattr(settings, 'SITE_NAME', 'Your Site')} Team"
        )
        send_mail(
            subject, body,
            getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            [email], fail_silently=True
        )

    def send_otp_via_sms(self, phone_number, otp):
        """
        Simulate sending OTP via SMS (implement with service like Twilio).
        """
        try:
            # Uncomment and configure to enable actual SMS sending:
            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # client.messages.create(
            #     body=f"Your OTP is: {otp}. Valid for 5 minutes.",
            #     from_=settings.TWILIO_PHONE_NUMBER,
            #     to=phone_number
            # )
            print(f"[DEBUG] (SMS) Would send OTP {otp} to {phone_number}")
        except Exception as exc:
            print("SMS sending error:", exc)

    def _success_response(self, message, data=None, status_code=status.HTTP_200_OK):
        """
        Standard method for sending success response.
        """
        return Response({
            "success": True,
            "message": message,
            "data": data or {}
        }, status=status_code)

    def _error_response(self, message, error_code=None, status_code=status.HTTP_400_BAD_REQUEST):
        """
        Standard method for sending error response.
        """
        return Response({
            "success": False,
            "message": message,
            "error_code": error_code or "UNKNOWN_ERROR"
        }, status=status_code)


class VerifyOTPAPIView(APIView):
    """
    Verifies user's OTP from session against input,
    activates session and logs in the user.
    """
    def post(self, request):
        """
        Handle POST request for OTP verification.
        """
        user_otp = request.data.get('otp')
        phone_number = request.session.get('phone_number')
        stored_otp = request.session.get('otp')
        otp_valid_until = request.session.get('otp_valid_until')

        # Debug prints
        print(f"[DEBUG] SESSION KEY for verification: {request.session.session_key}")
        print(f"[DEBUG] user_otp: {user_otp}")
        print(f"[DEBUG] phone_number (session): {phone_number}")
        print(f"[DEBUG] stored_otp (session): {stored_otp}")
        print(f"[DEBUG] otp_valid_until (session): {otp_valid_until}")

        if not all([user_otp, stored_otp, otp_valid_until, phone_number]):
            print("[DEBUG] Missing required session/data fields.")
            print(f"[DEBUG] SESSION DUMP: {dict(request.session.items())}")
            return Response(
                {"detail": "Session expired or OTP not sent."},
                status=status.HTTP_400_BAD_REQUEST
            )

        dt = parse_datetime(otp_valid_until)
        print(f"[DEBUG] Parsed datetime: {dt}")
        print(f"[DEBUG] Current time: {timezone.now()}")

        if not dt or timezone.now() > dt:
            print("[DEBUG] OTP expired or invalid datetime.")
            return Response(
                {"detail": "OTP has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user_otp != stored_otp:
            print("[DEBUG] OTP mismatch.")
            return Response(
                {"detail": "Invalid OTP."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            user = User.objects.get(phone_number=phone_number)
            print(f"[DEBUG] User found: {getattr(user, 'member_id', None)} ({user.email})")
        except User.DoesNotExist:
            print("[DEBUG] User not found.")
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        print("[DEBUG] User logged in successfully.")

        # Generate JWT Access Token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        print("[DEBUG] JWT issued.")

        # Clean up OTP/session-related keys, if present.
        for k in ('otp', 'otp_valid_until', 'phone_number'):
            if k in request.session:
                request.session.pop(k, None)
                print(f"[DEBUG] Session key '{k}' cleared after login.")

        print("[DEBUG] Returning login response.")

        # Return the response matching Google/OTP style: just {"key": ...}
        return Response(
            {"key": access_token},
            status=status.HTTP_200_OK
        )




class LoginAPIView(APIView):
    """
    Authenticates user by username/mobile and password, issues JWT.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle POST for traditional username/password login.
        """
        mobile = request.data.get('mobile')
        password = request.data.get('password')

        print(f"[DEBUG] mobile: {mobile}")
        print(f"[DEBUG] password: {password}")
        print(f"[DEBUG] SESSION KEY: {request.session.session_key}")
        print(f"[DEBUG] SESSION DUMP: {dict(request.session.items())}")

        if not mobile or not password:
            print("[DEBUG] Missing mobile or password.")
            return Response(
                {'detail': "Mobile and password required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=mobile, password=password)
        print(f"[DEBUG] User authenticated: {user}")

        if not user:
            print("[DEBUG] Invalid credentials.")
            return Response(
                {'detail': "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            print("[DEBUG] User account is disabled.")
            return Response(
                {'detail': "User account is disabled."},
                status=status.HTTP_403_FORBIDDEN
            )

        login(request, user)
        print("[DEBUG] User logged in successfully.")

        # Generate JWT
        refresh = RefreshToken.for_user(user)
        print("[DEBUG] JWT issued.")

        # Clean up OTP/session keys, if present.
        for k in ('otp', 'otp_valid_until', 'phone_number'):
            if k in request.session:
                request.session.pop(k, None)
                print(f"[DEBUG] Session key '{k}' cleared after login.")

        print("[DEBUG] Returning login response.")

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.pk,
                'mobile': getattr(user, 'mobile', user.username),
                'name': user.get_full_name() or user.username,
                'email': user.email,
            }
        }, status=status.HTTP_200_OK)


class SignOutAPIView(APIView):
    """
    Logs out the current user and clears the session.
    """
    def post(self, request):
        """
        POST to logout and clear session for current user.
        """
        print(f"[DEBUG] Logging out user: {request.user}")

        logout(request)
        request.session.flush()
        print("[DEBUG] User logged out. Session cleared.")

        return Response({"detail": "Signed out successfully."}, status=status.HTTP_200_OK)




class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = "http://localhost:8000/accounts/google/login/callback/"



from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response

class CustomGoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

    def get_response(self):
        response = super().get_response()
        user = self.user

        # Generate JWT tokens for the user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Add extra data to the response JSON
        extra_data = {
            "access": access_token,
            "refresh": refresh_token,
            "user": {
                "id": user.pk,
                "email": user.email,
                "name": user.get_full_name() or user.username,
                "staff_role": getattr(user, "staff_role", None),
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            },
        }

        response.data.update(extra_data)
        return response



from datetime import date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get today's date inside the method
        today = date.today()
        user = request.user  # The authenticated user
        Vendor = getattr(user, 'Vendor', None)

        # Get latest measurement for this user (any date), if present
        latest = (
            BodyMeasurement.objects
            .filter(user=user)
            .order_by('-date', '-id')
            .first()
        )

        # Fixed: Use the local 'today' variable
        log_status = Attendance.objects.filter(user=user, date=today).exists()

        latest_measurement = None
        if latest:
            latest_measurement = {
                "date": latest.date.isoformat(),
                "height_cm": float(latest.height_cm) if latest.height_cm is not None else None,
                "weight_kg": float(latest.weight_kg) if latest.weight_kg is not None else None,
                "bmi": float(latest.bmi) if latest.bmi is not None else None,
                "year": latest.year,
                "week_of_year": latest.week_of_year,
                "week_index_since_join": latest.week_index_since_join,
            }

        data = {
            "avatar_url": user.avatar.url if hasattr(user, 'avatar') and user.avatar else None,
            "name": user.get_full_name() or user.username,
            "email": user.email,
            "member_id": user.member_id,
            "gender": getattr(user, 'gender', None),
            "phone": getattr(user, 'phone_number', '') or '',
            "vendor_name": getattr(Vendor, 'name', '') or '',
            "location": getattr(Vendor, 'location', '') or '',
            "status": getattr(user, 'on_subscription', ''),
            "is_active": getattr(user, 'is_active', ''),
            "log_status": log_status,  # Fixed: Use actual log_status variable
            "package_expiry_date": user.package_expiry_date.isoformat() if getattr(user, 'package_expiry_date', None) else "",
            "package": getattr(getattr(user, 'package', None), 'name', '') or "",

            # Latest body measurement snapshot (if any)
            "latest_measurement": latest_measurement,

            # Optionally expose convenience top-level fields for Flutter grid:
            "height": latest_measurement["height_cm"] if latest_measurement else None,
            "weight": latest_measurement["weight_kg"] if latest_measurement else None,
            "bmi_value": latest_measurement["bmi"] if latest_measurement else None,
        }

        return Response(data)





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models.functions import ExtractWeek, ExtractYear
from health.serializers import BodyMeasurementTodaySerializer
from health.models import BodyMeasurement
import logging

logger = logging.getLogger(__name__)

class MeasurementTodayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        today = timezone.localdate()
        user = request.user

        height = request.data.get('height_cm')
        weight = request.data.get('weight_kg')

        logger.info(f"[POST /api/measurements/week/] User={getattr(user, 'member_id', user.member_id)} ({user}), Date={today}")
        logger.info(f"📥 Incoming data: height_cm={height}, weight_kg={weight}")

        # Validate and convert numeric types
        if height is not None:
            try:
                height = float(height)
                if height <= 0:
                    return Response(
                        {"height_cm": "Height must be greater than 0."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except (ValueError, TypeError):
                return Response(
                    {"height_cm": "Must be a valid number."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        if weight is not None:
            try:
                weight = float(weight)
                if weight <= 0:
                    return Response(
                        {"weight_kg": "Weight must be greater than 0."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except (ValueError, TypeError):
                return Response(
                    {"weight_kg": "Must be a valid number."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Current week and year
        current_week = today.isocalendar()[1]
        current_year = today.year

        try:
            # 1️⃣ Try to get an existing instance in the same week/year
            # Use different annotation names to avoid conflicts with model fields
            instance = (
                BodyMeasurement.objects
                .annotate(
                    week_num=ExtractWeek('date'), 
                    year_num=ExtractYear('date')
                )
                .filter(user=user, week_num=current_week, year_num=current_year)
                .first()
            )

            if instance:
                logger.info(f"ℹ Updating existing record ID={instance.id} for week={current_week}, year={current_year}.")
                
                # Update only provided fields
                updated_fields = []
                if height is not None:
                    instance.height_cm = height
                    updated_fields.append('height_cm')
                if weight is not None:
                    instance.weight_kg = weight
                    updated_fields.append('weight_kg')
                
                if updated_fields:
                    instance.save(update_fields=updated_fields + ['updated_at'] if hasattr(instance, 'updated_at') else updated_fields)
                
                return Response(
                    BodyMeasurementTodaySerializer(instance).data,
                    status=status.HTTP_200_OK
                )

            # 2️⃣ No entry for this week — check if we need fallback values
            if height is None or weight is None:
                last_measurement = BodyMeasurement.objects.filter(user=user).order_by('-date').first()
                if last_measurement:
                    logger.info(f"ℹ Using last measurement as fallback: height_cm={last_measurement.height_cm}, weight_kg={last_measurement.weight_kg}")
                    if height is None:
                        height = last_measurement.height_cm
                    if weight is None:
                        weight = last_measurement.weight_kg
                else:
                    logger.warning("❌ No previous measurements found for fallback")

            # Still missing required values?
            if height is None or weight is None:
                logger.error("❌ Cannot create measurement — missing both current and fallback values")
                return Response(
                    {
                        "detail": "Both height_cm and weight_kg are required for your first measurement.",
                        "missing_fields": [
                            field for field, value in [("height_cm", height), ("weight_kg", weight)] 
                            if value is None
                        ]
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 3️⃣ Create new measurement with validated values
            instance = BodyMeasurement.objects.create(
                user=user, 
                date=today, 
                height_cm=height, 
                weight_kg=weight
            )
            
            logger.info(f"✅ Created new record ID={instance.id} for week={current_week}, year={current_year}.")

            return Response(
                BodyMeasurementTodaySerializer(instance).data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"❌ Unexpected error in MeasurementTodayView: {e}", exc_info=True)
            return Response(
                {"detail": "An error occurred while processing your measurement."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request):
        """Get today's or current week's measurement"""
        try:
            user = request.user
            today = timezone.localdate()
            current_week = today.isocalendar()[1]
            current_year = today.year

            # Try to get measurement for current week
            measurement = (
                BodyMeasurement.objects
                .annotate(
                    week_num=ExtractWeek('date'), 
                    year_num=ExtractYear('date')
                )
                .filter(user=user, week_num=current_week, year_num=current_year)
                .first()
            )

            if measurement:
                return Response(
                    BodyMeasurementTodaySerializer(measurement).data,
                    status=status.HTTP_200_OK
                )

            # No measurement for this week, get the most recent one
            last_measurement = BodyMeasurement.objects.filter(user=user).order_by('-date').first()
            
            if last_measurement:
                return Response(
                    {
                        **BodyMeasurementTodaySerializer(last_measurement).data,
                        "is_current_week": False,
                        "message": "No measurement for current week, showing most recent."
                    },
                    status=status.HTTP_200_OK
                )

            # No measurements at all
            return Response(
                {
                    "detail": "No measurements found. Please add your first measurement.",
                    "has_measurements": False
                },
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            logger.error(f"❌ Error getting measurement: {e}", exc_info=True)
            return Response(
                {"detail": "An error occurred while retrieving measurement."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models.functions import ExtractWeek, ExtractYear
from health.models import BodyMeasurement

class MeasurementProgressView(APIView):
    """
    Returns all measurements for the logged-in user,
    grouped by week, ordered by date, for graph display.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        measurements = (
            BodyMeasurement.objects
            .filter(user=user)
            .annotate(week_num=ExtractWeek('date'), year_num=ExtractYear('date'))
            .order_by('year_num', 'week_num')
            .values('date', 'week_num', 'year_num', 'height_cm', 'weight_kg', 'bmi')
        )

        data = [
            {
                "date": m["date"],
                "week": m["week_num"],
                "year": m["year_num"],
                "height_cm": float(m["height_cm"]) if m["height_cm"] else None,
                "weight_kg": float(m["weight_kg"]) if m["weight_kg"] else None,
                "bmi": float(m["bmi"]) if m["bmi"] else None,
            }
            for m in measurements
        ]
        print("datadatadata", data)
        return Response({"progress": data}, status=status.HTTP_200_OK)



# workout/api_views.py
from django.utils import timezone
from datetime import datetime, timedelta
from workout.models import UserWorkoutAssignment, DayTemplate
from workout.serializers import UserWorkoutAssignmentSerializer, DayTemplateSerializer
import calendar

class TodayWorkoutAPIView(APIView):
    """API to get today's workout for the authenticated user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            today = timezone.now().date()

            day_name = calendar.day_name[today.weekday()].lower()
            
            # Get user's active assignments
            assignments = UserWorkoutAssignment.objects.filter(
                user=request.user,
                status='assigned',
                start_date__lte=today
            ).select_related('weekly_template').prefetch_related(
                'weekly_template__day_templates__activities__exercise__equipment'
            )
            
            if not assignments.exists():
                return Response({
                    'status': 'success',
                    'message': 'No active workout assignments found',
                    'data': {
                        'today': str(today),
                        'day_name': day_name.title(),
                        'workouts': []
                    }
                })
            
            today_workouts = []

            
            for assignment in assignments:
                # Find today's workout
                try:
                    day_template = assignment.weekly_template.day_templates.get(day=day_name)
                    
                    workout_data = {
                        'assignment_id': assignment.id,
                        'template_name': assignment.weekly_template.name,
                        'trainer_name': assignment.weekly_template.trainer.get_full_name() or assignment.weekly_template.trainer.username,
                        'day_template': DayTemplateSerializer(day_template).data,
                        'program_info': {
                            'fitness_level': assignment.weekly_template.fitness_level.get_name_display(),
                            'goal': assignment.weekly_template.goal.get_name_display(),
                            'total_sessions_per_week': assignment.weekly_template.total_sessions_per_week,
                            'estimated_duration': assignment.weekly_template.estimated_duration_per_session
                        }
                    }
                    today_workouts.append(workout_data)
                    
                except DayTemplate.DoesNotExist:
                    # No workout scheduled for today in this template
                    continue
            
            return Response({
                'status': 'success',
                'data': {
                    'today': str(today),
                    'day_name': day_name.title(),
                    'workouts': today_workouts,
                    'total_workouts': len(today_workouts)
                }
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpcomingWorkoutsAPIView(APIView):
    """API to get upcoming workouts for the next 7 days"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            today = timezone.now().date()
            next_7_days = [today + timedelta(days=i) for i in range(1, 8)]
            
            # Get user's active assignments
            assignments = UserWorkoutAssignment.objects.filter(
                user=request.user,
                status='assigned',
                start_date__lte=today
            ).select_related('weekly_template').prefetch_related(
                'weekly_template__day_templates__activities__exercise__equipment'
            )
            if not assignments.exists():
                return Response({
                    'status': 'success',
                    'message': 'No active workout assignments found',
                    'data': {
                        'upcoming_workouts': []
                    }
                })
            
            upcoming_workouts = []
            for future_date in next_7_days:
                day_name = calendar.day_name[future_date.weekday()].lower()
                day_workouts = []
                
                for assignment in assignments:
                    try:
                        day_template = assignment.weekly_template.day_templates.get(day=day_name)
                        
                        workout_data = {
                            'assignment_id': assignment.id,
                            'template_name': assignment.weekly_template.name,
                            'trainer_name': assignment.weekly_template.trainer.get_full_name() or assignment.weekly_template.trainer.username,
                            'day_template': DayTemplateSerializer(day_template).data,
                            'program_info': {
                                'fitness_level': assignment.weekly_template.fitness_level.get_name_display(),
                                'goal': assignment.weekly_template.goal.get_name_display(),
                            }
                        }
                        day_workouts.append(workout_data)
                        
                    except DayTemplate.DoesNotExist:
                        continue
                
                if day_workouts:  # Only add days that have workouts
                    upcoming_workouts.append({
                        'date': str(future_date),
                        'day_name': day_name.title(),
                        'workouts': day_workouts,
                        'total_workouts': len(day_workouts)
                    })

            
            return Response({
                'status': 'success',
                'data': {
                    'upcoming_workouts': upcoming_workouts,
                    'total_days': len(upcoming_workouts)
                }
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WeeklyWorkoutScheduleAPIView(APIView):
    """API to get complete weekly workout schedule"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            today = timezone.now().date()

            
            # Get user's active assignments
            assignments = UserWorkoutAssignment.objects.filter(
                user=request.user,
                status='assigned',
                start_date__lte=today
            ).select_related('weekly_template').prefetch_related(
                'weekly_template__day_templates__activities__exercise__equipment'
            )
            
            if not assignments.exists():
                return Response({
                    'status': 'success',
                    'message': 'No active workout assignments found',
                    'data': {
                        'assignments': []
                    }
                })
            
            assignments_data = []


            
            for assignment in assignments:
                # Get all day templates for this assignment
                day_templates = assignment.weekly_template.day_templates.all().order_by('day')
                
                assignment_data = {
                    'assignment_id': assignment.id,
                    'template_name': assignment.weekly_template.name,
                    'description': assignment.weekly_template.description,
                    'trainer_name': assignment.weekly_template.trainer.get_full_name() or assignment.weekly_template.trainer.username,
                    'start_date': str(assignment.start_date),
                    'status': assignment.status,
                    'program_info': {
                        'fitness_level': assignment.weekly_template.fitness_level.get_name_display(),
                        'goal': assignment.weekly_template.goal.get_name_display(),
                        'total_sessions_per_week': assignment.weekly_template.total_sessions_per_week,
                        'estimated_duration': assignment.weekly_template.estimated_duration_per_session
                    },
                    'weekly_schedule': DayTemplateSerializer(day_templates, many=True).data
                }
                assignments_data.append(assignment_data)
            
            return Response({
                'status': 'success',
                'data': {
                    'assignments': assignments_data,
                    'total_assignments': len(assignments_data),
                    'today': str(today)
                }
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib.contenttypes.models import ContentType
from datetime import timedelta
import json
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_subscription_payment_api(request):
    """
    API endpoint to initiate Vendor membership subscription payment from Flutter app.
    Creates necessary database entries before Cashfree payment processing.
    
    Expected payload:
    {
        "member_id": "string",
        "package_id": "integer"
    }
    """
    try:
        # Get data from request
        member_id = request.data.get('member_id')
        package_id = request.data.get('package_id')
        
        # Validate required fields
        if not member_id or not package_id:
            return Response({
                'success': False,
                'message': 'Missing member_id or package_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user and package objects
        user = get_object_or_404(User, member_id=member_id)
        package = get_object_or_404(Package, id=package_id)
        
        # Create subscription order
        subscription_order = SubscriptionOrder.objects.create(
            customer=user,
            package=package,
            total=package.final_price,
            status=SubscriptionOrder.Status.PENDING,
            payment_status=SubscriptionOrder.PaymentStatus.PENDING,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=package.duration_days),
            Vendor=request.user.vendor
        )
        
        # Create payment record
        payment, created = Payment.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(subscription_order),
            object_id=subscription_order.id,
            Vendor=request.user.vendor,
            defaults={
                'payment_method': 'cashfree',
                'amount': subscription_order.total,
                'status': Payment.Status.PENDING,
                'customer': user,
            }
        )
        
        if not created:
            payment.payment_method = 'cashfree'
            payment.amount = subscription_order.total
            payment.status = Payment.Status.PENDING
            payment.customer = user
            payment.save()
        
        # Prepare response data for Flutter
        response_data = {
            'success': True,
            'subscription_order': {
                'id': subscription_order.id,
                'order_number': subscription_order.order_number,
                'total': float(subscription_order.total),
                'customer_name': user.get_full_name() or user.username,
                'customer_email': user.email,
                'customer_phone': getattr(user, 'phone_number', ''),
            },
            'payment': {
                'id': payment.id,
                'amount': float(payment.amount),
                'status': payment.status
            }
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Package.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Package not found'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"Error in initiate_subscription_payment_api: {str(e)}")
        return Response({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_payment_status_api(request):
    """
    API endpoint to update payment status after successful payment from Flutter app.
    
    Expected payload:
    {
        "order_id": "string",
        "payment_status": "SUCCESS" | "FAILED",
        "transaction_id": "string",
        "payment_method": "string",
        "gateway_response": {} // optional
    }
    """
    try:
        order_id = request.data.get('order_id')
        payment_status = request.data.get('payment_status')
        transaction_id = request.data.get('transaction_id')
        payment_method = request.data.get('payment_method', 'cashfree')
        gateway_response = request.data.get('gateway_response', {})
        
        # Validate required fields
        if not order_id or not payment_status:
            return Response({
                'success': False,
                'message': 'Missing order_id or payment_status'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find the subscription order
        subscription_order = get_object_or_404(SubscriptionOrder, order_number=order_id)
        
        # Find the payment record
        payment = Payment.objects.filter(
            content_type=ContentType.objects.get_for_model(subscription_order),
            object_id=subscription_order.id
        ).first()
        
        if not payment:
            return Response({
                'success': False,
                'message': 'Payment record not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Update payment record
        if transaction_id:
            payment.transaction_id = transaction_id
        payment.gateway_response = gateway_response
        
        if payment_status.upper() == 'SUCCESS':
            # Update payment status
            payment.status = Payment.Status.COMPLETED
            
            # Update subscription order
            subscription_order.status = SubscriptionOrder.Status.ACTIVE
            subscription_order.payment_status = SubscriptionOrder.PaymentStatus.COMPLETED
            
            # Update user subscription details
            user = subscription_order.customer
            package = subscription_order.package
            today = timezone.now().date()
            
            # Handle stacked subscriptions
            cur_expiry = getattr(user, "package_expiry_date", None)
            if cur_expiry and cur_expiry >= today:
                user.package_expiry_date = cur_expiry + timedelta(days=package.duration_days)
            else:
                user.package_expiry_date = today + timedelta(days=package.duration_days)
            
            user.package = package
            user.on_subscription = True
            user.save(update_fields=['package_expiry_date', 'package', 'on_subscription'])
            
            # Update subscription order dates
            subscription_order.start_date = today
            subscription_order.end_date = user.package_expiry_date
            subscription_order.save(update_fields=['start_date', 'end_date', 'status', 'payment_status'])
            
            payment.save(update_fields=['status', 'gateway_response', 'transaction_id'])
            
            response_data = {
                'success': True,
                'message': 'Payment updated successfully',
                'subscription': {
                    'status': subscription_order.status,
                    'start_date': subscription_order.start_date.isoformat(),
                    'end_date': subscription_order.end_date.isoformat(),
                    'package_name': package.name
                }
            }
            
        elif payment_status.upper() == 'FAILED':
            payment.status = Payment.Status.FAILED
            subscription_order.payment_status = SubscriptionOrder.PaymentStatus.FAILED
            subscription_order.status = SubscriptionOrder.Status.CANCELLED
            
            payment.save(update_fields=['status', 'gateway_response'])
            subscription_order.save(update_fields=['payment_status', 'status'])
            
            response_data = {
                'success': True,
                'message': 'Payment failure recorded',
                'subscription': {
                    'status': subscription_order.status,
                }
            }
        
        else:
            return Response({
                'success': False,
                'message': 'Invalid payment status'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except SubscriptionOrder.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Subscription order not found'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"Error in update_payment_status_api: {str(e)}")
        return Response({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_status_api(request, order_id):
    """
    API endpoint to get payment status for a specific order.
    """
    try:
        subscription_order = get_object_or_404(SubscriptionOrder, order_number=order_id)
        
        payment = Payment.objects.filter(
            content_type=ContentType.objects.get_for_model(subscription_order),
            object_id=subscription_order.id
        ).first()
        
        response_data = {
            'success': True,
            'order': {
                'order_id': subscription_order.order_number,
                'status': subscription_order.status,
                'payment_status': subscription_order.payment_status,
                'total': float(subscription_order.total),
                'start_date': subscription_order.start_date.isoformat() if subscription_order.start_date else None,
                'end_date': subscription_order.end_date.isoformat() if subscription_order.end_date else None,
            },
            'payment': {
                'status': payment.status if payment else None,
                'transaction_id': payment.transaction_id if payment else None,
                'amount': float(payment.amount) if payment else None,
            } if payment else None
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except SubscriptionOrder.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Order not found'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"Error in get_payment_status_api: {str(e)}")
        return Response({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.contrib.contenttypes.models import ContentType
from payments.models import Transaction  # Add this import

@csrf_exempt
def cashfree_webhook(request):
    """
    Handles Cashfree webhook events for payment and refund status updates.
    Updates both Payment and Transaction records.
    """
    from payments.models import Transaction
    
    try:
        data = json.loads(request.body)
        event_type = data.get("type")
        link_id = None
        payment_status = None

        # Extract link_id and payment_status based on event type
        if event_type == "PAYMENT_SUCCESS_WEBHOOK":
            order_data = data.get('data', {}).get('order', {})
            payment_data = data.get('data', {}).get('payment', {})
            link_id = order_data.get('order_tags', {}).get('link_id')
            payment_status = payment_data.get('payment_status')
        elif event_type == "PAYMENT_LINK_EVENT":
            order_data = data.get('data', {}).get('order', {})
            link_id = data.get('data', {}).get('link_id')
            payment_status = data.get('data', {}).get('link_status')
        elif event_type == "PAYMENT_CHARGES_WEBHOOK":
            order_data = data.get('data', {}).get('order', {})
            link_id = order_data.get('order_tags', {}).get('link_id')
        else:
            link_id = None

        payment = Payment.objects.filter(transaction_id=link_id).first()
        log_entry = PaymentAPILog.objects.create(
            Vendor=payment.Vendor if payment else None,
            action='WEBHOOK',
            request_url=request.path,
            response_body=request.body.decode('utf-8') if request.body else None,
            response_status=0
        )

        if request.method != 'POST':
            log_entry.error_message = "Invalid method"
            log_entry.response_status = 405
            log_entry.save()
            return JsonResponse({'error': 'Invalid method'}, status=405)

        if not link_id:
            error_msg = 'Missing link_id'
            log_entry.error_message = error_msg
            log_entry.response_status = 400
            log_entry.save()
            return JsonResponse({'error': error_msg}, status=400)

        payment = Payment.objects.filter(transaction_id=link_id).first()
        if not payment:
            error_msg = f'Payment not found for link_id: {link_id}'
            log_entry.error_message = error_msg
            log_entry.response_status = 404
            log_entry.save()
            return JsonResponse({'error': error_msg}, status=404)

        order = payment.content_object
        payment.gateway_response = data

        # Get related transaction
        transaction = Transaction.objects.filter(
            content_type=payment.content_type,
            object_id=payment.object_id,
            Vendor=payment.Vendor
        ).first()

        if (
            (event_type == "PAYMENT_SUCCESS_WEBHOOK" and payment_status == "SUCCESS") or
            (event_type == "PAYMENT_LINK_EVENT" and payment_status == "PAID")
        ):
            payment.status = Payment.Status.COMPLETED

            # Update Transaction status to COMPLETED
            if transaction:
                transaction.status = Transaction.Status.COMPLETED
                transaction.description = f"Payment completed for {order.__class__.__name__} #{order.order_number if hasattr(order, 'order_number') else order.id}"
                transaction.save(skip_auto_status=True)  # Skip automatic status setting
                print(f"Transaction {transaction.id} updated to COMPLETED")


            # Update user subscription and order status
            if hasattr(order, 'customer') and isinstance(order, SubscriptionOrder):
                user = order.customer
                package = order.package
                today = timezone.now().date()

                cur_expiry = getattr(user, "package_expiry_date", None)
                if cur_expiry and cur_expiry >= today:
                    user.package_expiry_date = cur_expiry + timedelta(days=package.duration_days)
                else:
                    user.package_expiry_date = today + timedelta(days=package.duration_days)
                user.package = package
                user.on_subscription = True
                user.save(update_fields=['package_expiry_date', 'package', 'on_subscription'])

                order.start_date = today
                order.end_date = user.package_expiry_date
                order.status = SubscriptionOrder.Status.ACTIVE
                order.payment_status = SubscriptionOrder.PaymentStatus.COMPLETED
                order.save(update_fields=['start_date', 'end_date', 'status', 'payment_status'])

            elif hasattr(order, 'customer') and isinstance(order, Order):
                order.status = Order.Status.PROCESSING
                order.payment_status = 'completed'
                order.save(update_fields=['status', 'payment_status'])

            payment.save(update_fields=['status', 'gateway_response'])

        elif event_type == "PAYMENT_LINK_EVENT" and payment_status in ['EXPIRED', 'FAILED']:
            payment.status = Payment.Status.FAILED
            
            # Update Transaction status to FAILED (you might want to add this status to your choices)
            if transaction:
                transaction.status = Transaction.Status.INITIATED  # or add FAILED status
                transaction.description = f"Payment failed for {order.__class__.__name__} #{order.order_number if hasattr(order, 'order_number') else order.id} - Status: {payment_status}"
                transaction.save()
                print(f"Transaction {transaction.id} updated to FAILED")
                
            if hasattr(order, 'payment_status'):
                order.payment_status = 'failed'
                order.save(update_fields=['payment_status'])
            payment.save(update_fields=['status'])

        log_entry.response_status = 200
        log_entry.response_body = json.dumps({
            'status': 'success',
            'event_type': event_type
        })
        log_entry.link_id = link_id
        log_entry.save()

        return HttpResponse(status=200)

    except Exception as e:
        error_msg = str(e)
        if 'log_entry' in locals():
            log_entry.error_message = error_msg
            log_entry.response_status = 500
            log_entry.save()
        return HttpResponse(status=200)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import UserFCMToken
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class UpdateFCMTokenView(APIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]  # Support both
    permission_classes = [IsAuthenticated]

    def post(self, request):
        fcm_token = request.data.get('fcm_token')
        if not fcm_token:
            return Response({"error": "FCM token is required"}, status=400)

        try:
            user_id = getattr(request.user, 'id', None) or getattr(request.user, 'member_id', None) or request.user.pk
            
            obj, created = UserFCMToken.objects.update_or_create(
                user=request.user,
                defaults={
                    'fcm_token': fcm_token,
                    'updated_at': timezone.now()
                }
            )
            
            action = "created" if created else "updated"
            logger.info(f"FCM token {action} for user {user_id}")
            
            return Response({
                "status": f"FCM token {action}",
                "user_id": user_id
            })
            
        except Exception as e:
            logger.error(f"Error updating FCM token: {str(e)}")
            return Response({"error": "Failed to update FCM token"}, status=500)

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from products.models import Package
from products.serializers import PackageSerializer

class PackageListAPI(generics.ListAPIView):
    """
    API to fetch all packages for the authenticated user's Vendor
    ordered by price in ascending order
    """
    serializer_class = PackageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # Get user's Vendor - adjust this based on your User-Vendor relationship
        Vendor = getattr(user, 'Vendor', None)
        
        if not Vendor:
            return Package.objects.none()
        
        return Package.objects.filter(
            vendor_id=Vendor.id,
            is_active=True  # Only return active packages
        ).order_by('price')  # Ascending order by price

    def list(self, request, *args, **kwargs):
        """
        Override list method to add custom response format
        """
        queryset = self.get_queryset()
        
        # Check if user has Vendor
        user = request.user
        Vendor = getattr(user, 'Vendor', None)
        
        if not Vendor:
            return Response(
                {'detail': 'User is not associated with any Vendor'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Apply pagination if configured
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            # Add custom fields to paginated response
            result.data['vendor_name'] = Vendor.name
            result.data['vendor_id'] = Vendor.id
            return result

        # Non-paginated response
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'vendor_name': Vendor.name,
            'vendor_location': Vendor.location,
            'vendor_id': Vendor.id,
            'packages': serializer.data
        })


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models.query import QuerySet
# from django.utils.timezone import datetime, date
from django.core.serializers.json import DjangoJSONEncoder
import json

class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def _make_serializable(self, value):
        """
        Convert complex Django objects in context to JSON serializable formats.
        """
        if isinstance(value, QuerySet):
            # Convert QuerySet to list of dicts
            return list(value.values())
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, dict):
            # Recursively convert dict values
            return {k: self._make_serializable(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._make_serializable(v) for v in value]
        # Add other conversions if needed (e.g., model instances)
        # Fallback: try JSON serialization via DjangoJSONEncoder
        try:
            json.dumps(value, cls=DjangoJSONEncoder)
            return value
        except TypeError:
            return str(value)  # fallback to string
        return value

    def get(self, request, *args, **kwargs):
        dashboard_view = DashboardView()
        dashboard_view.request = request
        dashboard_view.args = args
        dashboard_view.kwargs = kwargs

        context = dashboard_view.get_context_data()

        # Remove irrelevant template keys
        context.pop('page_name', None)
        context.pop('pages_group', None)

        # Clean context to make everything JSON serializable
        serializable_context = {}
        for key, value in context.items():
            serializable_context[key] = self._make_serializable(value)


        print("Dashboard context data:----------------", serializable_context)

        return Response(serializable_context)

# views.py
from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFromToRangeFilter
from django_filters import CharFilter, ChoiceFilter, NumberFilter
from django.db.models import Q, Sum
from payments.models import Transaction
from .serializers import TransactionSerializer
from .permissions import IsAdminStaff

class TransactionFilter(FilterSet):
    """Custom filter class for Transaction model"""
    
    date_range = DateFromToRangeFilter(field_name='date')
    transaction_type = ChoiceFilter(choices=TransactionTypeChoice)
    category = ChoiceFilter(choices=TransactionCategoryChoice)
    status = ChoiceFilter(choices=TransactionCategoryChoice)
    amount_min = NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = NumberFilter(field_name='amount', lookup_expr='lte')
    reference = CharFilter(lookup_expr='icontains')
    description = CharFilter(lookup_expr='icontains')
    
    # Customer Information Filters
    customer_name = CharFilter(lookup_expr='icontains', help_text="Filter by customer name")
    customer_email = CharFilter(lookup_expr='icontains', help_text="Filter by customer email")
    customer_phone = CharFilter(lookup_expr='icontains', help_text="Filter by customer phone")
    
    class Meta:
        model = Transaction
        fields = [
            'transaction_type', 'category', 'status', 'date_range', 
            'reference', 'description', 'customer_name', 'customer_email', 'customer_phone'
        ]

class TransactionPagination(PageNumberPagination):
    """Custom pagination for transactions"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class TransactionListAPIView(generics.ListAPIView):
    """
    API endpoint for fetching transactions with filtering and search.
    Only accessible by Admin staff users.
    """
    
    serializer_class = TransactionSerializer
    permission_classes = [IsAdminStaff]
    pagination_class = TransactionPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TransactionFilter
    
    # Fixed search fields - removed GenericForeignKey references
    search_fields = [
        'description', 'reference', 'customer_name', 'customer_email', 'customer_phone'
    ]
    
    # Updated ordering fields to include customer fields
    ordering_fields = [
        'date', 'created_at', 'amount', 'transaction_type', 'category', 'status',
        'customer_name', 'customer_email'
    ]
    ordering = ['-created_at']  # Default ordering by latest first
    
    def get_queryset(self):
        """
        Filter transactions by user's Vendor and optimize queries
        """
        user = self.request.user
        
        # Get Vendor from user (adjust field name as per your User model)
        Vendor = None
        if hasattr(user, 'Vendor'):
            Vendor = user.vendor
        elif hasattr(user, 'vendor_id'):
            vendor_id = user.vendor_id
            return Transaction.objects.filter(vendor_id=vendor_id).select_related('Vendor', 'content_type').prefetch_related('content_object')
        
        if not Vendor:
            # Return empty queryset if no Vendor found
            return Transaction.objects.none()
        
        return Transaction.objects.filter(Vendor=Vendor).select_related('Vendor', 'content_type').prefetch_related('content_object')
    
    def filter_queryset(self, queryset):
        """
        Override to add custom search logic for GenericForeignKey content
        """
        queryset = super().filter_queryset(queryset)
        
        # Handle search parameter manually to include content_object fields
        search_param = self.request.query_params.get('search', None)
        if search_param:
            # Create Q object for searching across multiple fields including content_object
            search_query = Q(
                Q(description__icontains=search_param) |
                Q(reference__icontains=search_param) |
                Q(customer_name__icontains=search_param) |
                Q(customer_email__icontains=search_param) |
                Q(customer_phone__icontains=search_param)
            )
            
            # Search in related objects manually
            from subscriptions.models import SubscriptionOrder  # Import your models
            from orders.models import Order  # Import your models
            
            # Get IDs of subscription orders that match search
            try:
                subscription_order_ids = SubscriptionOrder.objects.filter(
                    Q(customer__name__icontains=search_param) |
                    Q(customer__email__icontains=search_param) |
                    Q(customer__username__icontains=search_param) |
                    Q(order_number__icontains=search_param)
                ).values_list('id', flat=True)
                
                if subscription_order_ids:
                    from django.contrib.contenttypes.models import ContentType
                    subscription_ct = ContentType.objects.get_for_model(SubscriptionOrder)
                    search_query |= Q(
                        content_type=subscription_ct,
                        object_id__in=subscription_order_ids
                    )
            except Exception as e:
                print(f"Error searching subscription orders: {e}")
            
            # Get IDs of orders that match search (if you have Order model)
            try:
                order_ids = Order.objects.filter(
                    Q(customer__name__icontains=search_param) |
                    Q(customer__email__icontains=search_param) |
                    Q(customer__username__icontains=search_param) |
                    Q(order_number__icontains=search_param)
                ).values_list('id', flat=True)
                
                if order_ids:
                    from django.contrib.contenttypes.models import ContentType
                    order_ct = ContentType.objects.get_for_model(Order)
                    search_query |= Q(
                        content_type=order_ct,
                        object_id__in=order_ids
                    )
            except Exception as e:
                print(f"Error searching orders: {e}")
            
            queryset = queryset.filter(search_query)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        Override list method to add additional response data
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Add summary statistics
        total_income = queryset.filter(
            transaction_type=Transaction.Type.INCOME,
            status=Transaction.Status.COMPLETED
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_expense = queryset.filter(
            transaction_type=Transaction.Type.EXPENSE
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Customer statistics
        unique_customers = queryset.exclude(
            customer_email__isnull=True
        ).exclude(
            customer_email__exact=''
        ).values('customer_email').distinct().count()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            
            # Add summary to paginated response
            response.data['summary'] = {
                'total_income': float(total_income),
                'total_expense': float(total_expense),
                'net_amount': float(total_income - total_expense),
                'total_transactions': queryset.count(),
                'unique_customers': unique_customers
            }
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'summary': {
                'total_income': float(total_income),
                'total_expense': float(total_expense),
                'net_amount': float(total_income - total_expense),
                'total_transactions': queryset.count(),
                'unique_customers': unique_customers
            }
        })
