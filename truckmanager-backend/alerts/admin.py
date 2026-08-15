# alerts/admin.py
from django.contrib import admin
from .models import Alert

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['alert_type', 'truck', 'status', 'triggered_at']
    list_filter = ['alert_type', 'status', 'triggered_at']
    search_fields = ['truck__truck_id', 'message']
    readonly_fields = ['triggered_at', 'updated_at']