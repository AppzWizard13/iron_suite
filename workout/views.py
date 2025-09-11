# workout/views.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, 
    DeleteView, TemplateView, View
)
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import *
from .forms import *


# Base Mixins
class TrainerRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure user is a trainer"""
    def dispatch(self, request, *args, **kwargs):
        # Add your trainer check logic here
        # For now, assuming all logged-in users can be trainers
        return super().dispatch(request, *args, **kwargs)


# Trainer Views
class TrainerDashboardView(TrainerRequiredMixin, TemplateView):
    """Trainer dashboard showing templates and assignments"""
    template_name = 'workout/trainer_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        templates = WeeklyTemplate.objects.filter(trainer=self.request.user, is_active=True)
        assignments = UserWorkoutAssignment.objects.filter(trainer=self.request.user, status='active')
        
        context.update({
            'page_name': 'trainer_dashboard',
            'templates': templates[:5],  # Latest 5
            'assignments': assignments[:10],  # Latest 10
            'total_templates': templates.count(),
            'active_assignments': assignments.count(),
        })
        return context


class WeeklyTemplateCreateView(TrainerRequiredMixin, CreateView):
    """Single page form to create weekly template"""
    model = WeeklyTemplate
    form_class = WeeklyTemplateForm
    template_name = 'workout/create_weekly_template.html'
    success_url = reverse_lazy('workout:trainer_dashboard')
    
    def form_valid(self, form):
        form.instance.trainer = self.request.user
        response = super().form_valid(form)
        
        # Process day templates and activities from form
        self.process_day_templates()
        
        messages.success(self.request, 'Weekly template created successfully!')
        return response
    
    def process_day_templates(self):
        """Process day templates and activities from POST data"""
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for day in weekdays:
            # Check if this day has any data
            day_name = self.request.POST.get(f'{day}_name')
            is_rest_day = self.request.POST.get(f'{day}_rest') == 'on'
            
            # Only create day template if there's data or it's explicitly marked as rest day
            if day_name or is_rest_day:
                day_template = DayTemplate.objects.create(
                    weekly_template=self.object,
                    day=day,
                    name=day_name or f'{day.title()} Workout',
                    is_rest_day=is_rest_day,
                    estimated_duration=self.request.POST.get(f'{day}_duration', '45-55min'),
                    notes=self.request.POST.get(f'{day}_notes', ''),
                )
                
                # Process activities for this day if not rest day
                if not is_rest_day:
                    self.process_activities_for_day(day_template, day)
    
    def process_activities_for_day(self, day_template, day):
        """Process activities for a specific day"""
        # Look for activities in the POST data
        activity_count = 0
        while True:
            exercise_id = self.request.POST.get(f'{day}_exercise_{activity_count}')
            if not exercise_id:
                break
                
            try:
                exercise = Exercise.objects.get(id=exercise_id)
                sets = int(self.request.POST.get(f'{day}_sets_{activity_count}', 1))
                reps = self.request.POST.get(f'{day}_reps_{activity_count}', '10')
                weight = self.request.POST.get(f'{day}_weight_{activity_count}', '')
                duration = self.request.POST.get(f'{day}_duration_{activity_count}', '10min')
                cues = self.request.POST.get(f'{day}_cues_{activity_count}', '')
                
                ActivityTemplate.objects.create(
                    day_template=day_template,
                    exercise=exercise,
                    order=activity_count + 1,
                    sets=sets,
                    reps=reps,
                    weight_percentage=weight,
                    estimated_duration=duration,
                    form_cues=cues,
                )
            except (Exercise.DoesNotExist, ValueError):
                pass
                
            activity_count += 1
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_name': 'create_template',
            'exercises': Exercise.objects.all().select_related('equipment'),
            'fitness_levels': FitnessLevel.objects.all(),
            'goals': Goal.objects.all(),
            'weekdays': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
        })
        return context


class WeeklyTemplateListView(TrainerRequiredMixin, ListView):
    """List all templates created by trainer"""
    model = WeeklyTemplate
    template_name = 'workout/template_list.html'
    context_object_name = 'templates'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = WeeklyTemplate.objects.filter(Q(trainer=self.request.user) | Q(trainer_id=5))
        
        # Filters
        fitness_level = self.request.GET.get('fitness_level')
        goal = self.request.GET.get('goal')
        search = self.request.GET.get('search')
        
        if fitness_level:
            queryset = queryset.filter(fitness_level__name=fitness_level)
        if goal:
            queryset = queryset.filter(goal__name=goal)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset.select_related('fitness_level', 'goal').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_name': 'template_list',
            'fitness_levels': FitnessLevel.objects.all(),
            'goals': Goal.objects.all(),
            'current_fitness_level': self.request.GET.get('fitness_level', ''),
            'current_goal': self.request.GET.get('goal', ''),
            'current_search': self.request.GET.get('search', ''),
        })
        return context


class WeeklyTemplateDetailView(TrainerRequiredMixin, DetailView):
    """Detail view for weekly template"""
    model = WeeklyTemplate
    template_name = 'workout/template_detail.html'
    context_object_name = 'template'
    
    def get_queryset(self):
        return WeeklyTemplate.objects.filter(trainer=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_name': 'template_detail',
            'day_templates': self.object.day_templates.all().prefetch_related(
                'activities__exercise__equipment'
            ),
            'assignments': UserWorkoutAssignment.objects.filter(
                weekly_template=self.object
            ).select_related('user')[:10]
        })
        return context


class WeeklyTemplateUpdateView(TrainerRequiredMixin, UpdateView):
    """Update weekly template"""
    model = WeeklyTemplate
    form_class = WeeklyTemplateForm
    template_name = 'workout/update_template.html'
    
    def get_queryset(self):
        return WeeklyTemplate.objects.filter(trainer=self.request.user)
    
    def get_success_url(self):
        return reverse('workout:template_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Template updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = 'update_template'
        return context


class WeeklyTemplateDeleteView(TrainerRequiredMixin, DeleteView):
    """Delete weekly template"""
    model = WeeklyTemplate
    template_name = 'workout/template_confirm_delete.html'
    success_url = reverse_lazy('workout:template_list')
    
    def get_queryset(self):
        return WeeklyTemplate.objects.filter(trainer=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Template deleted successfully!')
        return super().delete(request, *args, **kwargs)


class AssignTemplateView(TrainerRequiredMixin, CreateView):
    """Assign template to user"""
    model = UserWorkoutAssignment
    form_class = AssignTemplateForm
    template_name = 'workout/assign_template.html'
    success_url = reverse_lazy('workout:trainer_dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        self.template = get_object_or_404(
            WeeklyTemplate, 
            pk=self.kwargs['template_id'], 
            trainer=request.user
        )
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.trainer = self.request.user
        form.instance.weekly_template = self.template
        response = super().form_valid(form)
        
        messages.success(
            self.request, 
            f'Template assigned to {form.instance.user.username} successfully!'
        )
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'template': self.template,
            'page_name': 'assign_template'
        })
        return context


class UserWorkoutAssignmentListView(TrainerRequiredMixin, ListView):
    """List all workout assignments by trainer"""
    model = UserWorkoutAssignment
    template_name = 'workout/assignment_list.html'
    context_object_name = 'assignments'
    paginate_by = 15
    
    def get_queryset(self):
        return UserWorkoutAssignment.objects.filter(
            trainer=self.request.user
        ).select_related('user', 'weekly_template').order_by('-assigned_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = 'assignment_list'
        return context


# User Views
class UserDashboardView(LoginRequiredMixin, TemplateView):
    """User dashboard showing current assignments"""
    template_name = 'workout/user_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assignments = UserWorkoutAssignment.objects.filter(
            user=self.request.user, 
            status='active'
        ).select_related('weekly_template', 'trainer')
        recent_sessions = WorkoutSession.objects.filter(
            assignment__user=self.request.user
        ).select_related('day_template')[:5]
        
        context.update({
            'page_name': 'user_dashboard',
            'assignments': assignments,
            'recent_sessions': recent_sessions,
            'total_assignments': assignments.count(),
        })
        return context


class UserWorkoutDetailView(LoginRequiredMixin, DetailView):
    """Detail view of user's workout assignment"""
    model = UserWorkoutAssignment
    template_name = 'workout/user_workout_detail.html'
    context_object_name = 'assignment'
    
    def get_queryset(self):
        return UserWorkoutAssignment.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_name': 'user_workout_detail',
            'day_templates': self.object.weekly_template.day_templates.all().prefetch_related(
                'activities__exercise__equipment'
            )
        })
        return context


class WorkoutCalendarView(LoginRequiredMixin, TemplateView):
    """Calendar view of user's workouts"""
    template_name = 'workout/workout_calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_name': 'workout_calendar',
            'assignments': UserWorkoutAssignment.objects.filter(
                user=self.request.user,
                status='active'
            )
        })
        return context


class WorkoutSessionCreateView(LoginRequiredMixin, CreateView):
    """Start a new workout session"""
    model = WorkoutSession
    fields = []
    template_name = 'workout/start_session.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.assignment = get_object_or_404(
            UserWorkoutAssignment,
            pk=self.kwargs['assignment_id'],
            user=request.user
        )
        self.day_template = get_object_or_404(
            DayTemplate,
            pk=self.kwargs['day_id'],
            weekly_template=self.assignment.weekly_template
        )
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        from django.utils import timezone
        
        form.instance.assignment = self.assignment
        form.instance.day_template = self.day_template
        form.instance.date = timezone.now().date()
        form.instance.started_at = timezone.now()
        
        response = super().form_valid(form)
        
        # Create activity logs for this session
        for activity in self.day_template.activities.all():
            ActivityLog.objects.create(
                session=self.object,
                activity_template=activity,
                sets_completed=0,
                reps_completed='0',
            )
        
        return redirect('workout:workout_session', pk=self.object.pk)


class WorkoutSessionDetailView(LoginRequiredMixin, DetailView):
    """Active workout session view"""
    model = WorkoutSession
    template_name = 'workout/workout_session.html'
    context_object_name = 'session'
    
    def get_queryset(self):
        return WorkoutSession.objects.filter(assignment__user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_name': 'workout_session',
            'activity_logs': self.object.activity_logs.all().select_related(
                'activity_template__exercise__equipment'
            ).order_by('activity_template__order')
        })
        return context


class WorkoutSessionListView(LoginRequiredMixin, ListView):
    """List of user's workout sessions"""
    model = WorkoutSession
    template_name = 'workout/session_history.html'
    context_object_name = 'sessions'
    paginate_by = 20
    
    def get_queryset(self):
        return WorkoutSession.objects.filter(
            assignment__user=self.request.user
        ).select_related('day_template', 'assignment__weekly_template').order_by('-date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = 'session_history'
        return context


# API Views for Flutter App
class APIUserWorkoutsView(LoginRequiredMixin, View):
    """API endpoint for Flutter app"""
    
    def get(self, request, *args, **kwargs):
        assignments = UserWorkoutAssignment.objects.filter(
            user=request.user, 
            status='active'
        ).select_related('weekly_template', 'trainer').prefetch_related(
            'weekly_template__day_templates__activities__exercise__equipment'
        )
        
        data = []
        for assignment in assignments:
            assignment_data = {
                'id': assignment.id,
                'template_name': assignment.weekly_template.name,
                'trainer': assignment.trainer.username,
                'start_date': assignment.start_date.isoformat(),
                'fitness_level': assignment.weekly_template.fitness_level.name,
                'goal': assignment.weekly_template.goal.name,
                'days': []
            }
            
            for day_template in assignment.weekly_template.day_templates.all():
                day_data = {
                    'id': day_template.id,
                    'day': day_template.day,
                    'name': day_template.name,
                    'is_rest_day': day_template.is_rest_day,
                    'estimated_duration': day_template.estimated_duration,
                    'warm_up_instructions': day_template.warm_up_instructions,
                    'cool_down_instructions': day_template.cool_down_instructions,
                    'activities': []
                }
                
                for activity in day_template.activities.all():
                    activity_data = {
                        'id': activity.id,
                        'exercise': {
                            'name': activity.exercise.name,
                            'muscle_groups': activity.exercise.muscle_groups,
                            'instructions': activity.exercise.instructions,
                        },
                        'equipment': activity.exercise.equipment.name,
                        'sets': activity.sets,
                        'reps': activity.reps,
                        'weight_percentage': activity.weight_percentage,
                        'rest_time': activity.rest_time,
                        'form_cues': activity.form_cues,
                        'rpe_target': activity.rpe_target,
                        'estimated_duration': activity.estimated_duration,
                    }
                    day_data['activities'].append(activity_data)
                
                assignment_data['days'].append(day_data)
            
            data.append(assignment_data)
        
        return JsonResponse({'workouts': data, 'status': 'success'})


class APIWorkoutSessionView(LoginRequiredMixin, View):
    """API for workout session management"""
    
    def get(self, request, session_id):
        """Get workout session details"""
        try:
            session = WorkoutSession.objects.get(
                id=session_id,
                assignment__user=request.user
            )
            
            data = {
                'id': session.id,
                'day_template': session.day_template.name,
                'date': session.date.isoformat(),
                'is_completed': session.is_completed,
                'activities': []
            }
            
            for log in session.activity_logs.all():
                activity_data = {
                    'id': log.id,
                    'exercise': log.activity_template.exercise.name,
                    'target_sets': log.activity_template.sets,
                    'target_reps': log.activity_template.reps,
                    'completed_sets': log.sets_completed,
                    'completed_reps': log.reps_completed,
                    'weight_used': log.weight_used,
                    'is_completed': log.is_completed,
                }
                data['activities'].append(activity_data)
            
            return JsonResponse({'session': data, 'status': 'success'})
        
        except WorkoutSession.DoesNotExist:
            return JsonResponse({'error': 'Session not found', 'status': 'error'}, status=404)
    
    def post(self, request, session_id):
        """Update workout session"""
        try:
            session = WorkoutSession.objects.get(
                id=session_id,
                assignment__user=request.user
            )
            
            # Update session data from request
            import json
            data = json.loads(request.body)
            
            if 'complete_session' in data:
                from django.utils import timezone
                session.is_completed = True
                session.completed_at = timezone.now()
                session.save()
            
            if 'activities' in data:
                for activity_data in data['activities']:
                    try:
                        log = ActivityLog.objects.get(
                            id=activity_data['id'],
                            session=session
                        )
                        log.sets_completed = activity_data.get('sets_completed', log.sets_completed)
                        log.reps_completed = activity_data.get('reps_completed', log.reps_completed)
                        log.weight_used = activity_data.get('weight_used', log.weight_used)
                        log.actual_rpe = activity_data.get('actual_rpe', log.actual_rpe)
                        log.is_completed = activity_data.get('is_completed', log.is_completed)
                        log.notes = activity_data.get('notes', log.notes)
                        log.save()
                    except ActivityLog.DoesNotExist:
                        continue
            
            return JsonResponse({'status': 'success', 'message': 'Session updated'})
        
        except WorkoutSession.DoesNotExist:
            return JsonResponse({'error': 'Session not found', 'status': 'error'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e), 'status': 'error'}, status=400)


# Exercise and Equipment Management Views
class ExerciseListView(TrainerRequiredMixin, ListView):
    """List all exercises"""
    model = Exercise
    template_name = 'workout/exercise_list.html'
    context_object_name = 'exercises'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Exercise.objects.select_related('equipment')
        
        search = self.request.GET.get('search')
        equipment = self.request.GET.get('equipment')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(muscle_groups__icontains=search)
            )
        if equipment:
            queryset = queryset.filter(equipment_id=equipment)
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_name': 'exercise_list',
            'equipment_list': Equipment.objects.all()
        })
        return context


class ExerciseCreateView(TrainerRequiredMixin, CreateView):
    """Create new exercise"""
    model = Exercise
    form_class = ExerciseForm
    template_name = 'workout/exercise_form.html'
    success_url = reverse_lazy('workout:exercise_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Exercise created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = 'create_exercise'
        return context


class EquipmentListView(TrainerRequiredMixin, ListView):
    """List all equipment"""
    model = Equipment
    template_name = 'workout/equipment_list.html'
    context_object_name = 'equipment_list'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = 'equipment_list'
        return context


class EquipmentCreateView(TrainerRequiredMixin, CreateView):
    """Create new equipment"""
    model = Equipment
    form_class = EquipmentForm
    template_name = 'workout/equipment_form.html'
    success_url = reverse_lazy('workout:equipment_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Equipment created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = 'create_equipment'
        return context
