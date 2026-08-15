# trucks/admin.py
from django.contrib import admin
from .models import Truck

@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    list_display = ['truck_id', 'license_plate', 'brand', 'model', 'owner', 'is_active']
    list_filter = ['is_active', 'brand', 'year']
    search_fields = ['truck_id', 'license_plate', 'brand', 'model']
    readonly_fields = ['created_at', 'updated_at']