"""
RBAC Configuration Module
Centralized configuration for role-based access control (RBAC).
Defines sidebar visibility, module descriptions, and module-to-URL mappings.
"""

SIDEBAR_CONFIG = {
    "Super Admin": [
        "dashboard", "classification", "cases", "controls", "matching",
        "adjudication", "analytics", "data_quality", "study_site",
        "sync_telemetry", "data_export", "settings", "audit_logs",
        "user_management", "rbac_matrix"
    ],
    "Admin": [
        "dashboard", "registration", "classification", "cases", "controls",
        "matching", "analytics", "data_quality", "study_site",
        "sync_telemetry", "data_export", "settings", "audit_logs",
        "user_management"
    ],
    "Nodal Officer": [
        "dashboard", "classification", "cases", "controls",
        "matching", "analytics", "data_quality", "study_site",
        "sync_telemetry", "audit_logs"
    ],
    "Doctor": [
        "dashboard", "classification", "cases", "controls",
        "matching", "adjudication", "doctor_queue"
    ],
    "Project Nurse": [
        "dashboard", "registration", "search", "sync_telemetry"
    ]
}

MODULE_DESCRIPTIONS = {
    "dashboard": {
        "icon": "layout-dashboard",
        "label": "Dashboard",
        "description": "Operations dashboard and study statistics",
        "url_name": "questions:dashboard_home"
    },
    "registration": {
        "icon": "user-plus",
        "label": "Participant Registration",
        "description": "Register new participants and manage screening",
        "url_name": "questions:registration"
    },
    "search": {
        "icon": "search",
        "label": "Search Registry",
        "description": "Search and view participant records",
        "url_name": "questions:search"
    },
    "classification": {
        "icon": "stethoscope",
        "label": "Classification",
        "description": "View participant classification and eligibility",
        "url_name": "questions:classification"
    },
    "cases": {
        "icon": "clipboard-list",
        "label": "Cases",
        "description": "Manage TB Case cohort participants",
        "url_name": "questions:cases"
    },
    "controls": {
        "icon": "shield-check",
        "label": "Controls",
        "description": "Manage TB Control cohort participants",
        "url_name": "questions:controls"
    },
    "matching": {
        "icon": "git-compare",
        "label": "Matching",
        "description": "Review case-control matching results",
        "url_name": "questions:matching"
    },
    "adjudication": {
        "icon": "alert-circle",
        "label": "Adjudication Pending",
        "description": "Clinical cases requiring adjudication review",
        "url_name": "questions:adjudication"
    },
    "doctor_queue": {
        "icon": "user-check",
        "label": "Doctor Queue",
        "description": "Doctor's clinical review queue",
        "url_name": "questions:doctor_queue"
    },
    "analytics": {
        "icon": "bar-chart-3",
        "label": "Analytics",
        "description": "Study analytics and reporting dashboards",
        "url_name": "questions:analytics"
    },
    "data_quality": {
        "icon": "shield-alert",
        "label": "Data Quality",
        "description": "Monitor data quality exceptions and completeness",
        "url_name": "questions:data_quality"
    },
    "study_site": {
        "icon": "monitor",
        "label": "Study Site",
        "description": "Monitor and manage study sites and tablets",
        "url_name": "questions:study_site"
    },
    "sync_telemetry": {
        "icon": "radio",
        "label": "Sync & Telemetry",
        "description": "Manage data synchronization and device telemetry",
        "url_name": "questions:sync_telemetry"
    },
    "pending_sync": {
        "icon": "refresh-cw",
        "label": "Data Sync Staging",
        "description": "Offline sync staging and queue management",
        "url_name": "questions:pending_sync"
    },
    "data_export": {
        "icon": "download",
        "label": "Data Export",
        "description": "Export authorized datasets in multiple formats",
        "url_name": "questions:data_export"
    },
    "settings": {
        "icon": "settings",
        "label": "Settings",
        "description": "Configure campaign settings and system parameters",
        "url_name": "questions:settings"
    },
    "audit_logs": {
        "icon": "clock",
        "label": "Audit Logs",
        "description": "Review synchronization and audit event logs",
        "url_name": "questions:rbac_audit_logs"
    },
    "user_management": {
        "icon": "users",
        "label": "User Management",
        "description": "Create and manage user profiles and roles",
        "url_name": "questions:rbac_users"
    },
    "rbac_matrix": {
        "icon": "shield-lock",
        "label": "RBAC Management",
        "description": "Configure role-based access control permissions",
        "url_name": "questions:rbac_roles"
    },
    "groups_admin": {
        "icon": "lock",
        "label": "Groups Management",
        "description": "Manage user group membership",
        "url_name": "questions:rbac_groups"
    }
}

def get_sidebar_items_for_role(role):
    """
    Returns list of sidebar items accessible to a given role.
    Each item includes icon, label, description, and URL.

    Args:
        role (str): User role (Super Admin, Admin, Nodal Officer, Doctor, Project Nurse)

    Returns:
        list: List of sidebar item dictionaries with module metadata
    """
    module_keys = SIDEBAR_CONFIG.get(role, [])
    items = []

    for key in module_keys:
        if key in MODULE_DESCRIPTIONS:
            module = MODULE_DESCRIPTIONS[key].copy()
            module['key'] = key
            items.append(module)

    return items


def has_sidebar_access(role, module_key):
    """
    Check if a role has access to a specific sidebar module.

    Args:
        role (str): User role
        module_key (str): Module identifier

    Returns:
        bool: True if role can access module, False otherwise
    """
    return module_key in SIDEBAR_CONFIG.get(role, [])


def get_module_description(module_key):
    """
    Get metadata for a sidebar module.

    Args:
        module_key (str): Module identifier

    Returns:
        dict: Module metadata (icon, label, description, url_name)
    """
    return MODULE_DESCRIPTIONS.get(module_key, {})


def get_module_url(module_key):
    """
    Get the URL name for a sidebar module.

    Args:
        module_key (str): Module identifier

    Returns:
        str: Django URL name, or empty string if not found
    """
    module = MODULE_DESCRIPTIONS.get(module_key, {})
    return module.get('url_name', '')
