from django.contrib import admin
from .models import WorkoutProgram, WorkoutCategory, Equipment

@admin.register(WorkoutProgram)
class WorkoutProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'type', 'level')
    list_filter = ('category', 'type', 'level', 'equipment')
    search_fields = ('name',)

admin.site.register(WorkoutCategory)
admin.site.register(Equipment)


# admin.py

from django.contrib import admin
from .models import WorkoutTemplate, WorkoutTemplateDay, MemberWorkoutAssignment

class WorkoutTemplateDayInline(admin.TabularInline):
    model = WorkoutTemplateDay
    extra = 1

@admin.register(WorkoutTemplate)
class WorkoutTemplateAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [WorkoutTemplateDayInline]

@admin.register(MemberWorkoutAssignment)
class MemberWorkoutAssignmentAdmin(admin.ModelAdmin):
    list_display = ['member', 'template', 'start_date', 'is_active']
    list_filter = ['is_active', 'template']
