from django import template
from questions.models import RolePermission

register = template.Library()

@register.filter(name='has_role')
def has_role(user, role_name):
    if not user or not user.is_authenticated:
        return False
    profile = getattr(user, 'profile', None)
    if not profile:
        return False
    if profile.role == "Super Admin":
        return True
    return profile.role == role_name

@register.filter(name='has_any_role')
def has_any_role(user, roles_string):
    if not user or not user.is_authenticated:
        return False
    profile = getattr(user, 'profile', None)
    if not profile:
        return False
    if profile.role == "Super Admin":
        return True
    roles = [r.strip() for r in roles_string.split(',')]
    return profile.role in roles


@register.filter(name='has_group')
def has_group(user, group_name):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or user.groups.filter(name="Super Admin").exists():
        return True
    return user.groups.filter(name=group_name).exists() or has_role(user, group_name)


@register.filter(name='has_any_group')
def has_any_group(user, groups_string):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or user.groups.filter(name="Super Admin").exists():
        return True
    groups = [g.strip() for g in groups_string.split(',')]
    return user.groups.filter(name__in=groups).exists() or has_any_role(user, groups_string)

from questions.decorators import has_role_permission

@register.simple_tag
def has_perm(user, module, action):
    """
    Usage: {% has_perm user "Participant Registration" "Create" as can_create %}
    """
    if not user or not user.is_authenticated:
        return False
    profile = getattr(user, 'profile', None)
    if not profile:
        return False
    return has_role_permission(profile.role, module, action)


@register.simple_tag
def get_sidebar_items(user):
    """
    Returns sidebar items accessible to the user based on their role.
    Usage: {% get_sidebar_items user as sidebar_items %}

    Returns a list of dicts with keys:
    - key: module identifier
    - label: display label
    - icon: bootstrap icon class
    - description: module description
    - url_name: Django URL name
    """
    if not user or not user.is_authenticated:
        return []

    profile = getattr(user, 'profile', None)
    if not profile:
        return []

    try:
        from questions.rbac_config import get_sidebar_items_for_role
        return get_sidebar_items_for_role(profile.role)
    except Exception:
        return []


@register.simple_tag
def can_access_sidebar_module(user, module_key):
    """
    Check if user can access a specific sidebar module.
    Usage: {% can_access_sidebar_module user "analytics" as can_view %}

    Returns True/False
    """
    if not user or not user.is_authenticated:
        return False

    profile = getattr(user, 'profile', None)
    if not profile:
        return False

    try:
        from questions.rbac_config import has_sidebar_access
        return has_sidebar_access(profile.role, module_key)
    except Exception:
        return False


@register.filter(name='dict_get')
def dict_get(value, arg):
    """
    Usage: {{ dictionary|dict_get:key }}
    """
    if isinstance(value, dict):
        return value.get(arg)
    return None


@register.filter(name='in_list')
def in_list(value, arg):
    """
    Usage: {% if item|in_list:list %}
    """
    if isinstance(arg, (list, tuple, set)):
        return value in arg
    return False
