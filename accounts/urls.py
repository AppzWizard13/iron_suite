from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    HomePageView, CustomLoginView, DashboardView, DashboardSearchView, LoginWithOTPView,
    LogoutView, OTPLoginSuccessView, ServicesView, AboutView, DownloadDatabaseView,
    UserListView,UserStaffRoleListView, UserCreateView, UserUpdateView, UserDeleteView,
    ReviewListView, ReviewCreateView, ReviewDetailView, ReviewUpdateView, ReviewDeleteView,
    BannerListView, BannerCreateView, BannerDetailView, BannerUpdateView, BannerDeleteView,
    DownloadAllMediaView, PasswordResetRequestView, PasswordResetVerifyView, AccountSettingsView,
    ProfileUpdateView, SocialMediaListView, SocialMediaCreateView,CustomerCreateView,
    SocialMediaDetailView, SocialMediaUpdateView, VerifyOTPView, toggle_user_active,BlockedUserListView, UnblockUserView,MemberRegisterView,
    SocialMediaDeleteView, get_company_data, login_redirect, GoogleSSOCallbackView
)
from .views import (
    BlogDetailsView, BlogView, BMICalculatorView, ClassDetailsView,
    ClassTimetableView, ContactView, GalleryView,
    ServicesView, TeamView, Error404View
)

urlpatterns = [
    # Landing page
    path('', HomePageView.as_view(), name='home'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('my-profile/', AccountSettingsView.as_view(), name='account_settings'),
    path('my-profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/verify/<str:user_username>/', PasswordResetVerifyView.as_view(), name='password_reset_verify'),

    # Dashboard search
    path('dashboard/search/', DashboardSearchView.as_view(), name='dashboard_search_list'),

    # Static pages
    path('services/', ServicesView.as_view(), name='services'),
    path('about/', AboutView.as_view(), name='about'),
    path('download-db/', DownloadDatabaseView.as_view(), name='download_database'),

    # User management
    path('users/', UserListView.as_view(), name='user_list'),
    path('staff/<slug:role>/', UserStaffRoleListView.as_view(), name='staff_by_role'),
    path('users/registartion/', UserCreateView.as_view(), name='user_registration'),
    path('users/edit/<str:username>/', UserUpdateView.as_view(), name='user_edit'),
    path('users/delete/<str:username>/', UserDeleteView.as_view(), name='user_delete'),
    path('customer/registration/', CustomerCreateView.as_view(), name='customer_registration'),

    path('member/registration/', MemberRegisterView.as_view(), name='member_registration'),
    path('toggle-active/', toggle_user_active, name='toggle_user_active'),
    path('blocked-users/', BlockedUserListView.as_view(), name='blocked_users'),
    path('unblock-user/<str:username>/', UnblockUserView.as_view(), name='unblock_user'),

    # Review management
    path('reviews/', ReviewListView.as_view(), name='review_list'),
    path('reviews/add/', ReviewCreateView.as_view(), name='review_create'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review_detail'),
    path('reviews/<int:pk>/edit/', ReviewUpdateView.as_view(), name='review_edit'),
    path('reviews/<int:pk>/delete/', ReviewDeleteView.as_view(), name='review_delete'),

    # Banner management
    path('banners/', BannerListView.as_view(), name='banner_list'),
    path('banners/create/', BannerCreateView.as_view(), name='banner_create'),
    path('banners/<int:pk>/', BannerDetailView.as_view(), name='banner_detail'),
    path('banners/<int:pk>/edit/', BannerUpdateView.as_view(), name='banner_edit'),
    path('banners/<int:pk>/delete/', BannerDeleteView.as_view(), name='banner_delete'),

    # Media download
    path('download-all-media/', DownloadAllMediaView.as_view(), name='download_all_media'),
    path('socialmedia/', SocialMediaListView.as_view(), name='socialmedia_list'),
    path('socialmedia/add/', SocialMediaCreateView.as_view(), name='socialmedia_add'),
    path('socialmedia/<int:pk>/', SocialMediaDetailView.as_view(), name='socialmedia_detail'),
    path('socialmedia/<int:pk>/edit/', SocialMediaUpdateView.as_view(), name='socialmedia_edit'),
    path('socialmedia/<int:pk>/delete/', SocialMediaDeleteView.as_view(), name='socialmedia_delete'),
    path('api/company-data/', get_company_data, name='company-data-api'),


    path('login_with_otp/', LoginWithOTPView.as_view(), name='login_with_otp'),
    path('verify_otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('otp_login_success/', OTPLoginSuccessView.as_view(), name='otp_login_success'),

    
    path('accounts/login/', login_redirect, name='account_login'),
    path('google_sso/callback/', GoogleSSOCallbackView.as_view(), name='google_callback'),






    path('blog-details/', BlogDetailsView.as_view(), name='blog-details'),
    path('blog/', BlogView.as_view(), name='blog'),
    path('bmi-calculator/', BMICalculatorView.as_view(), name='bmi-calculator'),
    path('class-details/', ClassDetailsView.as_view(), name='class-details'),
    path('class-timetable/', ClassTimetableView.as_view(), name='class-timetable'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('gallery/', GalleryView.as_view(), name='gallery'),
    path('services/', ServicesView.as_view(), name='services'),
    path('team/', TeamView.as_view(), name='team'),
    path('404/', Error404View.as_view(), name='404'),









]