# workout/urls.py
from django.urls import path
from . import views

app_name = 'workout'

urlpatterns = [
    # Trainer URLs
    path('trainer/', views.TrainerDashboardView.as_view(), name='trainer_dashboard'),
    path('trainer/templates/', views.WeeklyTemplateListView.as_view(), name='template_list'),
    path('trainer/templates/create/', views.WeeklyTemplateCreateView.as_view(), name='create_template'),
    path('trainer/templates/<int:pk>/', views.WeeklyTemplateDetailView.as_view(), name='template_detail'),
    path('trainer/templates/<int:pk>/update/', views.WeeklyTemplateUpdateView.as_view(), name='update_template'),
    path('trainer/templates/<int:pk>/delete/', views.WeeklyTemplateDeleteView.as_view(), name='delete_template'),
    path('trainer/templates/<int:template_id>/assign/', views.AssignTemplateView.as_view(), name='assign_template'),
    path('trainer/assignments/', views.UserWorkoutAssignmentListView.as_view(), name='assignment_list'),
    
    # Exercise Management
    path('trainer/exercises/', views.ExerciseListView.as_view(), name='exercise_list'),
    path('trainer/exercises/create/', views.ExerciseCreateView.as_view(), name='create_exercise'),
    
    # User URLs
    path('', views.UserDashboardView.as_view(), name='user_dashboard'),
    path('workouts/<int:pk>/', views.UserWorkoutDetailView.as_view(), name='user_workout_detail'),
    path('calendar/', views.WorkoutCalendarView.as_view(), name='workout_calendar'),
    path('sessions/', views.WorkoutSessionListView.as_view(), name='session_history'),
    path('sessions/start/<int:assignment_id>/<int:day_id>/', views.WorkoutSessionCreateView.as_view(), name='start_session'),
    path('sessions/<int:pk>/', views.WorkoutSessionDetailView.as_view(), name='workout_session'),
    
    # API URLs for Flutter
    path('api/workouts/', views.APIUserWorkoutsView.as_view(), name='api_user_workouts'),
    path('api/sessions/<int:session_id>/', views.APIWorkoutSessionView.as_view(), name='api_workout_session'),
    path('trainer/equipment/', views.EquipmentListView.as_view(), name='equipment_list'),
    path('trainer/equipment/create/', views.EquipmentCreateView.as_view(), name='create_equipment'),
]
