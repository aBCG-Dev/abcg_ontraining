from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from questions.models import RolePermission

DEFAULT_PERMISSIONS = {
    "Super Admin": {
        "Participant Registration": ["View", "Create", "Edit", "Export"],
        "Diagnostic Review (Doctor)": ["View", "Create", "Edit", "Approve/Reconcile", "Export"],
        "Nikshay Reconciliation": ["View", "Create", "Edit", "Approve/Reconcile", "Export"],
        "Bulk Sync Operations": ["View", "Create", "Edit", "Approve/Reconcile", "Export"],
        "Global Settings Admin": ["View", "Create", "Edit", "Approve/Reconcile", "Export"],
        "Telemetry & Audit Logs": ["View", "Export"],
        "User Management": ["View", "Create", "Edit", "Delete"],
        "System Configuration": ["View", "Create", "Edit", "Delete"]
    },
    "Admin": {
        "Participant Registration": ["View", "Create", "Edit", "Export"],
        "Diagnostic Review (Doctor)": ["View", "Export"],
        "Nikshay Reconciliation": ["View", "Create", "Edit", "Approve/Reconcile", "Export"],
        "Bulk Sync Operations": ["View", "Create", "Edit", "Approve/Reconcile", "Export"],
        "Global Settings Admin": ["View", "Create", "Edit", "Approve/Reconcile", "Export"],
        "Telemetry & Audit Logs": ["View", "Export"]
    },
    "Nodal Officer": {
        "Participant Registration": ["View", "Export"],
        "Diagnostic Review (Doctor)": ["View", "Export"],
        "Nikshay Reconciliation": ["View", "Create", "Edit", "Approve/Reconcile", "Export"],
        "Bulk Sync Operations": ["View", "Create", "Edit", "Approve/Reconcile", "Export"],
        "Global Settings Admin": ["View"],
        "Telemetry & Audit Logs": ["View", "Export"]
    },
    "Doctor": {
        "Participant Registration": ["View"],
        "Diagnostic Review (Doctor)": ["View", "Create", "Edit", "Approve/Reconcile"],
        "Nikshay Reconciliation": ["View"],
        "Bulk Sync Operations": [],
        "Global Settings Admin": [],
        "Telemetry & Audit Logs": []
    },
    "Project Nurse": {
        "Participant Registration": ["View", "Create", "Edit"],
        "Diagnostic Review (Doctor)": [],
        "Nikshay Reconciliation": ["View", "Approve/Reconcile"],
        "Bulk Sync Operations": ["View", "Create", "Edit", "Approve/Reconcile"],
        "Global Settings Admin": [],
        "Telemetry & Audit Logs": []
    }
}

def has_role_permission(role, module, action):
    """
    Checks if a role is permitted to perform an action on a module.
    If the RolePermission table is empty (e.g. in test suites), it falls back to DEFAULT_PERMISSIONS.

    Args:
        role (str): User role (Super Admin, Admin, Nodal Officer, Doctor, Project Nurse)
        module (str): Module name (e.g. 'Participant Registration', 'Diagnostic Review (Doctor)')
        action (str): Action name (e.g. 'View', 'Create', 'Edit', 'Approve/Reconcile')

    Returns:
        bool: True if role has permission for module/action, False otherwise
    """
    # Super Admin always has full access
    if role == "Super Admin":
        return True

    # Check database-backed RolePermission table first
    if RolePermission.objects.exists():
        has_perm = RolePermission.objects.filter(
            role=role,
            module=module,
            action=action,
            allowed=True
        ).exists()
        return has_perm

    # Fallback to DEFAULT_PERMISSIONS if table is empty (for testing)
    role_rules = DEFAULT_PERMISSIONS.get(role, {})
    allowed_actions = role_rules.get(module, [])
    return action in allowed_actions


def group_required(*group_names):
    """
    Decorator that checks if the logged in user belongs to at least one of the specified Groups.
    Super Admin / superusers bypass this check.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("questions:home")
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
                
            # Check native group membership
            if request.user.groups.filter(name__in=group_names).exists():
                return view_func(request, *args, **kwargs)
                
            # Fallback checks on UserProfile.role
            profile = getattr(request.user, "profile", None)
            if profile and profile.role in group_names:
                return view_func(request, *args, **kwargs)
                
            messages.error(request, f"Permission denied. Required Group: {', '.join(group_names)}")
            return redirect("questions:home")
        return _wrapped_view
    return decorator


def role_required(allowed_roles):
    """
    Decorator that checks if the logged in user has one of the allowed roles/groups.
    Super Admin has access to everything.
    """
    return group_required(*allowed_roles)


def permission_required(module, action):
    """
    Decorator that checks if the user's role/group has permission for a specific module and action.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("questions:home")
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
                
            profile = getattr(request.user, "profile", None)
            if not profile:
                return HttpResponseForbidden("User profile not found.")
                
            role = profile.role
            if not has_role_permission(role, module, action):
                messages.error(request, f"Permission denied. Role '{role}' is not allowed to {action.lower()} '{module}' operations.")
                return redirect("questions:home")
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
