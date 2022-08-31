from ast import Or
from venv import create
from rest_framework import permissions
from orders.models import Order 
class IsOwnerOrder(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            order = Order.objects.get(id=request.data.get('order_id'), created_by=request.user)
        except:
            return False
        return True