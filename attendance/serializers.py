from rest_framework import serializers
from .models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'date', 'status', 'check_in_time', 'check_out_time', 'duration', 'user', 'schedule', 'Vendor']
