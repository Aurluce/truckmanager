from rest_framework import serializers

class TruckStatusSerializer(serializers.Serializer):
    """Serializer pour le statut des camions."""
    truck_id = serializers.CharField()
    license_plate = serializers.CharField()
    status = serializers.CharField()
    position = serializers.DictField(required=False)
    speed = serializers.FloatField(required=False)
    last_update = serializers.DateTimeField(required=False)

class RealtimeDataSerializer(serializers.Serializer):
    """Serializer pour les données en temps réel."""
    truck_id = serializers.CharField()
    status = serializers.CharField()
    trip_id = serializers.IntegerField(required=False)
    start_time = serializers.DateTimeField(required=False)
    duration = serializers.FloatField(required=False)
    current_weight = serializers.FloatField(required=False)
    fuel_level = serializers.FloatField(required=False)
    fuel_liters = serializers.FloatField(required=False)
    speed = serializers.FloatField(required=False)
    position = serializers.DictField(required=False)
    is_overloaded = serializers.BooleanField(required=False)

class DashboardSummarySerializer(serializers.Serializer):
    """Serializer pour le résumé du dashboard."""
    trucks = serializers.DictField()
    trips = serializers.DictField()
    alerts = serializers.DictField()
    financial = serializers.DictField()

class ChartDataSerializer(serializers.Serializer):
    """Serializer pour les données de graphiques."""
    date = serializers.CharField()
    trips = serializers.IntegerField()
    distance = serializers.FloatField()
    fuel = serializers.FloatField()
