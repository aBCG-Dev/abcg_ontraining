import csv
from django.contrib import admin
from django.http import HttpResponse
from .models import GlobalSettings, UserProfile, Participant, TptIndividual, IneligibleIndividual, DeviceSyncLog, Question, Option, AuditLog

# Custom Action: Export to CSV
def export_to_csv(modeladmin, request, queryset):
    """
    Generic action to export selected queryset records to CSV file.
    Very useful for clinical researchers and stakeholders!
    """
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta.object_name}_export.csv'
    writer = csv.writer(response)
    
    # Write CSV header row
    writer.writerow(field_names)
    
    # Write database data rows
    for obj in queryset:
        row = []
        for field in field_names:
            val = getattr(obj, field)
            # Handle text serialization for JSON fields or textareas
            if isinstance(val, str):
                val = val.replace('\n', ' ').replace('\r', ' ')
            row.append(val)
        writer.writerow(row)
        
    return response

export_to_csv.short_description = "Export Selected to CSV File"


@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'bmi_threshold', 'age_threshold', 'campaign_period')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'role', 'state', 'district', 'tb_unit')
    list_filter = ('role', 'state', 'district')
    search_fields = ('user__username', 'full_name', 'tb_unit')


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('study_id', 'full_name', 'age', 'gender', 'tb_unit', 'classification', 'eligible', 'uploaded_by', 'uploaded_at')
    list_filter = ('classification', 'eligible', 'uploaded_by', 'state', 'district')
    search_fields = ('study_id', 'nikshay_id', 'full_name', 'contact_number')
    actions = [export_to_csv]


@admin.register(TptIndividual)
class TptIndividualAdmin(admin.ModelAdmin):
    list_display = ('study_id', 'full_name', 'age', 'gender', 'tpt_undergone', 'uploaded_by', 'uploaded_at')
    list_filter = ('tpt_undergone', 'uploaded_by')
    search_fields = ('study_id', 'full_name')
    actions = [export_to_csv]


@admin.register(IneligibleIndividual)
class IneligibleIndividualAdmin(admin.ModelAdmin):
    list_display = ('study_id', 'full_name', 'age', 'date_enroll', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_by',)
    search_fields = ('study_id', 'full_name')
    actions = [export_to_csv]


@admin.register(DeviceSyncLog)
class DeviceSyncLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'latitude', 'longitude', 'battery_level', 'battery_charging', 'synced_count', 'timestamp')
    list_filter = ('user', 'battery_charging')
    date_hierarchy = 'timestamp'


class OptionInline(admin.TabularInline):
    model = Option
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('step', 'code', 'label', 'field_type', 'display_order', 'is_active')
    list_filter = ('step', 'field_type', 'is_active')
    search_fields = ('code', 'label')
    inlines = [OptionInline]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('actor', 'action', 'target_user', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('actor__username', 'action', 'target_user__username')

