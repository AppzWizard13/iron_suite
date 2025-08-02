from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, CreateView, FormView
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django import forms

from health.forms import TemplateAssignForm, WorkoutProgramForm

from .models import (
    WorkoutCategory, WorkoutProgram, Equipment, WorkoutTemplate,
    WorkoutTemplateDay, MemberWorkoutAssignment
)
from django.contrib.auth import get_user_model
User = get_user_model()


# ---- CBVs ----
class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "health/admin_dashboard.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["stats"] = {
            "num_users": User.objects.count(),
            "num_workout_programs": WorkoutProgram.objects.count(),
            "num_templates": WorkoutTemplate.objects.count(),
            "num_assignments": MemberWorkoutAssignment.objects.count(),
        }
        return ctx

class WorkoutProgramListView(LoginRequiredMixin, ListView):
    model = WorkoutProgram
    template_name = "health/workout_list.html"
    context_object_name = "workouts"

class WorkoutProgramCreateView(LoginRequiredMixin, CreateView):
    model = WorkoutProgram
    form_class = WorkoutProgramForm
    template_name = "health/workout_add.html"
    success_url = reverse_lazy("workout_program_list")

    def form_valid(self, form):
        messages.success(self.request, "Workout Program created!")
        return super().form_valid(form)

class EquipmentListView(LoginRequiredMixin, ListView):
    model = Equipment
    template_name = "health/equipment_list.html"
    context_object_name = "equipment"

class EquipmentCreateView(LoginRequiredMixin, CreateView):
    model = Equipment
    fields = ['name']
    template_name = "health/equipment_add.html"
    success_url = reverse_lazy("equipment_list")

    def form_valid(self, form):
        messages.success(self.request, "Equipment created!")
        return super().form_valid(form)

class WorkoutTemplateListView(LoginRequiredMixin, ListView):
    model = WorkoutTemplate
    template_name = "health/template_list.html"
    context_object_name = "templates"

class WorkoutTemplateCreateView(LoginRequiredMixin, CreateView):
    model = WorkoutTemplate
    fields = ['name', 'description']
    template_name = "health/template_add.html"
    success_url = reverse_lazy("template_list")

    def form_valid(self, form):
        messages.success(self.request, "Template created!")
        return super().form_valid(form)

class AssignTemplateView(LoginRequiredMixin, FormView):
    form_class = TemplateAssignForm
    template_name = "health/assign_template.html"
    success_url = reverse_lazy("workout_template_list")  # update this URL name to your template list route

    def form_valid(self, form):
        members = form.cleaned_data['members']      # FIXED: use plural, as in your form!
        template = form.cleaned_data['template']
        start_date = form.cleaned_data['start_date']
        assignments = []
        for member in members:
            assignment = MemberWorkoutAssignment.objects.create(
                member=member, template=template, start_date=start_date, is_active=True
            )
            assignments.append(assignment)
        messages.success(
            self.request,
            f"Workout Template assigned to {members.count()} member{'s' if members.count() != 1 else ''}!"
        )
        return super().form_valid(form)
class MemberListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "health/member_list.html"
    context_object_name = "members"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['assignments'] = (
            MemberWorkoutAssignment.objects.select_related('member', 'template')
            .order_by('-assigned_at')
        )
        return ctx

class WorkoutCategoryListView(LoginRequiredMixin, ListView):
    model = WorkoutCategory
    template_name = 'health/category_list.html'
    context_object_name = 'categories'

class WorkoutCategoryCreateView(LoginRequiredMixin, CreateView):
    model = WorkoutCategory
    fields = ['name']
    template_name = 'health/category_add.html'
    success_url = reverse_lazy("category_list")

    def form_valid(self, form):
        messages.success(self.request, "Workout Category created!")
        return super().form_valid(form)
