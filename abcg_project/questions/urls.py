from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "questions"

urlpatterns = [
    path("", views.home, name="home"),
    path("logout/", views.user_logout, name="logout"),
    path("registration/", views.registration, name="registration"),
    path("registration/edit/<int:pk>/", views.registration, name="registration_edit"),
    path("search/", views.search, name="search"),
    path("registration/verify-beneficiary/", views.verify_beneficiary, name="verify_beneficiary"),
    path("pending-sync/", views.pending_sync, name="pending_sync"),
    path("reconcile/<int:pk>/", views.reconcile, name="reconcile"),
    path("api/nikshay/<str:nikshay_id>/", views.nikshay_api, name="nikshay_api"),
    path("api/reconcile/match/", views.reconcile_match_api, name="reconcile_match_api"),
    path("api/reconcile/save/", views.reconcile_save_api, name="reconcile_save_api"),
    
    # RBAC Routes
    path("rbac/users/", views.rbac_users, name="rbac_users"),
    path("rbac/roles/", views.rbac_roles, name="rbac_roles"),
    path("rbac/groups/", views.rbac_groups, name="rbac_groups"),
    path("rbac/audit-logs/", views.rbac_audit_logs, name="rbac_audit_logs"),
    
    # Dashboard Routes
    path("dashboard/", views.dashboard_home, name="dashboard_home"),
    path("dashboard/nodal/", views.nodal_dashboard, name="nodal_dashboard"),
    path("dashboard/doctor/", views.doctor_queue, name="doctor_queue"),
    path("dashboard/doctor/verify/<int:pk>/", views.doctor_verify, name="doctor_verify"),
    path("dashboard/classification/", views.classification_view, name="classification"),
    path("dashboard/cases/", views.cases_view, name="cases"),
    path("dashboard/controls/", views.controls_view, name="controls"),
    path("dashboard/matching/", views.matching_view, name="matching"),
    path("dashboard/adjudication/", views.adjudication_view, name="adjudication"),
    path("dashboard/analytics/", views.analytics_view, name="analytics"),
    path("dashboard/data-quality/", views.data_quality_view, name="data_quality"),
    path("dashboard/site-monitoring/", RedirectView.as_view(pattern_name="questions:study_site", permanent=True), name="site_monitoring"),
    path("dashboard/study-site/", views.study_site_view, name="study_site"),
    path("dashboard/telemetry/", views.sync_telemetry_view, name="sync_telemetry"),
    path("dashboard/export/", views.data_export_view, name="data_export"),
    path("dashboard/data-export/", RedirectView.as_view(pattern_name="questions:data_export", permanent=True)),
    path("dashboard/settings/", views.settings_view, name="settings"),
    path("dashboard/participant/<str:study_id>/", views.participant_detail_view, name="participant_detail"),
]
