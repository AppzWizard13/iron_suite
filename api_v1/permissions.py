# permissions.py
from rest_framework.permissions import BasePermission

class IsAdminStaff(BasePermission):
    """
    Custom permission to only allow admin staff to access transaction data.
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Check if user has staff_role as Admin
        if hasattr(request.user, 'staff_role'):
            return request.user.staff_role == 'Admin'
        
        # Fallback to check if user is Django superuser/staff
        return request.user.is_staff or request.user.is_superuser
