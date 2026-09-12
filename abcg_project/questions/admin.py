from django.contrib import admin
from .models import (
    UserProfile, Participant, Symptom, RiskFactor, Question,
    Option, AuditLog, RolePermission, NikshayRecord, TptIndividual, IneligibleIndividual
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "role", "state", "district", "tb_unit")
    list_filter = ("role", "state", "district")
    search_fields = ("user__username", "full_name", "tb_unit")

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("study_id", "full_name", "age", "gender", "classification", "eligibility_status", "match_hrg", "eligible_bcg_campaign", "synced", "created_at")
    list_filter = ("classification", "eligible", "eligible_bcg_campaign", "synced", "sector", "case_finding_type")
    search_fields = ("study_id", "full_name", "contact_number", "nikshay_id")
    ordering = ("-created_at",)

    def eligibility_status(self, obj):
        return "Eligible for the aBCG VE study" if obj.eligible else "Not eligible for the aBCG VE study"
    eligibility_status.short_description = "Eligibility Status"

@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "display_order", "is_active")
    list_editable = ("display_order", "is_active")
    search_fields = ("code", "name")
    ordering = ("display_order",)

@admin.register(RiskFactor)
class RiskFactorAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_target_hrg", "display_order", "is_active")
    list_editable = ("is_target_hrg", "display_order", "is_active")
    search_fields = ("code", "name")
    ordering = ("display_order",)

class OptionInline(admin.TabularInline):
    model = Option
    extra = 1
    fields = ("code", "name", "display_order", "is_active")

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("code", "label", "step", "field_type", "display_order", "is_active")
    list_filter = ("step", "field_type", "is_active")
    list_editable = ("step", "field_type", "display_order", "is_active")
    search_fields = ("code", "label")
    ordering = ("step", "display_order")
    inlines = [OptionInline]

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ("code", "question", "name", "display_order", "is_active")
    list_filter = ("question", "is_active")
    list_editable = ("display_order", "is_active")
    search_fields = ("code", "name")
    ordering = ("question", "display_order")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("actor", "action", "target_user", "timestamp", "ip_address")
    list_filter = ("action", "timestamp")
    search_fields = ("actor__username", "action", "target_user__username")


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ("role", "module", "action", "allowed")
    list_filter = ("role", "module", "allowed")


@admin.register(NikshayRecord)
class NikshayRecordAdmin(admin.ModelAdmin):
    list_display = ("nikshay_id", "study_id", "screening_id", "full_name", "cohort", "state", "district", "tb_unit", "created_by", "updated_at")
    list_filter = ("cohort", "state", "district")
    search_fields = ("nikshay_id", "study_id", "screening_id", "full_name", "contact_number")
    ordering = ("-updated_at",)


@admin.register(TptIndividual)
class TptIndividualAdmin(admin.ModelAdmin):
    list_display = ("study_id", "full_name", "nikshay_id", "age", "gender", "classification", "synced", "created_at")
    list_filter = ("classification", "synced", "state", "district")
    search_fields = ("study_id", "full_name", "contact_number", "nikshay_id")
    ordering = ("-created_at",)


@admin.register(IneligibleIndividual)
class IneligibleIndividualAdmin(admin.ModelAdmin):
    list_display = ("study_id", "full_name", "nikshay_id", "age", "gender", "classification", "synced", "created_at")
    list_filter = ("classification", "synced", "state", "district")
    search_fields = ("study_id", "full_name", "contact_number", "nikshay_id")
    ordering = ("-created_at",)

