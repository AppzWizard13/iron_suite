from django.urls import path
from . import views

app_name = 'master'

urlpatterns = [
    # --- CATEGORY URLS ---
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # --- SUBCATEGORY URLS ---
    path('subcategories/', views.SubCategoryListView.as_view(), name='subcategory_list'),
    path('subcategories/add/', views.SubCategoryCreateView.as_view(), name='subcategory_create'),
    path('subcategories/<int:pk>/edit/', views.SubCategoryUpdateView.as_view(), name='subcategory_update'),
    path('subcategories/<int:pk>/delete/', views.SubCategoryDeleteView.as_view(), name='subcategory_delete'),

    # Products
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # Discounts
    path('discounts/', views.DiscountListView.as_view(), name='discount_list'),
    path('discounts/add/', views.DiscountCreateView.as_view(), name='discount_create'),
    
    # Delivery Zones
    path('delivery-zones/', views.DeliveryZoneListView.as_view(), name='delivery_zone_list'),
    path('delivery-zones/<int:pk>/edit/', views.DeliveryZoneUpdateView.as_view(), name='delivery_zone_update'),
]
