from rest_framework import serializers
from .models import Trip
from trucks.serializers import TruckSerializer

class TripSerializer(serializers.ModelSerializer):
    truck_details = TruckSerializer(source='truck', read_only=True)
    
    class Meta:
        model = Trip
        fields = [
            'id', 'truck', 'truck_details',
            'start_time', 'end_time', 'start_location', 'end_location',
            'total_distance_km', 'total_fuel_consumed_l',
            'avg_fuel_consumption_l_100km', 'avg_fuel_per_ton_km',
            'max_weight_kg', 'avg_weight_kg',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class TripListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des trajets."""
    
    truck_id = serializers.CharField(source='truck.truck_id', read_only=True)
    
    class Meta:
        model = Trip
        fields = [
            'id', 'truck_id', 'start_time', 'end_time',
            'total_distance_km', 'status'
        ]
