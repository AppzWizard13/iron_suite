from datetime import timedelta
import random
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
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




class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # The authenticated user
        gym = getattr(user, 'gym', None)

        # Get latest measurement for this user (any date), if present
        latest = (
            BodyMeasurement.objects
            .filter(user=user)
            .order_by('-date', '-id')
            .first()
        )

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
            "gender": getattr(user, 'gender', None),
            "phone": getattr(user, 'phone_number', '') or '',
            "gym_name": getattr(gym, 'name', '') or '',
            "location": getattr(gym, 'location', '') or '',
            "status": getattr(user, 'on_subscription', ''),
            "package_expiry_date": user.package_expiry_date.isoformat() if getattr(user, 'package_expiry_date', None) else "",
            "package": getattr(getattr(user, 'package', None), 'name', '') or "",

            # Latest body measurement snapshot (if any)
            "latest_measurement": latest_measurement,

            # Optionally expose convenience top-level fields for Flutter grid:
            "height": latest_measurement["height_cm"] if latest_measurement else None,
            "weight": latest_measurement["weight_kg"] if latest_measurement else None,
            "bmi_value": latest_measurement["bmi"] if latest_measurement else None,
        }

        print("datadatadatadatadata", data)
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
            today = today + timedelta(days=3)

            print("qqqqqqqqqqqqqqqqqqqqqqqqq", today)
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

            print("assignments", assignments)
            
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
            print("eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", e)
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpcomingWorkoutsAPIView(APIView):
    """API to get upcoming workouts for the next 7 days"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            print("oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
            today = timezone.now().date()
            today = today + timedelta(days=3)
            next_7_days = [today + timedelta(days=i) for i in range(1, 8)]
            
            # Get user's active assignments
            assignments = UserWorkoutAssignment.objects.filter(
                user=request.user,
                status='assigned',
                start_date__lte=today
            ).select_related('weekly_template').prefetch_related(
                'weekly_template__day_templates__activities__exercise__equipment'
            )
            print("ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooccccccccccccc", assignments)
            if not assignments.exists():
                return Response({
                    'status': 'success',
                    'message': 'No active workout assignments found',
                    'data': {
                        'upcoming_workouts': []
                    }
                })
            
            upcoming_workouts = []
            print("ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooccccccccccccc", assignments)
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

            print("ppppppppppppppppppppppppppppppppppppppppppp", upcoming_workouts)
            
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

            print("oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
            
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


            print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", assignments)
            
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
