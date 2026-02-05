from django.urls import path
from . import views

app_name = 'ecommerce'

urlpatterns = [
    # Customer Addresses
    path('addresses/', views.CustomerAddressListView.as_view(), name='customer_address_list'),
    path('addresses/<int:id>/delete/', views.CustomerAddressDeleteView.as_view(), name='customer_address_delete'),
    
    # Carts
    path('carts/', views.CartListView.as_view(), name='cart_list'),
    path('carts/<int:id>/delete/', views.CartDeleteView.as_view(), name='cart_delete'),
    
    # Wishlists
    path('wishlists/', views.WishlistListView.as_view(), name='wishlist_list'),
    path('wishlists/<int:id>/delete/', views.WishlistDeleteView.as_view(), name='wishlist_delete'),
    
    # Orders
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/<str:order_number>/delete/', views.OrderDeleteView.as_view(), name='order_delete'),
    
    # Order Items
    path('order-items/', views.OrderItemListView.as_view(), name='order_item_list'),
    path('order-items/<int:id>/delete/', views.OrderItemDeleteView.as_view(), name='order_item_delete'),
    
    # Order Status History
    path('order-status-history/', views.OrderStatusHistoryListView.as_view(), name='order_status_history_list'),
    
    # Transactions
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    
    # Invoices
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    
    # Riders
    path('riders/', views.RiderListView.as_view(), name='rider_list'),
    path('riders/<int:id>/delete/', views.RiderDeleteView.as_view(), name='rider_delete'),
    
    # Reviews
    path('reviews/', views.ReviewListView.as_view(), name='review_list'),
    path('reviews/<int:id>/delete/', views.ReviewDeleteView.as_view(), name='review_delete'),
    
    # AJAX Endpoints
    path('addresses/toggle-active/', views.ToggleCustomerAddressActive.as_view(), name='toggle_customer_address_active'),
    path('orders/toggle-status/', views.ToggleOrderStatus.as_view(), name='toggle_order_status'),
    path('riders/toggle-active/', views.ToggleRiderActive.as_view(), name='toggle_rider_active'),

    path('orders/assign-rider/', views.AssignRiderView.as_view(), name='assign_rider'),
]
