from rest_framework import permissions

from .models import get_user_role


class IsAdmin(permissions.BasePermission):
    """Vérifie si l'utilisateur est un administrateur."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_superuser or get_user_role(request.user) == 'ADMIN'
        )


class IsManager(permissions.BasePermission):
    """Vérifie si l'utilisateur est autorisé à gérer les camions."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_superuser or get_user_role(request.user) in ['ADMIN', 'OWNER']
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Vérifie si l'utilisateur est le propriétaire de l'objet ou un admin."""

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser or get_user_role(request.user) == 'ADMIN':
            return True

        if request.method in permissions.SAFE_METHODS:
            return obj.owner == request.user if hasattr(obj, 'owner') else True

        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        if hasattr(obj, 'truck') and hasattr(obj.truck, 'owner'):
            return obj.truck.owner == request.user
        return False


class IsTruckOwner(permissions.BasePermission):
    """Vérifie si l'utilisateur est le propriétaire du camion."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or get_user_role(request.user) == 'ADMIN':
            return True

        if hasattr(obj, 'truck'):
            return obj.truck.owner == request.user
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False
