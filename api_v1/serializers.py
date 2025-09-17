# serializers.py
from rest_framework import serializers
from payments.models import Transaction
from django.contrib.contenttypes.models import ContentType

class TransactionSerializer(serializers.ModelSerializer):
    content_object_type = serializers.SerializerMethodField()
    content_object_details = serializers.SerializerMethodField()
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'transaction_type_display', 
            'category', 'category_display', 'status', 'status_display',
            'amount', 'description', 'reference', 'date', 'created_at',
            'updated_at', 'content_object_type', 'content_object_details',
            # Add customer fields
            'customer_name', 'customer_email', 'customer_phone'
        ]
    
    def get_content_object_type(self, obj):
        """Get the content object model name"""
        if obj.content_type:
            return obj.content_type.model
        return None
    
    def get_content_object_details(self, obj):
        """Get basic details of the related object"""
        details = {}
        
        if obj.content_object:
            if hasattr(obj.content_object, 'id'):
                details['object_id'] = obj.content_object.id
                
                # Add order number if available
                if hasattr(obj.content_object, 'order_number'):
                    details['order_number'] = obj.content_object.order_number
                
                # Add order-specific details (fallback customer info)
                if hasattr(obj.content_object, 'customer'):
                    customer = obj.content_object.customer
                    # Only add if transaction doesn't have direct customer fields populated
                    if not obj.customer_name:
                        details['customer_name'] = getattr(customer, 'name', '') or getattr(customer, 'username', '')
                    if not obj.customer_email:
                        details['customer_email'] = getattr(customer, 'email', '')
                    if not obj.customer_phone:
                        details['customer_phone'] = getattr(customer, 'phone', '') or str(getattr(customer, 'phone_number', ''))
                
                # Add package details for subscription orders
                if hasattr(obj.content_object, 'package') and obj.content_object.package:
                    details['package_name'] = obj.content_object.package.name
                    details['package_id'] = obj.content_object.package.id
                
                # Add order status if available
                if hasattr(obj.content_object, 'status'):
                    details['order_status'] = obj.content_object.status
                    if hasattr(obj.content_object, 'get_status_display'):
                        details['order_status_display'] = obj.content_object.get_status_display()
                
                # Add order total if available
                if hasattr(obj.content_object, 'total'):
                    details['order_total'] = float(obj.content_object.total)
        
        return details if details else None
