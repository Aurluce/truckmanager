from rest_framework import serializers
from .models import Alert

class AlertSerializer(serializers.ModelSerializer):
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    truck_id = serializers.CharField(source='truck.truck_id', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'truck', 'truck_id', 'trip',
            'alert_type', 'alert_type_display',
            'message', 'threshold_value', 'actual_value',
            'details', 'status', 'status_display',
            'resolved_by', 'resolved_at', 'resolution_notes',
            'triggered_at', 'updated_at'
        ]
        read_only_fields = ['id', 'triggered_at', 'updated_at']

class AlertListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des alertes."""
    
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    truck_id = serializers.CharField(source='truck.truck_id', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'truck_id', 'alert_type', 'alert_type_display',
            'message', 'status', 'status_display', 'triggered_at'
        ]
