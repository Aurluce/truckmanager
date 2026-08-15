# measurements/admin.py
from django.contrib import admin
from .models import WeightMeasurement, FuelMeasurement, GPSPosition

@admin.register(WeightMeasurement)
class WeightMeasurementAdmin(admin.ModelAdmin):
    list_display = ['trip', 'calibrated_weight_kg', 'is_overloaded', 'timestamp']
    list_filter = ['is_overloaded', 'timestamp']
    readonly_fields = ['timestamp']

@admin.register(FuelMeasurement)
class FuelMeasurementAdmin(admin.ModelAdmin):
    list_display = ['trip', 'fuel_level_percent', 'is_fuel_theft', 'timestamp']
    list_filter = ['is_fuel_theft', 'timestamp']
    readonly_fields = ['timestamp']

@admin.register(GPSPosition)
class GPSPositionAdmin(admin.ModelAdmin):
    list_display = ['trip', 'latitude', 'longitude', 'speed_kmh', 'timestamp']
    list_filter = ['is_stationary', 'is_abnormal_stop']
    readonly_fields = ['timestamp']