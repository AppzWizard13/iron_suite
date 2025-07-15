from django.urls import path
from .views import TicketListView, TicketDetailView, TicketCreateView, TicketEditView, TicketDeleteView, resolve_ticket
from .views import SupportExecutiveListView, SupportExecutiveCreateView, SupportExecutiveEditView, SupportExecutiveDeleteView


urlpatterns = [
    path('tickets/', TicketListView.as_view(), name='ticket_list'),
    path('tickets/<int:pk>/', TicketDetailView.as_view(), name='ticket_detail'),
    path('tickets/create/', TicketCreateView.as_view(), name='ticket_create'),
    path('tickets/<int:pk>/edit/', TicketEditView.as_view(), name='ticket_edit'),
    path('tickets/<int:pk>/delete/', TicketDeleteView.as_view(), name='ticket_delete'),
    path('tickets/<str:filter_type>/', TicketListView.as_view(), name='ticket_list_filtered'),
    path('ticket/<int:pk>/resolve/', resolve_ticket, name='resolve_ticket'),

    path('support-executives/', SupportExecutiveListView.as_view(), name='support_executive_list'),
    path('support-executives/create/', SupportExecutiveCreateView.as_view(), name='support_executive_create'),
    path('support-executives/<int:pk>/edit/', SupportExecutiveEditView.as_view(), name='support_executive_edit'),
    path('support-executives/<int:pk>/delete/', SupportExecutiveDeleteView.as_view(), name='support_executive_delete'),
]