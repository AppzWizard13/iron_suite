from django.urls import path
from .views import BusinessDetailsView
from .views import (
    ConfigurationCreateView,
    ConfigurationListView,
    ConfigurationDetailView,
    ConfigurationUpdateView,
    ConfigurationDeleteView,
    SystemReset
)



urlpatterns = [
    path('business-details/', BusinessDetailsView.as_view(), name='business_details'),


    path('configurations/', ConfigurationListView.as_view(), name='configuration_list'),
    path('configurations/add/', ConfigurationCreateView.as_view(), name='configuration_create'),
    path('configurations/<int:pk>/', ConfigurationDetailView.as_view(), name='configuration_detail'),
    path('configurations/<int:pk>/edit/', ConfigurationUpdateView.as_view(), name='configuration_update'),
    path('configurations/<int:pk>/delete/', ConfigurationDeleteView.as_view(), name='configuration_delete'),

    path('system-reset/', SystemReset.as_view(), name='system_reset'),

]

