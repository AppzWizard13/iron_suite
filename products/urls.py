from django.urls import path
from .views import (
    ManageItemsView,
    CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView,
    SubcategoryListView, SubcategoryCreateView, SubcategoryUpdateView, SubcategoryDeleteView,
    ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView,
    ProductGridView, ProductDetailView,    PackageListView, PackageCreateView,
    PackageUpdateView, PackageDeleteView
)
from accounts.views import FetchProductsView

urlpatterns = [
    path('manage-items/', ManageItemsView.as_view(), name='manage_items'),

    # Category URLs
    path('add-category/', CategoryCreateView.as_view(), name='add_category'),
    path('edit-category/<int:pk>/', CategoryUpdateView.as_view(), name='edit_category'),
    path('delete-category/<int:pk>/', CategoryDeleteView.as_view(), name='delete_category'),

    # Subcategory URLs
    path('add-subcategory/', SubcategoryCreateView.as_view(), name='add_subcategory'),
    path('edit-subcategory/<int:pk>/', SubcategoryUpdateView.as_view(), name='edit_subcategory'),
    path('delete-subcategory/<int:pk>/', SubcategoryDeleteView.as_view(), name='delete_subcategory'),

    # Product URLs
    path('product/add/', ProductCreateView.as_view(), name='add_product'),
    path('product/edit/<int:pk>/', ProductUpdateView.as_view(), name='edit_product'),
    path('product/delete/<int:pk>/', ProductDeleteView.as_view(), name='delete_product'),

    # List Views
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('subcategories/', SubcategoryListView.as_view(), name='subcategory_list'),
    path('products/', ProductListView.as_view(), name='product_list'),

    # Frontend Views
    path('products-grid/', ProductGridView.as_view(), name='product_grid_view'),
    path('products/<slug:sku>/', ProductDetailView.as_view(), name='product_detail'),
    path('category/<int:category_id>/', ProductGridView.as_view(), name='products_by_category'),

    # API View
    path('fetch-products/<int:category_id>/', FetchProductsView.as_view(), name='fetch_products'),
    path('packages/', PackageListView.as_view(), name='package_list'),
    path('packages/add/', PackageCreateView.as_view(), name='package_add'),
    path('packages/edit/<int:pk>/', PackageUpdateView.as_view(), name='package_edit'),
    path('packages/delete/<int:pk>/', PackageDeleteView.as_view(), name='package_delete'),
]

