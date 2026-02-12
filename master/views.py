from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Category, SubCategory, Product, Discount, DeliveryZone
from .forms import CategoryForm, SubCategoryForm, ProductForm, DiscountForm, DeliveryZoneForm

class SoftDeleteMixin:
    """Toggles is_active to False instead of deleting from DB."""
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        return redirect(self.get_success_url())

# --- CATEGORY VIEWS ---
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'master/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'master/category_form.html'
    success_url = reverse_lazy('master:category_list')

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'master/category_form.html'
    success_url = reverse_lazy('master:category_list')

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('master:category_list')
    
    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        messages.success(request, f'Category "{category.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)


# --- SUBCATEGORY VIEWS ---
class SubCategoryListView(LoginRequiredMixin, ListView):
    model = SubCategory
    template_name = 'master/subcategory_list.html'
    context_object_name = 'subcategories'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset.select_related('category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['selected_category'] = self.request.GET.get('category', '')
        return context


class SubCategoryCreateView(LoginRequiredMixin, CreateView):
    model = SubCategory
    form_class = SubCategoryForm
    template_name = 'master/subcategory_form.html'
    success_url = reverse_lazy('master:subcategory_list')
    
    def get_initial(self):
        initial = super().get_initial()
        # Pre-select category if passed in URL
        category_id = self.request.GET.get('category')
        if category_id:
            try:
                initial['category'] = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = False
        return context


class SubCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = SubCategory
    form_class = SubCategoryForm
    template_name = 'master/subcategory_form.html'
    success_url = reverse_lazy('master:subcategory_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context


class SubCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = SubCategory
    success_url = reverse_lazy('master:subcategory_list')
    
    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        subcategory = self.get_object()
        messages.success(request, f'SubCategory "{subcategory.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)



# --- PRODUCT VIEWS (With Vendor Isolation) ---
class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'master/product_list.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_superuser and hasattr(self.request.user, 'vendor'):
            qs = qs.filter(vendor=self.request.user.vendor)
        return qs

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'master/product_form.html'
    success_url = reverse_lazy('master:product_list')

    def form_valid(self, form):
        # Automatically assign the vendor on save
        if not self.request.user.is_superuser:
            form.instance.vendor = self.request.user.vendor
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'master/product_form.html'
    success_url = reverse_lazy('master:product_list')

class ProductDeleteView(LoginRequiredMixin, SoftDeleteMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('master:product_list')
    template_name = 'master/confirm_delete.html'

# --- DISCOUNT VIEWS ---
class DiscountListView(LoginRequiredMixin, ListView):
    model = Discount
    template_name = 'master/discount_list.html'

class DiscountCreateView(LoginRequiredMixin, CreateView):
    model = Discount
    form_class = DiscountForm
    template_name = 'master/discount_form.html'
    success_url = reverse_lazy('master:discount_list')

# --- DELIVERY ZONE VIEWS ---
class DeliveryZoneListView(LoginRequiredMixin, ListView):
    model = DeliveryZone
    template_name = 'master/delivery_zone_list.html'

class DeliveryZoneUpdateView(LoginRequiredMixin, UpdateView):
    model = DeliveryZone
    form_class = DeliveryZoneForm
    template_name = 'master/delivery_zone_form.html'
    success_url = reverse_lazy('master:delivery_zone_list')
