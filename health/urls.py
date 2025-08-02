from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('workout/dashboard/', views.AdminDashboardView.as_view(), name='workout_dashboard'),

    # Workout Programs
    path('workout-programs/', views.WorkoutProgramListView.as_view(), name='workout_program_list'),
    path('workout-programs/add/', views.WorkoutProgramCreateView.as_view(), name='workout_program_add'),

    # Equipment
    path('equipment/', views.EquipmentListView.as_view(), name='equipment_list'),
    path('equipment/add/', views.EquipmentCreateView.as_view(), name='equipment_add'),

    # Workout Categories (explicitly named)
    path('workout-categories/', views.WorkoutCategoryListView.as_view(), name='workout_category_list'),
    path('workout-categories/add/', views.WorkoutCategoryCreateView.as_view(), name='workout_category_add'),

    # Workout Templates
    path('workout-templates/', views.WorkoutTemplateListView.as_view(), name='workout_template_list'),
    path('workout-templates/add/', views.WorkoutTemplateCreateView.as_view(), name='workout_template_add'),
    path('workout-templates/assign/', views.AssignTemplateView.as_view(), name='workout_template_assign'),

    # Members
    path('members/', views.MemberListView.as_view(), name='member_list'),
    # If you add a member-workout assignment page, add it here as needed
]
