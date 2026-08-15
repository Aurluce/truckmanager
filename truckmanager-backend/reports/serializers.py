from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    truck_id = serializers.CharField(source='truck.truck_id', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'truck', 'truck_id', 'report_date',
            'total_trips', 'total_distance_km', 'total_duration_hours',
            'total_weight_kg', 'avg_weight_kg',
            'total_fuel_consumed_l', 'avg_fuel_consumption_l_100km',
            'avg_fuel_per_ton_km',
            'total_revenue', 'total_fuel_cost', 'profit_margin',
            'total_alerts', 'resolved_alerts',
            'pdf_file', 'pdf_generated_at', 'signature_hash',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ReportListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des rapports."""
    
    truck_id = serializers.CharField(source='truck.truck_id', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'truck_id', 'report_date',
            'total_trips', 'total_distance_km', 'total_duration_hours',
            'total_weight_kg', 'avg_weight_kg',
            'total_fuel_consumed_l', 'avg_fuel_consumption_l_100km',
            'avg_fuel_per_ton_km',
            'total_revenue', 'total_fuel_cost', 'profit_margin',
            'total_alerts', 'resolved_alerts',
            'pdf_file', 'pdf_generated_at', 'signature_hash',
            'created_at', 'updated_at'
        ]