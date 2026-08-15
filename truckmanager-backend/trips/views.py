from rest_framework import viewsets,filters,status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Trip
from .serializers import TripSerializer,TripListSerializer
from trucks.models import Truck
from dashboard.geocoding import reverse_geocode
from measurements.models import WeightMeasurement,FuelMeasurement,GPSPosition
from alerts.models import Alert
from loadings.models import Loading
from django.db.models import Avg,Max,Min,Sum
from datetime import timedelta
from core.models import get_user_role

class TripViewSet(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    filter_backends=[DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    filterset_fields=['status','truck']; search_fields=['start_location','end_location','truck__truck_id']; ordering=['-start_time']
    def get_queryset(self):
        qs=Trip.objects.select_related('truck')
        user_role = get_user_role(self.request.user)
        return qs if self.request.user.is_superuser or user_role == 'ADMIN' else qs.filter(truck__owner=self.request.user)
    def get_serializer_class(self): return TripListSerializer if self.action=='list' else TripSerializer
    @action(detail=False,methods=['post'])
    def start(self,request):
        truck=Truck.objects.filter(id=request.data.get('truck_id')).first()
        user_role = get_user_role(request.user)
        if not truck or (not request.user.is_superuser and user_role != 'ADMIN' and truck.owner!=request.user):
            return Response({'error':'Camion invalide'},404)
        if truck.get_current_trip(): return Response({'error':'Un trajet est déjà en cours'},400)
        trip=Trip.objects.create(truck=truck,start_time=timezone.now(),start_location=request.data.get('start_location','Départ GPS'))
        return Response(TripSerializer(trip).data,status=201)
    @action(detail=True,methods=['post'])
    def end_trip(self,request,pk=None):
        trip=self.get_object()
        if trip.status!='IN_PROGRESS': return Response({'error':'Trajet déjà terminé'},400)
        trip.end_time=timezone.now(); trip.status='COMPLETED'; trip.end_location=request.data.get('end_location','Arrivée GPS'); trip.recalculate()
        return Response(TripSerializer(trip).data)
    @action(detail=True,methods=['get'])
    def positions(self,request,pk=None):
        from measurements.serializers import GPSPositionSerializer
        return Response(GPSPositionSerializer(self.get_object().gps_positions.order_by('timestamp'),many=True).data)
    @action(detail=True,methods=['get'])
    def trace(self,request,pk=None):
        return Response([{'lat':p.latitude,'lng':p.longitude,'timestamp':p.timestamp,'speed':p.speed_kmh} for p in self.get_object().gps_positions.order_by('timestamp')])
    @action(detail=True,methods=['get'],url_path='detail')
    def trip_detail(self,request,pk=None):
        """Renvoie toutes les informations détaillées d'un trajet : infos, trace GPS,
        arrêts (avec nom du lieu), stationnements, chargements (avec photos), mesures
        et dernières données récupérées."""
        from measurements.serializers import GPSPositionSerializer,WeightMeasurementSerializer,FuelMeasurementSerializer
        from loadings.serializers import LoadingSerializer
        trip=self.get_object()
        positions=list(trip.gps_positions.order_by('timestamp'))
        # Regrouper les arrêts/stationnements consécutifs
        stops=[]
        current=None
        for p in positions:
            if p.is_stationary or p.is_abnormal_stop:
                if current is None:
                    current={'start':p,'end':p,'is_abnormal_stop':p.is_abnormal_stop}
                else:
                    current['end']=p
            else:
                if current is not None:
                    stops.append(current); current=None
        if current is not None:
            stops.append(current)
        stops_data=[]
        for s in stops:
            # Géocodage inverse pour déterminer le nom du lieu
            place_name = reverse_geocode(s['start'].latitude, s['start'].longitude)
            stops_data.append({
                'start_lat':s['start'].latitude,'start_lng':s['start'].longitude,
                'end_lat':s['end'].latitude,'end_lng':s['end'].longitude,
                'start_time':s['start'].timestamp,'end_time':s['end'].timestamp,
                'is_abnormal_stop':s['is_abnormal_stop'],
                'is_stationary':True,
                'place_name':place_name,
            })
        
        # Dernières données récupérées (télémétrie)
        last_weight = trip.weight_measurements.order_by('-timestamp').first()
        last_fuel = trip.fuel_measurements.order_by('-timestamp').first()
        last_gps = trip.gps_positions.order_by('-timestamp').first()
        
        # Dernière mise à jour = la plus récente des mesures
        timestamps = []
        if last_weight: timestamps.append(last_weight.timestamp)
        if last_fuel: timestamps.append(last_fuel.timestamp)
        if last_gps: timestamps.append(last_gps.timestamp)
        last_update = max(timestamps) if timestamps else None
        
        # Statistiques agrégées
        weight_agg = trip.weight_measurements.aggregate(
            avg_w=Avg('calibrated_weight_kg'),
            max_w=Max('calibrated_weight_kg'),
            min_w=Min('calibrated_weight_kg'),
        )
        fuel_agg = trip.fuel_measurements.aggregate(
            avg_speed=Avg('speed_kmh'),
            max_speed=Max('speed_kmh'),
            avg_rpm=Avg('engine_rpm'),
            avg_load=Avg('engine_load'),
        )
        
        # Alertes du trajet
        trip_alerts = trip.alerts.all()
        
        # Chargements du trajet
        trip_loadings = trip.loadings.all()
        
        return Response({
            'trip':TripSerializer(trip).data,
            'trace':[{'lat':p.latitude,'lng':p.longitude,'timestamp':p.timestamp,'speed':p.speed_kmh} for p in positions],
            'positions':GPSPositionSerializer(positions,many=True).data,
            'stops':stops_data,
            'loadings':LoadingSerializer(trip_loadings,many=True,context={'request':request}).data,
            'weight_measurements':WeightMeasurementSerializer(trip.weight_measurements.all(),many=True).data,
            'fuel_measurements':FuelMeasurementSerializer(trip.fuel_measurements.all(),many=True).data,
            'latest_data':{
                'speed':last_gps.speed_kmh if last_gps else (last_fuel.speed_kmh if last_fuel else 0),
                'weight':last_weight.calibrated_weight_kg if last_weight else 0,
                'fuel_level':last_fuel.fuel_level_percent if last_fuel else 0,
                'fuel_liters':last_fuel.fuel_level_liters if last_fuel else 0,
                'engine_rpm':last_fuel.engine_rpm if last_fuel else 0,
                'engine_load':last_fuel.engine_load if last_fuel else 0,
                'status':trip.status,
                'last_update':last_update,
                'latitude':last_gps.latitude if last_gps else None,
                'longitude':last_gps.longitude if last_gps else None,
                'place_name':reverse_geocode(last_gps.latitude, last_gps.longitude) if last_gps else None,
            },
            'stats':{
                'avg_weight_kg':round(weight_agg['avg_w'] or 0, 2),
                'max_weight_kg':round(weight_agg['max_w'] or 0, 2),
                'avg_speed_kmh':round(fuel_agg['avg_speed'] or 0, 2),
                'max_speed_kmh':round(fuel_agg['max_speed'] or 0, 2),
                'avg_rpm':round(fuel_agg['avg_rpm'] or 0, 0),
                'avg_engine_load':round(fuel_agg['avg_load'] or 0, 2),
                'alerts_count':trip_alerts.count(),
                'loadings_count':trip_loadings.count(),
                'stops_count':len(stops_data),
            },
        })