from django.contrib import admin
from .models import WorkoutProgram, WorkoutCategory, Equipment

@admin.register(WorkoutProgram)
class WorkoutProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'type', 'level')
    list_filter = ('category', 'type', 'level', 'equipment')
    search_fields = ('name',)

admin.site.register(WorkoutCategory)
admin.site.register(Equipment)



# from .models import BodyMeasurement

# @admin.register(BodyMeasurement)
# class BodyMeasurementAdmin(admin.ModelAdmin):
#     list_display = ('user', 'Vendor', 'date', 'weight_kg')
#     list_filter = ('Vendor', 'date')
#     autocomplete_fields = ('user', 'Vendor')
#     search_fields = [
#         'user__phone_number',
#         'user__first_name',
#         'user__last_name'
#     ]