from django.urls import path
from .views import enquiry_list, toggle_enquiry_status

urlpatterns = [
    path('enquiries/', enquiry_list, name='enquiry_list'),
    path('enquiries/toggle-status/<int:enquiry_id>/', toggle_enquiry_status, name='toggle_enquiry_status'),
]
