import os
import json
import zipfile
import random
import string
import logging
import requests
import smtplib
import calendar
from io import BytesIO
from datetime import timedelta
from collections import defaultdict

from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, FileResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q, Sum, Count, Min, Max
from django.db.models.functions import TruncMonth
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import (
    TemplateView, ListView, CreateView, UpdateView,
    DetailView, DeleteView
)
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.utils.dateparse import parse_datetime

# Email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Twilio
from twilio.rest import Client

# Core Choices
from core.choices import (
    GenderChoice, PaymentStatusChoice, StaffRoleChoice,
    SubscriptionStatusChoice, TransactionCategoryChoice,
    TransactionStatusChoice, TransactionTypeChoice
)

# Models
from core.models import BusinessDetails, Configuration
from products.models import Product, Category, subcategory
from enquiry.models import Enquiry
from orders.models import Order, SubscriptionOrder
from payments.models import Payment, Transaction
from attendance.models import Attendance, Schedule
from accounts.models import CustomUser, Banner, Review, SocialMedia, PasswordResetOTP
from accounts.models import Vendor, MonthlyMembershipTrend

# Forms
from .forms import (
    CustomUserForm, CustomerRegistrationForm, MemberRegistrationForm,
    ReviewForm, BannerForm, ProfileUpdateForm, SocialMediaForm, UserLoginForm,
    PasswordResetRequestForm, PasswordResetOTPForm, UserEditForm, VendorForm
)

# Logging setup
logger = logging.getLogger(__name__)

# ============================================================================
# VENDOR MANAGEMENT VIEWS
# ============================================================================

class VendorListView(LoginRequiredMixin, ListView):
    model = Vendor
    template_name = 'advadmin/vendor_list.html'
    context_object_name = 'vendors'
    paginate_by = 10

    def get_queryset(self):
        """
        Filter vendors based on user role:
        - Superuser: See all vendors
        - Regular user: See only their vendor
        """
        queryset = Vendor.objects.all().order_by('-created_at')

        if not self.request.user.is_superuser:
            vendor = getattr(self.request.user, 'vendor_profile', None)
            queryset = queryset.filter(id=vendor.id) if vendor else queryset.none()

        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(shop_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search) |
                Q(city__icontains=search) |
                Q(gstin__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_superuser'] = self.request.user.is_superuser
        context['search_query'] = self.request.GET.get('search', '')
        return context


class VendorCreateView(LoginRequiredMixin, CreateView):
    model = Vendor
    form_class = VendorForm
    template_name = 'advadmin/vendor_form.html'
    success_url = reverse_lazy('vendor_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, "You don't have permission to create vendors.")
            return redirect('vendor_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, f'Vendor "{form.instance.shop_name}" created successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class VendorUpdateView(LoginRequiredMixin, UpdateView):
    model = Vendor
    form_class = VendorForm
    template_name = 'advadmin/vendor_form.html'
    success_url = reverse_lazy('vendor_list')

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            vendor = getattr(self.request.user, 'vendor_profile', None)
            queryset = queryset.filter(id=vendor.id) if vendor else queryset.none()
        return queryset

    def form_valid(self, form):
        messages.success(self.request, f'Vendor "{form.instance.shop_name}" updated successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class VendorDeleteView(LoginRequiredMixin, DeleteView):
    model = Vendor
    success_url = reverse_lazy('vendor_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, "You don't have permission to delete vendors.")
            return redirect('vendor_list')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        vendor = self.get_object()
        vendor_name = vendor.shop_name
        response = super().post(request, *args, **kwargs)
        messages.success(request, f'Vendor "{vendor_name}" deleted successfully!')
        return response


# ============================================================================
# USER MANAGEMENT VIEWS
# ============================================================================

class UserCreateView(LoginRequiredMixin, CreateView):
    model = CustomUser
    form_class = CustomUserForm
    success_url = reverse_lazy('user_list')
    login_url = 'login'
    redirect_field_name = 'next'

    def dispatch(self, request, *args, **kwargs):
        next_url = request.GET.get('next', '')
        if '/staff/Trainer/' in next_url:
            self.hide_staff_role = True
            self.default_staff_role = 'Trainer'
        elif '/staff/Manager/' in next_url:
            self.hide_staff_role = True
            self.default_staff_role = 'Trainer'
        else:
            self.hide_staff_role = False
            self.default_staff_role = None
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/create_user.html']
        elif admin_mode == 'standard':
            return ['admin_panel/authentication-register-standard.html']
        return ['admin_panel/add_user.html']

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['hide_staff_role'] = getattr(self, 'hide_staff_role', False)
        kwargs['default_staff_role'] = getattr(self, 'default_staff_role', None)
        kwargs['is_superuser'] = self.request.user.is_superuser
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hide_staff_role'] = getattr(self, 'hide_staff_role', False)
        context['default_staff_role'] = getattr(self, 'default_staff_role', None)
        return context

    def form_valid(self, form):
        try:
            user = form.save(commit=False)

            if getattr(form, 'default_staff_role', None):
                user.staff_role = form.default_staff_role

            if 'password1' in form.cleaned_data and form.cleaned_data['password1']:
                user.set_password(form.cleaned_data['password1'])

            max_member_id = CustomUser.objects.aggregate(Max('member_id'))['member_id__max'] or 0
            user.member_id = max_member_id + 1

            redirect_to = self.request.GET.get('next') or self.success_url
            self.redirect_to = redirect_to
            user.username = self.generate_username(user.member_id)
            user.vendor = self.request.user.vendor
            user.save()

            messages.success(self.request, "User added successfully.")
            return redirect(redirect_to)

        except Exception as e:
            messages.error(self.request, f"An error occurred: {str(e)}")
            return self.form_invalid(form)

    def generate_username(self, member_id):
        redirect_to = getattr(self, 'redirect_to', '')
        if 'Trainer' in redirect_to:
            prefix = "TRAINER"
        elif 'Manager' in redirect_to:
            prefix = "MANAGER"
        elif 'Admin' in redirect_to:
            prefix = "ADMIN"
        elif 'Vendor' in redirect_to:
            prefix = "VENDOR"
        else:
            prefix = "MEMBER"
        return f"{prefix}{str(member_id).zfill(5)}"


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = UserEditForm
    template_name = 'advadmin/user_edit.html'
    success_url = reverse_lazy('user_list')
    slug_field = "username"
    slug_url_kwarg = "username"

    def form_valid(self, form):
        user = form.save(commit=False)
        password = form.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        user.save()
        messages.success(self.request, "User updated successfully.")
        return super().form_valid(form)


class UserListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'admin_panel/user_list.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        if not user.is_superuser:
            queryset = queryset.filter(Vendor=user.vendor)

        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(member_id__icontains=search_query) |
                Q(phone_number__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        sort_param = self.request.GET.get('sort')
        if sort_param == 'name':
            queryset = queryset.order_by('first_name', 'last_name')
        elif sort_param == '-name':
            queryset = queryset.order_by('-first_name', '-last_name')
        elif sort_param == 'member_id':
            queryset = queryset.order_by('member_id')
        elif sort_param == '-member_id':
            queryset = queryset.order_by('-member_id')
        else:
            queryset = queryset.order_by('-date_joined')

        return queryset

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        return ['advadmin/manage_user.html'] if admin_mode == 'advanced' else ['admin_panel/manage_user.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = "user_list"
        return context


class CustomerListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'admin_panel/user_list.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().filter(staff_role__iexact='Customer')

        if not user.is_superuser:
            queryset = queryset.filter(Vendor=user.vendor)

        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(member_id__icontains=search_query) |
                Q(phone_number__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        sort_param = self.request.GET.get('sort')
        if sort_param == 'name':
            queryset = queryset.order_by('first_name', 'last_name')
        elif sort_param == '-name':
            queryset = queryset.order_by('-first_name', '-last_name')
        elif sort_param == 'member_id':
            queryset = queryset.order_by('member_id')
        elif sort_param == '-member_id':
            queryset = queryset.order_by('-member_id')
        else:
            queryset = queryset.order_by('-date_joined')

        return queryset

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        return ['advadmin/manage_customer.html'] if admin_mode == 'advanced' else ['admin_panel/manage_customer.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = "customer_list"
        return context


class UserStaffRoleListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'admin_panel/user_list.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        role = self.kwargs.get('role')
        user = self.request.user
        queryset = CustomUser.objects.filter(staff_role__iexact=role)

        if not user.is_superuser:
            queryset = queryset.filter(Vendor=user.vendor)

        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(member_id__icontains=search_query) |
                Q(phone_number__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        sort_param = self.request.GET.get('sort')
        if sort_param == 'name':
            queryset = queryset.order_by('first_name', 'last_name')
        elif sort_param == '-name':
            queryset = queryset.order_by('-first_name', '-last_name')
        elif sort_param == 'member_id':
            queryset = queryset.order_by('member_id')
        elif sort_param == '-member_id':
            queryset = queryset.order_by('-member_id')
        else:
            queryset = queryset.order_by('-date_joined')
        return queryset

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        return ['advadmin/manage_user.html'] if admin_mode == 'advanced' else ['admin_panel/manage_user.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        role = self.kwargs.get('role', '').lower()
        context['page_name'] = f"{role}_Users"
        return context


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomUser
    slug_field = "username"
    slug_url_kwarg = "username"
    success_url = reverse_lazy('user_list')

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'User has been deleted successfully.')
        response = super().delete(request, *args, **kwargs)
        next_url = request.META.get('HTTP_REFERER') or self.success_url
        return redirect(next_url)


@require_POST
@login_required
@csrf_exempt
def toggle_user_active(request):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        action = data.get('action')

        if not user_id or action not in ['block', 'unblock']:
            return JsonResponse({'success': False, 'message': 'Invalid parameters'}, status=400)

        user = CustomUser.objects.get(username=user_id)
        user.is_active = (action == 'unblock')
        user.save()

        return JsonResponse({
            'success': True,
            'message': f'User {"unblocked" if user.is_active else "blocked"} successfully',
            'is_active': user.is_active
        })

    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


class BlockedUserListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'advadmin/blocked_users.html'
    permission_required = 'auth.change_user'
    context_object_name = 'users'

    def get_queryset(self):
        return CustomUser.objects.filter(
            is_active=False,
            vendor=self.request.user.vendor,
            staff_role="Customer"
        ).order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = "blocked_users"
        return context


class InactiveUserListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'advadmin/inactive_users.html'
    permission_required = 'auth.change_user'
    context_object_name = 'users'

    def get_queryset(self):
        return CustomUser.objects.filter(
            on_subscription=False,
            staff_role="Customer",
            vendor=self.request.user.vendor,
        ).order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = "inactive_users"
        return context


class UnblockUserView(LoginRequiredMixin, View):
    permission_required = 'auth.change_user'

    def post(self, request, *args, **kwargs):
        username = kwargs.get('username')
        try:
            user = CustomUser.objects.get(username=username)
            user.is_active = True
            user.save()
            return JsonResponse({
                'success': True,
                'message': f'User {username} has been unblocked successfully'
            })
        except CustomUser.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)


# ============================================================================
# MEMBER REGISTRATION VIEWS
# ============================================================================

class MemberRegisterView(LoginRequiredMixin, CreateView):
    model = CustomUser
    form_class = MemberRegistrationForm
    success_url = reverse_lazy('user_list')

    def get_template_names(self):
        return ['advadmin/member_registration.html']

    def form_valid(self, form):
        try:
            user = form.save(commit=False)
            user.staff_role = 'Member'
            user.vendor = self.request.user.vendor

            if form.cleaned_data.get('password1'):
                user.set_password(form.cleaned_data['password1'])
            user.save()

            package = form.cleaned_data['package']
            self.request.session['pending_member_member_id'] = user.member_id
            self.request.session['pending_package_id'] = package.id

            messages.success(self.request, "Please complete package payment to activate membership.")
            return redirect('registration_next_steps')

        except Exception as e:
            messages.error(self.request, f"Error: {str(e)}")
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        role = self.kwargs.get('role', '').capitalize()
        context['page_name'] = "member_registration"
        return context


class CustomerCreateView(View):
    template_name = 'advadmin/customer_registration.html'

    def get(self, request):
        users = CustomUser.objects.all()
        form = CustomerRegistrationForm()
        return render(request, self.template_name, {'form': form, 'users': users})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer created successfully!")
            return redirect('customer_registration')
        else:
            messages.error(request, "Error creating customer.")
            print("Form errors:", form.errors)
        return render(request, self.template_name, {'form': form, 'users': CustomUser.objects.all()})


class RegistrationNextStepsView(View):
    def get(self, request):
        member_id = request.session.get("pending_member_member_id")
        package_id = request.session.get("pending_package_id")
        print("package_idpackage_idpackage_idpackage_id", package_id)
        print("member_idmember_idmember_idmember_idmember_id", member_id)

        if not member_id or not package_id:
            return redirect('register_member')

        return render(request, "advadmin/registration_next_steps.html")


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

class CustomLoginView(LoginView):
    template_name = "admin_panel/authentication-login.html"
    form_class = UserLoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/auth-login-basic.html']
        elif admin_mode == 'standard':
            return ['admin_panel/authentication-login-standard.html']
        return ['admin_panel/authentication-login-basic.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = 'Login'
        return context

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        remember_me = self.request.POST.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
        else:
            self.request.session.set_expiry(60 * 60 * 24 * 30)

        messages.success(self.request, "Login successful!")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Invalid credentials. Please try again.", extra_tags='danger')
        return self.render_to_response(self.get_context_data(form=form))


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('login')


class PasswordResetRequestView(View):
    template_name = 'advadmin/auth-forgot-password-basic.html'

    def get(self, request):
        return render(request, self.template_name, {'form': PasswordResetRequestForm()})

    def post(self, request):
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = CustomUser.objects.get(email=email)

                PasswordResetOTP.objects.filter(user=user, is_used=False).delete()

                otp = ''.join(random.choices(string.digits, k=6))
                expires_at = timezone.now() + timezone.timedelta(minutes=15)
                otp_obj = PasswordResetOTP.objects.create(
                    user=user,
                    otp=otp,
                    expires_at=expires_at
                )

                subject = f"Password Reset OTP for {settings.SITE_NAME}"
                body = f"""
                Dear {user.get_full_name() or user.username},

                You have requested to reset your password. Please use the following OTP:

                OTP: {otp_obj.otp}

                This OTP is valid for 15 minutes.

                If you didn't request this, please ignore this email.

                Best regards,
                {settings.SITE_NAME} Team
                """

                smtp_server = "smtp.gmail.com"
                smtp_port = 587
                smtp_username = settings.EMAIL_HOST_USER
                smtp_password = settings.EMAIL_HOST_PASSWORD

                msg = MIMEMultipart()
                msg['From'] = settings.DEFAULT_FROM_EMAIL
                msg['To'] = email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))

                try:
                    with smtplib.SMTP(smtp_server, smtp_port) as server:
                        server.starttls()
                        server.login(smtp_username, smtp_password)
                        server.send_message(msg)

                    messages.success(request, "An OTP has been sent to your email address.")
                    logger.info(f"Password reset OTP sent to {email}")
                    return redirect(reverse('password_reset_verify', kwargs={'user_username': user.username}))

                except smtplib.SMTPAuthenticationError:
                    error_msg = "SMTP authentication failed. Please check email credentials."
                    logger.error(error_msg)
                    messages.error(request, "Email service temporarily unavailable. Please try later.")
                except smtplib.SMTPException as e:
                    error_msg = f"SMTP error occurred: {str(e)}"
                    logger.error(error_msg)
                    messages.error(request, "Failed to send email. Please try again.")
                except Exception as e:
                    error_msg = f"Unexpected error: {str(e)}"
                    logger.error(error_msg)

                return redirect('password_reset_request')

            except CustomUser.DoesNotExist:
                messages.success(request, "If an account exists with this email, we've sent an OTP.")
                logger.info(f"Password reset requested for non-existent email: {email}")
                return redirect('password_reset_request')

        logger.warning(f"Invalid form submission: {form.errors}")
        return render(request, self.template_name, {'form': form})


class PasswordResetVerifyView(View):
    template_name = 'advadmin/auth-reset-password-basic.html'

    def get(self, request, user_username):
        try:
            user = CustomUser.objects.get(username=user_username)
            return render(request, self.template_name, {
                'form': PasswordResetOTPForm(),
                'user_username': user_username
            })
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid user.")
            return redirect('password_reset_request')

    def post(self, request, user_username):
        form = PasswordResetOTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            new_password1 = form.cleaned_data['new_password1']
            new_password2 = form.cleaned_data['new_password2']

            if new_password1 != new_password2:
                messages.error(request, "Passwords don't match.")
                return render(request, self.template_name, {
                    'form': form,
                    'user_username': user_username
                })

            try:
                user = CustomUser.objects.get(username=user_username)
                otp_obj = PasswordResetOTP.objects.get(
                    user=user,
                    otp=otp,
                    is_used=False,
                    expires_at__gt=timezone.now()
                )

                user.set_password(new_password1)
                user.save()

                otp_obj.is_used = True
                otp_obj.save()

                PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)

                messages.success(request, "Password reset successfully. You can now login with your new password.")
                return redirect('login')

            except CustomUser.DoesNotExist:
                messages.error(request, "Invalid user.")
                return redirect('password_reset_request')
            except PasswordResetOTP.DoesNotExist:
                messages.error(request, "Invalid or expired OTP.")
                return render(request, self.template_name, {
                    'form': form,
                    'user_username': user_username
                })

        return render(request, self.template_name, {
            'form': form,
            'user_username': user_username
        })


class LoginWithOTPView(View):
    template_name = 'advadmin/login_with_otp.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        phone_number = request.POST.get('phone_number')
        if not phone_number:
            messages.error(request, "Phone number is required")
            return render(request, self.template_name)

        try:
            user = CustomUser.objects.get(phone_number=phone_number)
        except CustomUser.DoesNotExist:
            messages.error(request, "No user found with the corresponding phone number.")
            return render(request, self.template_name)

        email = user.email
        otp = str(random.randint(100000, 999999))
        valid_until = timezone.now() + timedelta(minutes=5)

        request.session['otp'] = otp
        request.session['otp_valid_until'] = valid_until.isoformat()
        request.session['phone_number'] = phone_number

        configs = Configuration.objects.filter(
            config__in=["enable-emailotp", "enable-smsotp"]
        )
        config_values = {config.config: config.value for config in configs}

        def str_to_bool(value):
            return value.lower() in ("true", "1", "yes", "on")

        if str_to_bool(config_values.get("enable-emailotp", "False")):
            self.send_otp_via_email(email, otp)
        if str_to_bool(config_values.get("enable-smsotp", "False")):
            self.send_otp_via_twilio(phone_number, otp)

        return redirect('verify_otp')

    def send_otp_via_email(self, email, otp):
        subject = f"OTP for {settings.SITE_NAME}"
        body = (
            f"Dear User,\n\n"
            f"Your OTP for logging in to {settings.SITE_NAME} is:\n\n"
            f"OTP: {otp}\n\n"
            f"This OTP is valid for 5 minutes.\n\n"
            f"If you didn't request this, please ignore this email.\n\n"
            f"Best regards,\n{settings.SITE_NAME} Team"
        )
        try:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
            messages.success(self.request, "OTP has been sent to your email. Please check your inbox.")
        except Exception as e:
            messages.error(self.request, "Failed to send OTP via email. Please try again.")
            print(f"Error sending email: {e}")

    def send_otp_via_twilio(self, phone_number, otp):
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f"Your OTP for login is: {otp}. Valid for 5 minutes.",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            print("message response from twilio:", message)
            return True
        except Exception as e:
            print(f"Error sending OTP: {e}")
            return False


class VerifyOTPView(View):
    template_name = 'advadmin/verify_otp.html'

    def get(self, request):
        if 'phone_number' not in request.session:
            messages.error(request, "Session expired. Please request OTP again.")
            return redirect('login_with_otp')
        return render(request, self.template_name)

    def post(self, request):
        user_otp = request.POST.get('otp', '').strip()
        phone_number = request.session.get('phone_number')
        stored_otp = request.session.get('otp')
        otp_valid_until = request.session.get('otp_valid_until')

        if not all([user_otp, stored_otp, otp_valid_until]):
            messages.error(request, "Session expired. Please request OTP again.")
            return redirect('login_with_otp')

        otp_expiry = parse_datetime(otp_valid_until)
        if otp_expiry is not None and timezone.is_naive(otp_expiry):
            otp_expiry = timezone.make_aware(otp_expiry)

        if timezone.now() > otp_expiry:
            messages.error(request, "OTP has expired. Please request a new one.")
            return redirect('login_with_otp')

        if user_otp == stored_otp:
            try:
                user = CustomUser.objects.get(phone_number=phone_number)
            except CustomUser.DoesNotExist:
                messages.error(request, "No user found with the corresponding phone number.")
                return render(request, self.template_name)

            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            for k in ('otp', 'otp_valid_until', 'phone_number'):
                request.session.pop(k, None)

            return redirect('otp_login_success')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, self.template_name)


class OTPLoginSuccessView(View):
    template_name = 'advadmin/otp_login_success.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login_with_otp')
        return redirect('dashboard')


def login_redirect(request):
    return redirect('/accounts/google/login/?process=login')


@method_decorator(csrf_exempt, name='dispatch')
class GoogleSSOCallbackView(View):
    def get(self, request):
        code = request.GET.get('code')
        if not code:
            messages.error(request, "Authorization code not found.")
            return redirect('/login/')

        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'code': code,
            'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
            'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET,
            'redirect_uri': settings.GOOGLE_OAUTH_REDIRECT_URI,
            'grant_type': 'authorization_code',
        }

        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()
        access_token = token_json.get('access_token')

        if not access_token:
            messages.error(request, "Failed to retrieve access token.")
            return redirect('/login/')

        user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        user_info_response = requests.get(
            user_info_url,
            params={'alt': 'json'},
            headers={'Authorization': f'Bearer {access_token}'}
        )
        user_info = user_info_response.json()
        email = user_info.get('email')
        name = user_info.get('name')

        if not email:
            messages.error(request, "Email not found in Google profile.")
            return redirect('/login/')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, "User not registered. Please sign up first.")
            return redirect('/login/')

        if user.first_name != name:
            user.first_name = name
            user.save()

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        return redirect('/dashboard')


# ============================================================================
# DASHBOARD & ANALYTICS VIEWS
# ============================================================================

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Admin Dashboard View that serves summary statistics, charts, and daily status
    of users, attendance, revenue, subscriptions, and classes.
    Supports both superuser (all vendors) and vendor-specific views.
    """
    template_name = 'admin_panel/index.html'

    def get_vendor_filter(self):
        """
        Returns the vendor filter for the current user.
        - Superuser: None (shows all data)
        - Regular user: Their specific vendor
        """
        if self.request.user.is_superuser:
            return None
        return getattr(self.request.user, 'vendor_profile', None)

    def get_template_names(self):
        """
        Dynamically return the correct dashboard template based on ADMIN_PANEL_MODE setting.
        """
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/index.html']
        elif admin_mode == 'standard':
            return ['admin_panel/standard.html']
        return [self.template_name]

    def get_membership_trends(self, years, vendor_filter):
        """
        Get membership trends filtered by vendor or all vendors for superuser.
        """
        today = timezone.now().date()
        membership_trends = defaultdict(lambda: [0] * 12)

        filters = Q(year__in=years, month__lte=12)
        if vendor_filter:
            filters &= Q(vendor=vendor_filter)

        trends = MonthlyMembershipTrend.objects.filter(filters).order_by('year', 'month')

        if vendor_filter:
            trends_dict = {(t.year, t.month): t.member_count for t in trends}
        else:
            trends_aggregated = trends.values('year', 'month').annotate(
                total_count=Sum('member_count')
            )
            trends_dict = {(t['year'], t['month']): t['total_count'] for t in trends_aggregated}

        for year in years:
            for month in range(1, 13):
                if year > today.year or (year == today.year and month > today.month):
                    continue
                count = trends_dict.get((year, month), 0)
                membership_trends[year][month - 1] = count

        return membership_trends

    def get_context_data(self, **kwargs):
        """
        Collects and prepares context data for dashboard rendering.
        Handles both superuser (all vendors) and vendor-specific views.
        """
        context = super().get_context_data(**kwargs)
        vendor_filter = self.get_vendor_filter()
        today = timezone.now().date()
        first_day = today.replace(day=1)
        last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        current_month_name = calendar.month_name[today.month]

        # Site Configurations
        configs = Configuration.objects.all()
        config_dict = {
            conf.config.replace("-", "_"): conf.value
            for conf in configs
        }

        def apply_vendor_filter(queryset, vendor_field='vendor_profile'):
            """Helper to apply vendor filter to querysets"""
            if vendor_filter:
                return queryset.filter(**{vendor_field: vendor_filter})
            return queryset

        # User Metrics
        active_users_query = CustomUser.objects.filter(
            staff_role='Member', is_active=True, on_subscription=True
        )
        active_users_count = apply_vendor_filter(active_users_query, 'vendor_profile').count()

        new_signups_query = CustomUser.objects.filter(
            staff_role='Member', join_date=today
        )
        new_signups_today = apply_vendor_filter(new_signups_query, 'vendor_profile').count()

        total_members_query = CustomUser.objects.filter(
            staff_role='Member', is_active=True
        )
        total_members = apply_vendor_filter(total_members_query, 'vendor_profile').count()

        # Attendance Metrics
        attendance_query = Attendance.objects.filter(date=today)
        if vendor_filter:
            attendance_query = attendance_query.filter(user__vendor_profile=vendor_filter)
        attended_today = attendance_query.values('user').distinct().count()
        attendance_rate = round((attended_today / total_members * 100), 1) if total_members else 0
        expiring_memberships = 0

        # Monthly Revenue
        payment_query = Payment.objects.filter(
            status=PaymentStatusChoice.COMPLETED,
            created_at__date__gte=first_day,
            created_at__date__lte=today,
        )
        if vendor_filter:
            payment_query = payment_query.filter(vendor=vendor_filter)
        current_month_income = payment_query.aggregate(total=Sum('amount'))['total'] or 0

        # Transaction Summary
        transactions_query = Transaction.objects.all()
        if vendor_filter:
            transactions_query = transactions_query.filter(vendor=vendor_filter)

        total_sales_amount = transactions_query.filter(
            category=TransactionCategoryChoice.SALES,
            transaction_type=TransactionTypeChoice.INCOME,
            status=TransactionStatusChoice.COMPLETED
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_completed_amount = transactions_query.filter(
            status=TransactionStatusChoice.COMPLETED
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_transaction_amount = transactions_query.aggregate(total=Sum('amount'))['total'] or 0

        total_income = transactions_query.filter(
            transaction_type=TransactionTypeChoice.INCOME,
            status=TransactionStatusChoice.COMPLETED
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_expense = transactions_query.filter(
            transaction_type=TransactionTypeChoice.EXPENSE,
            status=TransactionStatusChoice.COMPLETED
        ).aggregate(total=Sum('amount'))['total'] or 0

        profit = total_income - total_expense

        # Subscription Order Status Breakdown
        orders_query = SubscriptionOrder.objects.all()
        if vendor_filter:
            orders_query = orders_query.filter(vendor=vendor_filter)

        orders = orders_query.values('status').annotate(count=Count('id'))
        status_map = {
            'pending': 'pending_orders',
            'processing': 'processing_orders',
            'shipped': 'shipped_orders',
            'delivered': 'delivered_orders',
            'cancelled': 'cancelled_orders',
            'return': 'returned_orders',
        }

        order_status_counts = {
            'pending_orders': 0,
            'processing_orders': 0,
            'shipped_orders': 0,
            'delivered_orders': 0,
            'cancelled_orders': 0,
            'returned_orders': 0,
        }
        total_orders = 0

        for order in orders:
            order_status = order['status']
            count = order['count']
            total_orders += count
            if order_status in status_map:
                order_status_counts[status_map[order_status]] = count

        # Upcoming Renewals
        upcoming_renewals_query = SubscriptionOrder.objects.filter(
            end_date__gte=today,
            end_date__lte=last_day,
            status__in=[SubscriptionStatusChoice.ACTIVE, SubscriptionStatusChoice.PENDING],
        )
        if vendor_filter:
            upcoming_renewals_query = upcoming_renewals_query.filter(vendor=vendor_filter)

        upcoming_renewals_result = upcoming_renewals_query.aggregate(
            renewals_count=Count('id'),
            renewals_amount=Sum('total')
        )
        upcoming_renewals_count = upcoming_renewals_result['renewals_count'] or 0
        upcoming_renewals_amount = upcoming_renewals_result['renewals_amount'] or 0

        # Pending Dues
        pending_dues_query = SubscriptionOrder.objects.filter(
            end_date__lt=today,
            end_date__gte=first_day,
            end_date__lte=last_day,
            payment_status=PaymentStatusChoice.PENDING,
        )
        if vendor_filter:
            pending_dues_query = pending_dues_query.filter(vendor=vendor_filter)

        pending_dues_result = pending_dues_query.aggregate(
            pending_dues_count=Count('id'),
            pending_dues_amount=Sum('total')
        )
        pending_dues_count = pending_dues_result['pending_dues_count'] or 0
        pending_dues_amount = pending_dues_result['pending_dues_amount'] or 0

        # Enquiries
        try:
            enquiry_query = Enquiry.objects.all()
            if vendor_filter:
                enquiry_query = enquiry_query.filter(vendor=vendor_filter)
            total_enquiries = enquiry_query.count()
        except Exception:
            total_enquiries = 0

        # Recent Transactions
        recent_transactions = transactions_query.order_by('-created_at')[:6]

        # Chart Data: Membership Trends and Earnings
        earliest_year_query = CustomUser.objects.filter(
            staff_role='Member', is_active=True
        )
        if vendor_filter:
            earliest_year_query = earliest_year_query.filter(vendor_profile=vendor_filter)

        earliest_year = earliest_year_query.aggregate(earliest=Min('join_date'))['earliest']
        base_year = earliest_year.year if earliest_year else today.year - 2
        years = list(range(base_year, today.year + 1))

        membership_trends = self.get_membership_trends(years, vendor_filter)

        # Yearly Earnings
        yearly_earnings = {}
        for year in years:
            year_start = today.replace(year=year, month=1, day=1)
            year_end = today.replace(year=year, month=12, day=31)
            year_payment_query = Payment.objects.filter(
                status=PaymentStatusChoice.COMPLETED,
                created_at__date__gte=year_start,
                created_at__date__lte=year_end,
            )
            if vendor_filter:
                year_payment_query = year_payment_query.filter(vendor=vendor_filter)
            amount = year_payment_query.aggregate(total=Sum('amount'))['total'] or 0
            yearly_earnings[year] = float(amount)

        # Monthly Revenue By Year
        monthly_revenue_by_year = {}
        for year in years:
            monthly_amounts = [0] * 12
            monthly_payments_query = Payment.objects.filter(
                status=PaymentStatusChoice.COMPLETED,
                created_at__year=year,
            )
            if vendor_filter:
                monthly_payments_query = monthly_payments_query.filter(vendor=vendor_filter)

            monthly_payments = (
                monthly_payments_query
                .annotate(month=TruncMonth('created_at'))
                .values('month')
                .annotate(total=Sum('amount'))
                .order_by('month')
            )

            for month_data in monthly_payments:
                month = month_data['month'].month
                monthly_amounts[month - 1] = float(month_data['total'] or 0)
            monthly_revenue_by_year[year] = monthly_amounts

        # Update today's schedule statuses
        schedule_update_query = Schedule.objects.filter(schedule_date=today)
        if vendor_filter:
            schedule_update_query = schedule_update_query.filter(vendor=vendor_filter)
        schedule_update_query.select_related('trainer').prefetch_related(
            'enrollments', 'attendances'
        ).update(status='upcoming')

        schedules_today_query = Schedule.objects.filter(schedule_date=today)
        if vendor_filter:
            schedules_today_query = schedules_today_query.filter(vendor=vendor_filter)

        schedules_today = schedules_today_query
        for schedule in schedules_today:
            schedule.update_status()

        # Running Classes
        running_classes_query = Schedule.objects.filter(
            schedule_date=today, status='live'
        ).select_related('trainer').prefetch_related('enrollments', 'attendances')

        if vendor_filter:
            running_classes_query = running_classes_query.filter(vendor=vendor_filter)

        running_classes = []
        for cls in running_classes_query:
            running_classes.append({
                'class_name': cls.name,
                'trainer_name': cls.trainer.get_full_name() if cls.trainer else "Unassigned",
                'start_time': cls.start_time.strftime('%I:%M %p'),
                'end_time': cls.end_time.strftime('%I:%M %p'),
                'current_attendance': cls.attendances.filter(date=today).count(),
                'max_capacity': cls.capacity,
                'location': 'Main Hall',
            })

        # Pages group
        PAGES_GROUP = [
            'about-us', 'class-timetable', 'bmi-calculator',
            'team', 'gallery', 'blog', '404'
        ]

        # Yearly and Monthly growth calculation
        growth_per_month = {}
        current_month_index = today.month - 1

        for year in years:
            months_list = membership_trends.get(year, [0] * 12)
            for month_idx in range(len(months_list)):
                if year == today.year and month_idx > current_month_index:
                    break
                curr = months_list[month_idx]

                if month_idx == 0:
                    prev_year = year - 1
                    prev_month_val = membership_trends.get(prev_year, [0] * 12)[11] if prev_year in membership_trends else 0
                else:
                    prev_month_val = months_list[month_idx - 1]

                if prev_month_val:
                    percent = round(((curr - prev_month_val) / prev_month_val) * 100, 2)
                else:
                    percent = 100.0 if curr > 0 else 0

                key = f"{year}-{month_idx + 1:02d}"
                growth_per_month[key] = {"percent": percent, "count": curr}

        month_keys = list(growth_per_month.keys())
        last_two = month_keys[-2:] if len(month_keys) >= 2 else month_keys
        last_two_dict = {k: growth_per_month[k] for k in last_two}
        growth_per_month_json = json.dumps(last_two_dict)
        growth_months = list(last_two_dict.keys())[::-1]

        # Final Context Update
        context.update(config_dict)
        context.update({
            'is_superuser': self.request.user.is_superuser,
            'vendor_name': vendor_filter.shop_name if vendor_filter else 'All Vendors',
            'growth_per_month_json': growth_per_month_json,
            'growth_month_keys': growth_months,
            'running_classes': running_classes,
            'monthly_revenue_json': json.dumps(monthly_revenue_by_year),
            'membership_trends_json': json.dumps(membership_trends),
            'yearly_earnings_json': json.dumps(yearly_earnings),
            'years': years,
            'current_year': today.year,
            'pages_group': PAGES_GROUP,
            'current_month': current_month_name,
            'current_month_income': current_month_income,
            'total_members': total_members,
            'upcoming_renewals_count': upcoming_renewals_count,
            'upcoming_renewals_amount': upcoming_renewals_amount,
            'pending_dues_count': pending_dues_count,
            'pending_dues_amount': pending_dues_amount,
            'active_users_count': active_users_count,
            'new_signups_today': new_signups_today,
            'attendance_rate': attendance_rate,
            'expiring_memberships': expiring_memberships,
            'total_sales_amount': total_sales_amount,
            'total_completed_amount': total_completed_amount,
            'total_transaction_amount': total_transaction_amount,
            'profit': profit,
            'total_enquiries': total_enquiries,
            'total_orders': total_orders,
            'recent_transactions': recent_transactions,
            'page_name': "dashboard",
            'admin_mode': getattr(settings, 'ADMIN_PANEL_MODE', 'basic'),
        })
        context.update(order_status_counts)

        return context


class DashboardSearchView(LoginRequiredMixin, TemplateView):
    template_name = 'admin_panel/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('search', '').strip()
        category_id = self.request.GET.get('category', '').strip()
        subcategory_id = self.request.GET.get('subcategory', '').strip()

        products = Product.objects.all()
        error_message = None

        if query or category_id or subcategory_id:
            if query:
                products = products.filter(name__icontains=query)
            if category_id:
                products = products.filter(category_id=category_id)
            if subcategory_id:
                products = products.filter(subcategory_id=subcategory_id)
        else:
            error_message = "Please provide at least one search parameter."

        context.update({
            'total_products': Product.objects.all(),
            'total_categories': Category.objects.all(),
            'total_subcategories': subcategory.objects.all(),
            'products': products,
            'query': query,
            'selected_category': category_id,
            'selected_subcategory': subcategory_id,
            'error_message': error_message,
        })
        return context


# ============================================================================
# REVIEW MANAGEMENT VIEWS
# ============================================================================

class ReviewListView(LoginRequiredMixin, ListView):
    model = Review
    template_name = 'admin_panel/review_list.html'
    context_object_name = 'reviews'

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/review_list.html']
        return ['admin_panel/review_list.html']


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'admin_panel/review_form.html'
    success_url = reverse_lazy('review_list')

    def form_valid(self, form):
        messages.success(self.request, "Review added successfully!")
        return super().form_valid(form)

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/review_form.html']
        return ['admin_panel/review_form.html']

    def form_invalid(self, form):
        messages.error(self.request, "There was an error adding the review. Please check the form.")
        return super().form_invalid(form)


class ReviewDetailView(LoginRequiredMixin, DetailView):
    model = Review
    template_name = 'admin_panel/review_detail.html'
    context_object_name = 'review'

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/review_detail.html']
        return ['admin_panel/review_detail.html']


class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'admin_panel/review_form.html'
    success_url = reverse_lazy('review_list')

    def form_valid(self, form):
        messages.success(self.request, "Review updated successfully!")
        return super().form_valid(form)

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/review_form.html']
        return ['admin_panel/review_form.html']

    def form_invalid(self, form):
        messages.error(self.request, "Error updating review. Please check the form.")
        return super().form_invalid(form)


class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    model = Review
    success_url = reverse_lazy('review_list')
    template_name = None

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Review deleted successfully!")
        return super().delete(request, *args, **kwargs)


# ============================================================================
# BANNER MANAGEMENT VIEWS
# ============================================================================

class BannerListView(LoginRequiredMixin, ListView):
    model = Banner
    template_name = 'admin_panel/banner_list.html'
    context_object_name = 'banners'

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/banner_list.html']
        return ['admin_panel/banner_list.html']


class BannerCreateView(LoginRequiredMixin, CreateView):
    model = Banner
    form_class = BannerForm
    template_name = 'admin_panel/banner_form.html'
    success_url = reverse_lazy('banner_list')

    def form_valid(self, form):
        messages.success(self.request, "Banner added successfully!")
        return super().form_valid(form)

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/banner_form.html']
        return ['admin_panel/banner_form.html']

    def form_invalid(self, form):
        messages.error(self.request, "There was an error adding the banner. Please check the form.")
        return super().form_invalid(form)


class BannerDetailView(LoginRequiredMixin, DetailView):
    model = Banner
    template_name = 'admin_panel/banner_detail.html'
    context_object_name = 'banner'

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/banner_form.html']
        return ['admin_panel/banner_form.html']


class BannerUpdateView(LoginRequiredMixin, UpdateView):
    model = Banner
    form_class = BannerForm
    template_name = 'admin_panel/banner_form.html'
    success_url = reverse_lazy('banner_list')

    def form_valid(self, form):
        messages.success(self.request, "Banner updated successfully!")
        return super().form_valid(form)

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/banner_form.html']
        return ['admin_panel/banner_form.html']

    def form_invalid(self, form):
        messages.error(self.request, "Error updating banner. Please check the form.")
        return super().form_invalid(form)


class BannerDeleteView(LoginRequiredMixin, DeleteView):
    model = Banner
    success_url = reverse_lazy('banner_list')
    template_name = None

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Banner deleted successfully!")
        return super().delete(request, *args, **kwargs)


# ============================================================================
# SOCIAL MEDIA MANAGEMENT VIEWS
# ============================================================================

class SocialMediaListView(LoginRequiredMixin, ListView):
    model = SocialMedia
    template_name = 'admin_panel/socialmedia_list.html'
    context_object_name = 'social_links'

    def get_queryset(self):
        return SocialMedia.objects.filter(user=self.request.user)

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/socialmedia_list.html']
        return ['admin_panel/socialmedia_list.html']


class SocialMediaCreateView(LoginRequiredMixin, CreateView):
    model = SocialMedia
    form_class = SocialMediaForm
    template_name = 'admin_panel/socialmedia_form.html'
    success_url = reverse_lazy('socialmedia_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/socialmedia_form.html']
        return ['admin_panel/socialmedia_form.html']

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            form.instance.user = self.request.user
        messages.success(self.request, "Social media link added successfully!")
        return super().form_valid(form)


class SocialMediaDetailView(LoginRequiredMixin, DetailView):
    model = SocialMedia
    template_name = 'admin_panel/socialmedia_detail.html'
    context_object_name = 'social_link'

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/socialmedia_detail.html']
        return ['admin_panel/socialmedia_detail.html']


class SocialMediaUpdateView(LoginRequiredMixin, UpdateView):
    model = SocialMedia
    form_class = SocialMediaForm
    template_name = 'admin_panel/socialmedia_form.html'
    success_url = reverse_lazy('socialmedia_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/socialmedia_form.html']
        return ['admin_panel/socialmedia_form.html']

    def form_valid(self, form):
        messages.success(self.request, "Social media link updated successfully!")
        return super().form_valid(form)


class SocialMediaDeleteView(LoginRequiredMixin, DeleteView):
    model = SocialMedia
    success_url = reverse_lazy('socialmedia_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Social media link deleted successfully!")
        return super().delete(request, *args, **kwargs)


# ============================================================================
# ACCOUNT & PROFILE VIEWS
# ============================================================================

class AccountSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'advadmin/pages-account-settings-account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = 'advadmin/pages-account-settings-account.html'
    success_url = reverse_lazy('account_settings')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        print("self.request.FILES", self.request.FILES)
        if 'profile_image' in self.request.FILES:
            self.object.profile_image = self.request.FILES['profile_image']
            self.object.save()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


# ============================================================================
# API & UTILITY VIEWS
# ============================================================================

class FetchProductsView(View):
    def get(self, request, *args, **kwargs):
        category_id = self.kwargs['category_id']
        products = Product.objects.filter(
            category_id=category_id,
            is_active=True
        ).values('id', 'name', 'price', 'sku')
        return JsonResponse(list(products), safe=False)


class DownloadDatabaseView(LoginRequiredMixin, View):
    def get(self, request):
        db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
        if os.path.exists(db_path):
            response = FileResponse(open(db_path, 'rb'), as_attachment=True, filename="database.sqlite3")
            return response
        return HttpResponse("Database file not found.", status=404)


class DownloadAllMediaView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            memory_buffer = BytesIO()
            with zipfile.ZipFile(memory_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                media_root = str(settings.MEDIA_ROOT)
                for root, _, files in os.walk(media_root):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if file_path.startswith(media_root):
                            arcname = os.path.relpath(file_path, media_root)
                            zipf.write(file_path, arcname)

            memory_buffer.seek(0)
            response = HttpResponse(memory_buffer.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="all_media_files.zip"'
            memory_buffer.close()
            return response

        except Exception as e:
            if 'memory_buffer' in locals():
                memory_buffer.close()
            return HttpResponse(f"Error creating archive: {str(e)}", status=500, content_type='text/plain')


def get_company_data(request):
    try:
        company = BusinessDetails.objects.first()
        category_names = list(Category.objects.values_list('name', flat=True))

        if not company:
            return JsonResponse({'error': 'No company data found'}, status=404)

        data = {
            'company_name': company.company_name,
            'gstn': company.gstn,
            'breadcrumb_image_url': (
                company.breadcrumb_image.url if company.breadcrumb_image else None
            ),
            'about_page_image_url': (
                company.about_page_image.url if company.about_page_image else None
            ),
            'company_tagline': company.company_tagline,
            'company_logo_svg_url': (
                company.company_logo_svg.url if company.company_logo_svg else None
            ),
            'company_logo_url': (
                company.company_logo.url if company.company_logo else None
            ),
            'company_favicon_url': (
                company.company_favicon.url if company.company_favicon else None
            ),
            'company_address': company.offline_address,
            'company_map_location': company.map_location,
            'info_mobile': company.info_mobile,
            'info_email': company.info_email,
            'complaint_mobile': company.complaint_mobile,
            'complaint_email': company.complaint_email,
            'sales_mobile': company.sales_mobile,
            'sales_email': company.sales_email,
            'company_instagram': company.company_instagram,
            'company_facebook': company.company_facebook,
            'company_email_ceo': company.company_email_ceo,
            'opening_time': (
                company.opening_time.strftime('%H:%M:%S') if company.opening_time else None
            ),
            'closing_time': (
                company.closing_time.strftime('%H:%M:%S') if company.closing_time else None
            ),
            'closed_days': (
                company.closed_days.split(',') if company.closed_days else []
            ),
            'category_names': category_names
        }
        return JsonResponse(data)

    except ObjectDoesNotExist as e:
        logger.error(f"ObjectDoesNotExist Error: {str(e)} - Failed to fetch company data.")
        return JsonResponse({'error': 'Company data not found or missing fields'}, status=500)
    except Exception as e:
        logger.error(f"Error while processing company data: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred while processing company data'}, status=500)


# ============================================================================
# STATIC PAGE VIEWS (VENDOR UI)
# ============================================================================

class HomePageView(TemplateView):
    template_name = "myoceanbasket/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_categories = Category.objects.all().prefetch_related('products')
        products = Product.objects.values('category').distinct()
        reviews = Review.objects.all()
        banners = Banner.objects.all().order_by('series')

        product_list = []
        for item in products:
            product_list = Product.objects.filter(category=item['category']).order_by('price')[:4]

        all_products = Product.objects.select_related('category').filter(
            category__isnull=False
        ).order_by('-category__name', 'price')

        grouped = defaultdict(list)
        for product in all_products:
            category_obj = product.category
            if len(grouped[category_obj]) < 20:
                grouped[category_obj].append(product)

        category_products = [
            {'category': category, 'products': prods}
            for category, prods in grouped.items()
        ]

        category_data = {}
        for category in total_categories:
            products = category.products.filter(is_active=True).distinct().values('id', 'name', 'price')[:4]
            category_data[category.id] = list(products)

        context.update({
            'is_mobile': self.request.user_agent.is_mobile,
            'reviews': reviews,
            'total_categories': total_categories,
            'products': product_list,
            'category_data': category_data,
            'banners': banners,
            'category_products': category_products
        })
        return context


class ServicesView(LoginRequiredMixin, TemplateView):
    template_name = 'vendor_ui/services.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_categories'] = Category.objects.all()
        return context


class AboutView(LoginRequiredMixin, TemplateView):
    template_name = 'vendor_ui/about-us.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_categories'] = Category.objects.all()
        return context


class BlogDetailsView(LoginRequiredMixin, TemplateView):
    template_name = 'vendor_ui/blog-details.html'


class BlogView(LoginRequiredMixin, TemplateView):
    template_name = 'vendor_ui/blog.html'


class BMICalculatorView(LoginRequiredMixin, TemplateView):
    template_name = 'vendor_ui/bmi-calculator.html'


class ClassDetailsView(LoginRequiredMixin, TemplateView):
    template_name = 'vendor_ui/class-details.html'


class ClassTimetableView(LoginRequiredMixin, TemplateView):
    template_name = 'vendor_ui/class-timetable.html'


class ContactView(LoginRequiredMixin, TemplateView):
    template_name = 'vendor_ui/contact.html'


class GalleryView(LoginRequiredMixin, TemplateView):
    template_name = 'vendor_ui/gallery.html'


class TeamView(LoginRequiredMixin, TemplateView):
    template_name = 'vendor_ui/team.html'


class Error404View(LoginRequiredMixin, TemplateView):
    template_name = 'vendor_ui/404.html'