from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DetailView, View, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse, FileResponse
from django.conf import settings
from django.db.models import Max
import os
import zipfile
from io import BytesIO
import logging

from core.models import BusinessDetails, Configuration
from products.models import Product, Category, subcategory
from enquiry.models import Enquiry
from .models import CustomUser, Banner, Review
from .forms import CustomUserForm, CustomerRegistrationForm, MemberRegistrationForm, ReviewForm, BannerForm, ProfileUpdateForm
from django.contrib.auth import logout, login
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

from orders.models import Transaction, Order
from django.utils import timezone
from datetime import timedelta
from django.db import models 
from .forms import UserLoginForm
logger = logging.getLogger(__name__)
CustomUser = get_user_model()
from django.contrib.auth.mixins import LoginRequiredMixin

class UserCreateView(LoginRequiredMixin, CreateView):
    model = CustomUser
    form_class = CustomUserForm
    success_url = reverse_lazy('user_list')

    # Redirect unauthenticated users to login page
    login_url = 'login'  # <-- Uses your existing login URL
    redirect_field_name = 'next'  # Default: keeps track of where to return after login

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()

        if admin_mode == 'advanced':
            return ['advadmin/create_user.html']
        elif admin_mode == 'standard':
            return ['admin_panel/authentication-register-standard.html']
        else:
            return ['admin_panel/add_user.html']

    def form_valid(self, form):
        try:
            user = form.save(commit=False)

            if 'password1' in form.cleaned_data:
                user.set_password(form.cleaned_data['password1'])

            max_member_id = CustomUser.objects.aggregate(Max('member_id'))['member_id__max'] or 0
            user.member_id = max_member_id + 1
            user.username = self.generate_username(user.member_id)

            user.save()
            messages.success(self.request, "User added successfully.")
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"An error occurred: {str(e)}")
            return self.form_invalid(form)

    def generate_username(self, member_id):
        return f"MEMBER{str(member_id).zfill(5)}"


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = CustomUserForm
    template_name = 'admin_panel/manage_user.html'
    success_url = reverse_lazy('user_list')
    slug_field = "username"
    slug_url_kwarg = "username"

    def form_valid(self, form):
        user = form.save(commit=False)

        # Get password only if provided
        password = form.cleaned_data.get("password1")  # Use 'password1' instead of 'password'
        if password:
            user.set_password(password)  # Only set password if it's provided

        user.save()
        messages.success(self.request, "User updated successfully.")
        return super().form_valid(form)

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
            return ['advadmin/ironsuite-auth-login-basic.html']
        elif admin_mode == 'standard':
            return ['admin_panel/authentication-login-standard.html']
        else:
            return ['admin_panel/authentication-login-basic.html']

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        # ✅ Remember Me functionality
        remember_me = self.request.POST.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)  # Expires on browser close
        else:
            self.request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days

        messages.success(self.request, "Login successful!")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Invalid credentials. Please try again.",
            extra_tags='danger'
        )
        return self.render_to_response(self.get_context_data(form=form))



from django.views.generic import ListView
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class UserListView(ListView):
    model = User
    template_name = 'admin_panel/user_list.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        # Base queryset filtered by staff_role = 'Customer'
        queryset = super().get_queryset().filter(staff_role__iexact='Member')

        search_query = self.request.GET.get('q')
        sort_param = self.request.GET.get('sort')

        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(member_id__icontains=search_query) |
                Q(phone_number__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        # Sorting
        if sort_param == 'name':
            queryset = queryset.order_by('first_name', 'last_name')
        elif sort_param == '-name':
            queryset = queryset.order_by('-first_name', '-last_name')
        elif sort_param == 'member_id':
            queryset = queryset.order_by('member_id')
        elif sort_param == '-member_id':
            queryset = queryset.order_by('-member_id')
        else:
            queryset = queryset.order_by('-date_joined')  # default sort

        return queryset

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()

        if admin_mode == 'advanced':
            return ['advadmin/manage_user.html']
        elif admin_mode == 'standard':
            return ['admin_panel/manage_user.html']
        return ['admin_panel/manage_user.html']


from django.views.generic import ListView
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class UserStaffRoleListView(ListView):
    model = User
    template_name = 'admin_panel/user_list.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        role = self.kwargs.get('role')
        queryset = User.objects.filter(staff_role__iexact=role)

        search_query = self.request.GET.get('q')
        sort_param = self.request.GET.get('sort')

        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(member_id__icontains=search_query) |
                Q(phone_number__icontains=search_query) |
                Q(email__icontains=search_query)
            )

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

        if admin_mode == 'advanced':
            return ['advadmin/manage_user.html']
        elif admin_mode == 'standard':
            return ['admin_panel/manage_user.html']
        return ['admin_panel/manage_user.html']

class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomUser
    slug_field = "username"
    slug_url_kwarg = "username"
    success_url = reverse_lazy('user_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'User has been deleted successfully.')
        return super().delete(request, *args, **kwargs)
    

# Home Page View
class HomePageView(TemplateView):
    template_name = "gym_ui/index.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_categories = Category.objects.all().prefetch_related('products')
        products = Product.objects.values('category').distinct()
        reviews = Review.objects.all()
        banners = Banner.objects.all().order_by('series')

        product_list = []
        category_products = []
        for item in products:
            product_list = Product.objects.filter(category=item['category']).order_by('price')[:4]


        # Step 1: Fetch all products with valid category (ForeignKey)
        all_products = Product.objects.select_related('category').filter(category__isnull=False).order_by('-category__name', 'price')
        from collections import defaultdict
        # Step 2: Group by category object (not string)
        grouped = defaultdict(list)

        for product in all_products:
            category_obj = product.category
            if len(grouped[category_obj]) < 20:
                grouped[category_obj].append(product)

        # Step 3: Prepare context list
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
    

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import get_user_model
import json

User = get_user_model()

@require_POST
@login_required
@csrf_exempt  # Only needed if you're still having CSRF issues
def toggle_user_active(request):
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        user_id = data.get('user_id')
        action = data.get('action')
        
        if not user_id or action not in ['block', 'unblock']:
            return JsonResponse({
                'success': False,
                'message': 'Invalid parameters'
            }, status=400)
        
        user = User.objects.get(username=user_id)
        user.is_active = (action == 'unblock')
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': f'User {"unblocked" if user.is_active else "blocked"} successfully',
            'is_active': user.is_active
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
    

from django.views.generic import ListView
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

User = get_user_model()

class BlockedUserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'advadmin/blocked_users.html'
    permission_required = 'auth.change_user'
    context_object_name = 'users'
    
    def get_queryset(self):
        return User.objects.filter(is_active=False).order_by('-date_joined')

class UnblockUserView(LoginRequiredMixin, View):
    permission_required = 'auth.change_user'
    
    def post(self, request, *args, **kwargs):
        username = kwargs.get('username')
        try:
            user = User.objects.get(username=username)
            user.is_active = True
            user.save()
            return JsonResponse({
                'success': True,
                'message': f'User {username} has been unblocked successfully'
            })
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'User not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)

# API View
class FetchProductsView(View):
    def get(self, request, *args, **kwargs):
        category_id = self.kwargs['category_id']
        products = Product.objects.filter(
            category_id=category_id, 
            is_active=True
        ).values('id', 'name', 'price', 'sku')
        return JsonResponse(list(products), safe=False)



class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('login')


from core.models import Configuration
class DashboardView(LoginRequiredMixin, TemplateView):
    

    """
    Dashboard view that changes based on ADMIN_PANEL_MODE setting
    """
    # Default template (will be overridden based on mode)
    template_name = 'admin_panel/index.html'  
    
    def get_template_names(self):
        """
        Determine which template to use based on ADMIN_PANEL_MODE
        """
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/index.html']
        elif admin_mode == 'standard':
            return ['admin_panel/standard.html']  # Add if you have this
        else:  # basic or any other value
            return ['admin_panel/index.html']
        
    def get_context_data(self, **kwargs):
        from django.db.models import Sum, Q, Count
        context = super().get_context_data(**kwargs)

        configs = Configuration.objects.all()
        # Convert to dictionary with safe variable names for templates
        config_dict = {
            conf.config.replace("-", "_"): conf.value for conf in configs
        }
        transactions = Transaction.objects.all()

        total_sales_amount = transactions.filter(
            category=Transaction.Category.SALES,
            transaction_type=Transaction.Type.INCOME,
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_completed_amount = transactions.filter(
            status=Transaction.Status.COMPLETED
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_transaction_amount = transactions.aggregate(total=Sum('amount'))['total'] or 0

        total_income = transactions.filter(
            transaction_type=Transaction.Type.INCOME
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_expense = transactions.filter(
            transaction_type=Transaction.Type.EXPENSE
        ).aggregate(total=Sum('amount'))['total'] or 0

        profit = total_income - total_expense

        # Orders related counts
        active_users_count = CustomUser.objects.filter(staff_role='Member', is_active = True).count()
        orders = Order.objects.values('status').annotate(count=Count('id'))

        # Initialize all as 0
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
            status = order['status']
            count = order['count']
            total_orders += count

            if status == Order.Status.PENDING:
                order_status_counts['pending_orders'] = count
            elif status == Order.Status.PROCESSING:
                order_status_counts['processing_orders'] = count
            elif status == Order.Status.SHIPPED:
                order_status_counts['shipped_orders'] = count
            elif status == Order.Status.DELIVERED:
                order_status_counts['delivered_orders'] = count
            elif status == Order.Status.CANCELLED:
                order_status_counts['cancelled_orders'] = count
            elif status == Order.Status.RETURN:
                order_status_counts['returned_orders'] = count

        # --- Final base context ---
        print("config_dictconfig_dict", config_dict)
        base_context = {
            **config_dict,
            'active_users_count': active_users_count,
            'total_sales_amount': total_sales_amount,
            'total_completed_amount': total_completed_amount,
            'total_transaction_amount': total_transaction_amount,
            'profit': profit,
            'total_products': Product.objects.all(),
            'total_products_count': Product.objects.count(),
            'total_categories': Category.objects.all(),
            'total_subcategories': subcategory.objects.all(),
            'total_enquiries': Enquiry.objects.count(),
            'total_cat_count': Category.objects.count(),
            'total_subcat_count': subcategory.objects.count(),
            'total_orders': total_orders,
            'admin_mode': getattr(settings, 'ADMIN_PANEL_MODE', 'basic'),
        }

        base_context.update(order_status_counts)

        context.update(base_context)
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

# Static Pages
class ServicesView(TemplateView):
    template_name = 'gym_ui/services.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_categories'] = Category.objects.all()
        return context

class AboutView(TemplateView):
    template_name = 'gym_ui/about-us.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['total_categories'] = Category.objects.all()
        return context

# Review Management Views
class ReviewListView(LoginRequiredMixin, ListView):
    model = Review
    template_name = 'admin_panel/review_list.html'
    context_object_name = 'reviews'

    def get_template_names(self):
        """
        Determine which template to use based on ADMIN_PANEL_MODE
        """
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/review_list.html']
        elif admin_mode == 'standard':
            return ['admin_panel/review_list.html']  # Add if you have this
        else:  # basic or any other value
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
        """
        Determine which template to use based on ADMIN_PANEL_MODE
        """
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/review_form.html']
        elif admin_mode == 'standard':
            return ['admin_panel/review_form.html']  # Add if you have this
        else:  # basic or any other value
            return ['admin_panel/review_form.html']

    def form_invalid(self, form):
        messages.error(self.request, "There was an error adding the review. Please check the form.")
        return super().form_invalid(form)

class ReviewDetailView(LoginRequiredMixin, DetailView):
    model = Review
    template_name = 'admin_panel/review_detail.html'
    context_object_name = 'review'

    def get_template_names(self):
        """
        Determine which template to use based on ADMIN_PANEL_MODE
        """
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/review_detail.html']
        elif admin_mode == 'standard':
            return ['admin_panel/review_detail.html']  # Add if you have this
        else:  # basic or any other value
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
        """
        Determine which template to use based on ADMIN_PANEL_MODE
        """
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/review_form.html']
        elif admin_mode == 'standard':
            return ['admin_panel/review_form.html']  # Add if you have this
        else:  # basic or any other value
            return ['admin_panel/review_form.html']

    def form_invalid(self, form):
        messages.error(self.request, "Error updating review. Please check the form.")
        return super().form_invalid(form)


class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    model = Review
    success_url = reverse_lazy('review_list')
    template_name = None  # This tells Django not to look for a template

    def get(self, request, *args, **kwargs):
        """
        Skip the confirmation template and go straight to deletion
        """
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Handle the actual deletion and show success message
        """
        messages.success(request, "Review deleted successfully!")
        return super().delete(request, *args, **kwargs)

# Banner Management Views
class BannerListView(LoginRequiredMixin, ListView):
    model = Banner
    template_name = 'admin_panel/banner_list.html'
    context_object_name = 'banners'

    def get_template_names(self):
        """
        Determine which template to use based on ADMIN_PANEL_MODE
        """
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/banner_list.html']
        elif admin_mode == 'standard':
            return ['admin_panel/banner_list.html']  # Add if you have this
        else:  # basic or any other value
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
        """
        Determine which template to use based on ADMIN_PANEL_MODE
        """
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/banner_form.html']
        elif admin_mode == 'standard':
            return ['admin_panel/banner_form.html']  # Add if you have this
        else:  # basic or any other value
            return ['admin_panel/banner_form.html']

    def form_invalid(self, form):
        messages.error(self.request, "There was an error adding the banner. Please check the form.")
        return super().form_invalid(form)

class BannerDetailView(LoginRequiredMixin, DetailView):
    model = Banner
    template_name = 'admin_panel/banner_detail.html'
    context_object_name = 'banner'

    def get_template_names(self):
        """
        Determine which template to use based on ADMIN_PANEL_MODE
        """
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/banner_form.html']
        elif admin_mode == 'standard':
            return ['admin_panel/banner_form.html']  # Add if you have this
        else:  # basic or any other value
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
        """
        Determine which template to use based on ADMIN_PANEL_MODE
        """
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/banner_form.html']
        elif admin_mode == 'standard':
            return ['admin_panel/banner_form.html']  # Add if you have this
        else:  # basic or any other value
            return ['admin_panel/banner_form.html']

    def form_invalid(self, form):
        messages.error(self.request, "Error updating banner. Please check the form.")
        return super().form_invalid(form)

class BannerDeleteView(LoginRequiredMixin, DeleteView):
    model = Banner
    success_url = reverse_lazy('banner_list')
    template_name = None  # This tells Django not to look for a template

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Banner deleted successfully!")
        return super().delete(request, *args, **kwargs)
    
# Utility Views
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
        
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.views import View
from .models import PasswordResetOTP
from .forms import PasswordResetRequestForm, PasswordResetOTPForm
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Set up logging
logger = logging.getLogger(__name__)

User = get_user_model()

class PasswordResetRequestView(View):
    template_name = 'advadmin/auth-forgot-password-basic.html'
    
    def get(self, request):
        return render(request, self.template_name, {'form': PasswordResetRequestForm()})
    
    def post(self, request):
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                
                # Delete any existing unused OTPs for this user
                PasswordResetOTP.objects.filter(
                    user=user,
                    is_used=False
                ).delete()
                
                # Generate new OTP
                otp = ''.join(random.choices(string.digits, k=6))  # 6-digit OTP
                expires_at = timezone.now() + timezone.timedelta(minutes=15)
                otp_obj = PasswordResetOTP.objects.create(
                    user=user,
                    otp=otp,
                    expires_at=expires_at
                )
                
                # Email content
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
                
                # SMTP Configuration
                smtp_server = "smtp.gmail.com"
                smtp_port = 587
                smtp_username = settings.EMAIL_HOST_USER
                smtp_password = settings.EMAIL_HOST_PASSWORD
                
                # Create message
                msg = MIMEMultipart()
                msg['From'] = settings.DEFAULT_FROM_EMAIL
                msg['To'] = email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))
                
                try:
                    # Send email using SMTP
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
            
            except User.DoesNotExist:
                # Don't reveal whether email exists or not for security
                messages.success(request, "If an account exists with this email, we've sent an OTP.")
                logger.info(f"Password reset requested for non-existent email: {email}")
                return redirect('password_reset_request')
        
        # Form is invalid
        logger.warning(f"Invalid form submission: {form.errors}")
        return render(request, self.template_name, {'form': form})

class PasswordResetVerifyView(View):
    template_name = 'advadmin/auth-reset-password-basic.html'
    
    def get(self, request, user_username):
        try:
            # Use username field instead of pk
            user = User.objects.get(username=user_username)
            return render(request, self.template_name, {
                'form': PasswordResetOTPForm(),
                'user_username': user_username
            })
        except User.DoesNotExist:
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
                # Use username field instead of pk
                user = User.objects.get(username=user_username)
                otp_obj = PasswordResetOTP.objects.get(
                    user=user,
                    otp=otp,
                    is_used=False,
                    expires_at__gt=timezone.now()
                )
                
                # Update password
                user.set_password(new_password1)
                user.save()
                
                # Mark OTP as used
                otp_obj.is_used = True
                otp_obj.save()
                
                # Invalidate all other OTPs for this user
                PasswordResetOTP.objects.filter(
                    user=user,
                    is_used=False
                ).update(is_used=True)
                
                messages.success(request, "Password reset successfully. You can now login with your new password.")
                return redirect('login')
            
            except User.DoesNotExist:
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
    


User = get_user_model()

class AccountSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'advadmin/pages-account-settings-account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
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
    
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView, DeleteView
)
from django.conf import settings
from .models import SocialMedia
from .forms import SocialMediaForm

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
        elif admin_mode == 'standard':
            return ['admin_panel/socialmedia_list.html']
        else:
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
        elif admin_mode == 'standard':
            return ['admin_panel/socialmedia_form.html']
        else:
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
        elif admin_mode == 'standard':
            return ['admin_panel/socialmedia_detail.html']
        else:
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
        elif admin_mode == 'standard':
            return ['admin_panel/socialmedia_form.html']
        else:
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
    
import logging
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

# Create a logger for your app
logger = logging.getLogger(__name__)

def get_company_data(request):
    try:
        # Fetch the first available BusinessDetails entry
        company = BusinessDetails.objects.first()
        category_names = list(Category.objects.values_list('name', flat=True))


        if not company:
            return JsonResponse({'error': 'No company data found'}, status=404)

        # Prepare data safely
        data = {
            'company_name': company.company_name,
            'gstn': company.gstn,
            'breadcrumb_image_url': company.breadcrumb_image.url if company.breadcrumb_image else None,
            'about_page_image_url': company.about_page_image.url if company.about_page_image else None,
            'company_tagline': company.company_tagline,
            'company_logo_svg_url': company.company_logo_svg.url if company.company_logo_svg else None,
            'company_logo_url': company.company_logo.url if company.company_logo else None,
            'company_favicon_url': company.company_favicon.url if company.company_favicon else None,
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
            'opening_time': company.opening_time.strftime('%H:%M:%S') if company.opening_time else None,
            'closing_time': company.closing_time.strftime('%H:%M:%S') if company.closing_time else None,
            'closed_days': company.closed_days.split(',') if company.closed_days else [],
            'category_names': category_names

        }

        return JsonResponse(data)

    except ObjectDoesNotExist as e:
        # Log the error if the object is not found or some data is missing
        logger.error(f"ObjectDoesNotExist Error: {str(e)} - Failed to fetch company data.")
        return JsonResponse({'error': 'Company data not found or missing fields'}, status=500)

    except Exception as e:
        # Catch any other exceptions and log the error
        logger.error(f"Error while processing company data: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred while processing company data'}, status=500)



from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from .forms import CustomerRegistrationForm
from accounts.models import Customer

User = get_user_model()

class CustomerCreateView(View):
    template_name = 'advadmin/customer_registration.html'

    def get(self, request):
        users = User.objects.all()
        form = CustomerRegistrationForm()
        return render(request, self.template_name, {'form': form, 'users': users})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer created successfully!")
            return redirect('customer_registration')  # Redirect to the same page or another page
        else:
            messages.error(request, "Error creating customer.")
            print("Form errors:", form.errors)  # Print form errors for debugging
        return render(request, self.template_name, {'form': form, 'users': User.objects.all()})
    

from django.urls import reverse
from django.views.generic.edit import CreateView
from django.contrib import messages

class MemberRegisterView(CreateView):
    model = CustomUser
    form_class = MemberRegistrationForm
    success_url = reverse_lazy('user_list')  # Fallback, but you won't use it now

    def get_template_names(self):
        return ['advadmin/member_registration.html']

    def form_valid(self, form):
        try:
            user = form.save(commit=False)
            user.staff_role = 'Member'
            if form.cleaned_data.get('password1'):
                user.set_password(form.cleaned_data['password1'])
            user.save()

            # Fetch the selected package
            package = form.cleaned_data['package']

            # Store the new user ID and package ID in session (so payment view can access it)
            self.request.session['pending_member_member_id'] = user.member_id
            self.request.session['pending_package_id'] = package.id

            # Message for the user
            messages.success(
                self.request,
                "Please complete package payment to activate membership."
            )

            # Redirect to payment initiation view
            return redirect('initiate_subscription_payment')

        except Exception as e:
            messages.error(self.request, f"Error: {str(e)}")
            return self.form_invalid(form)


import random
from django.shortcuts import render, redirect 
from django.views import View
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from twilio.rest import Client
from django.conf import settings
from django.core.mail import send_mail

class LoginWithOTPView(View):
    template_name = 'advadmin/login_with_otp.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        phone_number = request.POST.get('phone_number')
        
        if not phone_number:
            messages.error(request, "Phone number is required")
            return render(request, self.template_name)
        
        # Check if user exists
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            messages.error(request, "No user found with the corresponding phone number.")
            return render(request, self.template_name)
        
        email = user.email
        
        # Generate a 6-digit OTP
        otp = str(random.randint(100000, 999999))
        valid_until = timezone.now() + timedelta(minutes=5)
        
        # Store OTP in session
        request.session['otp'] = otp
        request.session['otp_valid_until'] = valid_until.isoformat()
        request.session['phone_number'] = phone_number
        
        # Retrieve both configurations in a single query
        configs = Configuration.objects.filter(config__in=["enable-emailotp", "enable-smsotp"])

        # Initialize a dictionary to store the configuration values
        config_values = {config.config: config.value for config in configs}

        # Helper function to convert string to boolean
        def str_to_bool(value):
            return value.lower() in ("true", "1", "yes", "on")

        # Check the configuration values and send OTP accordingly
        if str_to_bool(config_values.get("enable-emailotp", "False")):
            self.send_otp_via_email(email, otp)

        if str_to_bool(config_values.get("enable-smsotp", "False")):
            self.send_otp_via_twilio(phone_number, otp)
        
        return redirect('verify_otp')
    
    def send_otp_via_email(self, email, otp):
        subject = f"OTP for {settings.SITE_NAME}"
        body = f"""
        Dear User,
        
        Your OTP for logging in to {settings.SITE_NAME} is:
        
        OTP: {otp}
        
        This OTP is valid for 5 minutes.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        {settings.SITE_NAME} Team
        """
        
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
        stored_otp = request.session.get('otp')
        print("stored_otpstored_otpstored_otpstored_otp", stored_otp)
        if 'phone_number' not in request.session:
            messages.error(request, "Session expired. Please request OTP again.")
            return redirect('login_with_otp')
        return render(request, self.template_name)
    
    def post(self, request):
        user_otp = request.POST.get('otp')
        phone_number = request.session.get('phone_number')
        stored_otp = request.session.get('otp')
        print("stored_otpstored_otpstored_otpstored_otp", stored_otp)
        otp_valid_until = request.session.get('otp_valid_until')
        
        if not all([user_otp, stored_otp, otp_valid_until]):
            messages.error(request, "Session expired. Please request OTP again.")
            return redirect('login_with_otp')
        
        # Check if OTP is expired
        if timezone.now() > timezone.datetime.fromisoformat(otp_valid_until):
            messages.error(request, "OTP has expired. Please request a new one.")
            return redirect('login_with_otp')
        
        # Verify OTP
        if user_otp == stored_otp:
            # OTP is valid - get or create user
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                messages.error(request, "No user found with the corresponding phone number.")
                return render(request, self.template_name)
            
            # Log the user in
            login(request, user)
            
            # Clear session data
            request.session.pop('otp', None)
            request.session.pop('otp_valid_until', None)
            request.session.pop('phone_number', None)
            
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


import requests
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class GoogleSSOCallbackView(View):
    def get(self, request):
        code = request.GET.get('code')
        if not code:
            messages.error(request, "Authorization code not found.")
            return redirect('/login/')

        # Step 1: Exchange code for access token
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

        # Step 2: Fetch user info
        user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        user_info_response = requests.get(user_info_url, params={'alt': 'json'}, headers={
            'Authorization': f'Bearer {access_token}'
        })
        user_info = user_info_response.json()

        email = user_info.get('email')
        name = user_info.get('name')

        if not email:
            messages.error(request, "Email not found in Google profile.")
            return redirect('/login/')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User not registered. Please sign up first.")
            return redirect('/login/')

        # Optional update name
        if user.first_name != name:
            user.first_name = name
            user.save()

        # Important: set backend
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        return redirect('/dashboard/')
