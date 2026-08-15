# reports/admin.py
from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['truck', 'report_date', 'total_trips', 'total_revenue']
    list_filter = ['report_date']
    search_fields = ['truck__truck_id']
    readonly_fields = ['created_at', 'updated_at']