from rest_framework.permissions import BasePermission

class HasRolePermission(BasePermission):
    """
    Checks if user is authenticated and has one of the allowed roles for the view.
    If the view does not declare allowed_roles, all authenticated users are permitted.
    Super Admins are always permitted.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        profile = getattr(request.user, 'central_profile', None)
        if not profile:
            return False

        role = getattr(profile, 'role', 'Field Investigator')
        if role == "Super Admin":
            return True

        allowed_roles = getattr(view, 'allowed_roles', None)
        if allowed_roles is None:
            return True

        return role in allowed_roles
