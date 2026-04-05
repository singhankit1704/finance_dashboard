from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only admin role can access."""
    message = "Access denied. Admin role required."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsAnalystOrAdmin(BasePermission):
    """Analyst or Admin can access."""
    message = "Access denied. Analyst or Admin role required."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_analyst)


class IsAnyRole(BasePermission):
    """Any authenticated user (viewer, analyst, admin) can access."""
    message = "Authentication required."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_active)
