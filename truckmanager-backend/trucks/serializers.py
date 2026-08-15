from rest_framework import serializers
from .models import Truck

class TruckSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    driver_name = serializers.SerializerMethodField()
    device_configured = serializers.SerializerMethodField()
    class Meta:
        model = Truck
        fields = [
            'id','truck_id','license_plate','brand','model','year','max_capacity_kg',
            'fuel_tank_capacity_l','owner','owner_name','driver','driver_name','esp32_device_id',
            'esp32_mac_address','firmware_version','api_key','device_configured',
            'overload_threshold_kg','fuel_theft_threshold_l','fuel_tolerance_threshold_l','abnormal_stop_minutes',
            'low_fuel_threshold_percent','speed_limit_kmh','cost_per_km',
            'cost_per_liter','revenue_per_ton','purchase_price','tco_months','is_active','created_at','updated_at'
        ]
        read_only_fields = ['id','owner_name','driver_name','device_configured','created_at','updated_at']
        extra_kwargs = {'api_key': {'write_only': True, 'required': False}}
    def get_owner_name(self,obj):
        return obj.owner.get_full_name() or obj.owner.username
    def get_driver_name(self,obj):
        return obj.driver.get_full_name() or obj.driver.username if obj.driver else None
    def get_device_configured(self,obj):
        return bool(obj.esp32_device_id and obj.api_key)

class TruckListSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    current_trip_id = serializers.SerializerMethodField()

    class Meta:
        model = Truck
        fields = [
            'id', 'truck_id', 'license_plate', 'brand', 'model', 'max_capacity_kg', 'fuel_tank_capacity_l',
            'owner_name', 'esp32_device_id', 'firmware_version', 'is_active', 'current_trip_id',
            'overload_threshold_kg', 'fuel_theft_threshold_l', 'fuel_tolerance_threshold_l', 'abnormal_stop_minutes',
            'low_fuel_threshold_percent', 'speed_limit_kmh', 'cost_per_liter', 'revenue_per_ton',
            'purchase_price', 'tco_months'
        ]

    def get_owner_name(self, obj):
        return obj.owner.get_full_name() or obj.owner.username

    def get_current_trip_id(self, obj):
        trip = obj.get_current_trip()
        return trip.id if trip else None
