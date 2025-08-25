from rest_framework import serializers
from .models import Package

class PackageSerializer(serializers.ModelSerializer):
    final_price = serializers.ReadOnlyField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'name', 'description', 'type', 'duration_days',
            'price', 'discount_type', 'discount_value', 'final_price',
            'features', 'is_active', 'created_at', 'updated_at'
        ]
