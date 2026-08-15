from rest_framework import serializers
from .models import WeightMeasurement, FuelMeasurement, GPSPosition

class WeightMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeightMeasurement
        fields = [
            'id', 'trip', 'raw_weight_kg', 'filtered_weight_kg',
            'calibrated_weight_kg', 'is_overloaded', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']

class FuelMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelMeasurement
        fields = [
            'id', 'trip', 'fuel_level_percent', 'fuel_level_liters',
            'speed_kmh', 'engine_rpm', 'engine_load',
            'is_fuel_theft', 'fuel_drop_amount', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']

class GPSPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPSPosition
        fields = [
            'id', 'trip', 'latitude', 'longitude', 'altitude',
            'speed_kmh', 'heading', 'accuracy',
            'is_stationary', 'is_abnormal_stop', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']
