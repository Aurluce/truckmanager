# trips/admin.py
from django.contrib import admin
from .models import Trip

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['truck', 'start_time', 'end_time', 'status', 'total_distance_km']
    list_filter = ['status', 'start_time']
    search_fields = ['truck__truck_id', 'start_location']
    readonly_fields = ['created_at', 'updated_at']