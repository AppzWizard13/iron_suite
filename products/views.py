from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from core.models import Configuration
from .models import Category, subcategory, Product
from .forms import CategoryForm, subcategoryForm, ProductForm
from django.conf import settings


class ManageItemsView(ListView):
    template_name = 'admin_panel/manage_items.html'
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['subcategories'] = subcategory.objects.all()
        context['products'] = Product.objects.all()
        return context

    def get_queryset(self):
        return None  # We're using get_context_data for multiple querysets

class CategoryListView(ListView):
    model = Category
    context_object_name = 'categories'

    def get_queryset(self):
        query = self.request.GET.get('search', '')
        if query:
            return Category.objects.filter(name__icontains=query)
        return super().get_queryset()

    def get_template_names(self):
        """ Dynamically select template based on ADMIN_PANEL_MODE setting """
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/view_category.html']
        elif admin_mode == 'standard':
            return ['admin_panel/standard.html']  # If you have a standard mode template
        else:  # Default to basic
            return ['admin_panel/categories.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('search', '')
        return context


class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'admin_panel/add_category.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Category added successfully!")
        return response
    
    def get_template_names(self):
        """ Dynamically select template based on ADMIN_PANEL_MODE setting """
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/add_category.html']
        elif admin_mode == 'standard':
            return ['admin_panel/add_category.html']  # If you have a standard mode template
        else:  # Default to basic
            return ['admin_panel/add_category.html']

    def form_invalid(self, form):
        messages.error(self.request, "There was an error adding the category. Please check the form.")
        return super().form_invalid(form)

class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'admin_panel/edit_category.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Category updated successfully!")
        return response
    
    def get_template_names(self):
        """ Dynamically select template based on ADMIN_PANEL_MODE setting """
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/edit_category.html']
        elif admin_mode == 'standard':
            return ['admin_panel/edit_category.html']  # If you have a standard mode template
        else:  # Default to basic
            return ['admin_panel/edit_category.html']

    def form_invalid(self, form):
        messages.error(self.request, "Error updating category. Please check the form.")
        return super().form_invalid(form)

class CategoryDeleteView(DeleteView):
    model = Category
    success_url = reverse_lazy('category_list')

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Category deleted successfully!")
        return super().delete(request, *args, **kwargs)

# Subcategory Views
class SubcategoryListView(ListView):
    model = subcategory
    template_name = 'admin_panel/subcategories.html'
    context_object_name = 'subcategories'

    def get_queryset(self):
        query = self.request.GET.get('search', '')
        if query:
            return subcategory.objects.filter(name__icontains=query)
        return super().get_queryset()
    
    def get_template_names(self):
        """ Dynamically select template based on ADMIN_PANEL_MODE setting """
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/subcategories.html']
        elif admin_mode == 'standard':
            return ['admin_panel/subcategories.html']  # If you have a standard mode template
        else:  # Default to basic
            return ['admin_panel/subcategories.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('search', '')
        return context

class SubcategoryCreateView(CreateView):
    model = subcategory
    template_name = 'admin_panel/add_subcategory.html'
    fields = ['name', 'description', 'category']
    success_url = reverse_lazy('subcategory_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context
    
    def get_template_names(self):
        """ Dynamically select template based on ADMIN_PANEL_MODE setting """
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/add_subcategory.html']
        elif admin_mode == 'standard':
            return ['admin_panel/add_subcategory.html']  # If you have a standard mode template
        else:  # Default to basic
            return ['admin_panel/add_subcategory.html']
        
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Subcategory added successfully!")
        return response

class SubcategoryUpdateView(UpdateView):
    model = subcategory
    template_name = 'admin_panel/edit_subcategory.html'
    fields = ['name', 'description', 'category']
    success_url = reverse_lazy('subcategory_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context
    
    def get_template_names(self):
        """ Dynamically select template based on ADMIN_PANEL_MODE setting """
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/edit_subcategory.html']
        elif admin_mode == 'standard':
            return ['admin_panel/edit_subcategory.html']  # If you have a standard mode template
        else:  # Default to basic
            return ['admin_panel/edit_subcategory.html']

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Subcategory updated successfully!")
        return response

class SubcategoryDeleteView(DeleteView):
    model = subcategory
    success_url = reverse_lazy('subcategory_list')

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Subcategory deleted successfully!")
        return super().delete(request, *args, **kwargs)

# Product Views
class ProductListView(ListView):
    model = Product
    template_name = 'admin_panel/products.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('search', '')
        category_id = self.request.GET.get('category', '')
        subcategory_id = self.request.GET.get('subcategory', '')

        if query:
            queryset = queryset.filter(name__icontains=query)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if subcategory_id:
            queryset = queryset.filter(subcategory_id=subcategory_id)
        
        return queryset
    
    def get_template_names(self):
        """ Dynamically select template based on ADMIN_PANEL_MODE setting """
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/products.html']
        elif admin_mode == 'standard':
            return ['admin_panel/products.html']  # If you have a standard mode template
        else:  # Default to basic
            return ['admin_panel/products.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['subcategories'] = subcategory.objects.all()
        context['query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_subcategory'] = self.request.GET.get('subcategory', '')
        return context

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'admin_panel/add_product.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Product added successfully!")
        return response
    
    def get_template_names(self):
        """ Dynamically select template based on ADMIN_PANEL_MODE setting """
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/add_product.html']
        elif admin_mode == 'standard':
            return ['admin_panel/add_product.html']  # If you have a standard mode template
        else:  # Default to basic
            return ['admin_panel/add_product.html']
        
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'admin_panel/edit_product.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Product updated successfully!")
        return response
    
    def get_template_names(self):
        """ Dynamically select template based on ADMIN_PANEL_MODE setting """
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        
        if admin_mode == 'advanced':
            return ['advadmin/edit_product.html']
        elif admin_mode == 'standard':
            return ['admin_panel/edit_product.html']  # If you have a standard mode template
        else:  # Default to basic
            return ['admin_panel/edit_product.html']
        
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)

class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('product_list')
    template_name = 'advadmin/product_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        product_name = product.name
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"Product '{product_name}' was successfully deleted!")
        return response

# Frontend Views
class ProductGridView(ListView):
    model = Product
    template_name = 'product_detail_view.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('search', '')
        category_id = self.kwargs.get('category_id') or self.request.GET.get('category', '')
        subcategory_id = self.request.GET.get('subcategory', '')

        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(product_uid__icontains=query))
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if subcategory_id:
            queryset = queryset.filter(subcategory_id=subcategory_id)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['total_categories'] = Category.objects.all()
        context['subcategories'] = subcategory.objects.all()
        context['query'] = self.request.GET.get('search', '')
        context['selected_category'] = str(self.kwargs.get('category_id') or self.request.GET.get('category', ''))
        context['selected_subcategory'] = str(self.request.GET.get('subcategory', ''))
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

    def get_object(self):
        sku = self.kwargs['sku']  # get the sku from the URL
        return get_object_or_404(Product, sku=sku)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()  # this will now return the product by SKU

        context['enable_cart'] = Configuration.objects.get(config="enable-cart")
        context['total_categories'] = Category.objects.all()
        context['same_category_products'] = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:8]
        context['same_subcategory_products'] = Product.objects.filter(
            subcategory=product.subcategory
        ).exclude(id=product.id)[:8] if product.subcategory else []

        return context
    
from .models import Package
from .forms import PackageForm  # You need to create this form

class PackageListView(ListView):
    model = Package
    form_class = PackageForm
    context_object_name = 'packages'

    def get_queryset(self):
        query = self.request.GET.get('search', '')
        if query:
            return Package.objects.filter(name__icontains=query)
        return super().get_queryset()

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/view_package.html']
        elif admin_mode == 'standard':
            return ['admin_panel/packages_standard.html']
        return ['admin_panel/packages.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('search', '')
        context['page_name'] = "package_list"
        return context


class PackageCreateView(CreateView):
    model = Package
    form_class = PackageForm
    template_name = 'admin_panel/add_package.html'
    success_url = reverse_lazy('package_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Package added successfully!")
        return response

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/add_package.html']
        elif admin_mode == 'standard':
            return ['admin_panel/add_package_standard.html']
        return ['admin_panel/add_package.html']

    def form_invalid(self, form):
        messages.error(self.request, "There was an error adding the package. Please check the form.")
        return super().form_invalid(form)


class PackageUpdateView(UpdateView):
    model = Package
    form_class = PackageForm
    template_name = 'admin_panel/edit_package.html'
    success_url = reverse_lazy('package_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Package updated successfully!")
        return response

    def get_template_names(self):
        admin_mode = getattr(settings, 'ADMIN_PANEL_MODE', 'basic').lower()
        if admin_mode == 'advanced':
            return ['advadmin/edit_package.html']
        elif admin_mode == 'standard':
            return ['admin_panel/edit_package_standard.html']
        return ['admin_panel/edit_package.html']

    def form_invalid(self, form):
        messages.error(self.request, "Error updating the package. Please check the form.")
        return super().form_invalid(form)


class PackageDeleteView(DeleteView):
    model = Package
    success_url = reverse_lazy('package_list')

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Package deleted successfully!")
        return super().delete(request, *args, **kwargs)