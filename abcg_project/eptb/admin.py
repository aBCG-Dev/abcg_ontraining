from django.contrib import admin
from .models import EptbSite, EptbSubQuestion

class EptbSubQuestionInline(admin.TabularInline):
    model = EptbSubQuestion
    extra = 1
    fields = ("code", "label", "display_order", "is_active")

@admin.register(EptbSite)
class EptbSiteAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "display_order", "is_active")
    list_editable = ("display_order", "is_active")
    search_fields = ("code", "name")
    ordering = ("display_order",)
    inlines = [EptbSubQuestionInline]

@admin.register(EptbSubQuestion)
class EptbSubQuestionAdmin(admin.ModelAdmin):
    list_display = ("code", "site", "label", "display_order", "is_active")
    list_filter = ("site", "is_active")
    list_editable = ("display_order", "is_active")
    search_fields = ("code", "label")
    ordering = ("site", "display_order")
