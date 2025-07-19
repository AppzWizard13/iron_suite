# orders/urls.py
from django.urls import path
from . import views
from .views import AddToCartView, CartDetailView, CodOrderSuccessView, PaymentOrderSuccessView, OrderDeleteView, OrderDetailView, OrderEditView, OrderListView, ProcessPaymentView, SubscriptionOrderSuccessView, TransactionDetailView, TransactionListView, UpdateCartItemView, RemoveCartItemView, GetCartCountView, CheckoutView, OrderConfirmationView, PaymentInitiateProcess, PaymentOrderFailView

urlpatterns = [
    path('cart/view/', AddToCartView.as_view(), name='cart_view'),
    # path('cart/', CartDetailView.as_view(), name='cart_detail'),
    path('update-cart-item/', UpdateCartItemView.as_view(), name='update_cart_item'),
    path('remove-cart-item/', RemoveCartItemView.as_view(), name='remove_cart_item'),

    path('update-cart/', AddToCartView.as_view(), name='update_cart'),  # Fo
    path('get-cart-count/', GetCartCountView.as_view(), name='get_cart_count'),


    path('checkout/', CheckoutView.as_view(), name='checkout'),
    
    path('initiate-payment/process', PaymentInitiateProcess.as_view(), name='initiate_payment_process'),
    path('initiate-payment/process/<int:order_id>/<str:order_number>', ProcessPaymentView.as_view(), name='process_payment'),

    path('cod-order-success/<int:pk>/', CodOrderSuccessView.as_view(), name='cod_order_success'),
    path('payment-order-success/<int:pk>/', PaymentOrderSuccessView.as_view(), name='payment_order_success'),
    path('subscription/success/<int:pk>/',SubscriptionOrderSuccessView.as_view(),name='payment_subscription_success'
    ),
    path('payment-order-decline/<int:pk>/', PaymentOrderFailView.as_view(), name='payment_order_decline'),


    


    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/edit/', OrderEditView.as_view(), name='order_edit'),
    path('orders/<int:pk>/delete/', OrderDeleteView.as_view(), name='order_delete'),


    path('transactions/', TransactionListView.as_view(), name='transaction_list'),
    path('transactions/<slug:transaction_type>/', TransactionListView.as_view(), name='transaction_list'),
    path('transactions-details/<int:pk>/', TransactionDetailView.as_view(), name='transaction_detail'),

    path('clear-order-session/', views.clear_order_session, name='clear_order_session'),



    



]