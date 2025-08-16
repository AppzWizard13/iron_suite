# health/serializers.py
from rest_framework import serializers
from .models import BodyMeasurement

class BodyMeasurementTodaySerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyMeasurement
        fields = (
            'date',
            'height_cm',
            'weight_kg',
            'bmi',
            'week_of_year',
            'year',
            'week_index_since_join',
        )
        read_only_fields = (
            'date',
            'bmi',
            'week_of_year',
            'year',
            'week_index_since_join',
        )

    def validate(self, attrs):
        height = attrs.get('height_cm')
        weight = attrs.get('weight_kg')

        if height is None:
            raise serializers.ValidationError({"height_cm": "This field is required."})
        if weight is None:
            raise serializers.ValidationError({"weight_kg": "This field is required."})

        if height <= 0:
            raise serializers.ValidationError({"height_cm": "Height must be greater than zero."})
        if weight <= 0:
            raise serializers.ValidationError({"weight_kg": "Weight must be greater than zero."})

        return attrs
