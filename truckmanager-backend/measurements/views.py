from rest_framework import viewsets,filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import WeightMeasurement,FuelMeasurement,GPSPosition
from .serializers import WeightMeasurementSerializer,FuelMeasurementSerializer,GPSPositionSerializer
from trucks.models import Truck
from core.models import get_user_role
class BaseMeasurement:
    def owner_qs(self,qs):
        user_role = get_user_role(self.request.user)
        if not self.request.user.is_superuser and user_role != 'ADMIN':
            qs=qs.filter(trip__truck__owner=self.request.user)
        return qs
class WeightMeasurementViewSet(BaseMeasurement,viewsets.ReadOnlyModelViewSet):
    permission_classes=[IsAuthenticated]; serializer_class=WeightMeasurementSerializer
    filter_backends=[DjangoFilterBackend,filters.OrderingFilter]; filterset_fields=['trip','is_overloaded','trip__truck']; ordering=['-timestamp']
    def get_queryset(self): return self.owner_qs(WeightMeasurement.objects.all())
    @action(detail=False,methods=['get'])
    def live(self,request):
        qs=self.get_queryset().order_by('-timestamp'); return Response(WeightMeasurementSerializer(qs[:50],many=True).data)
class FuelMeasurementViewSet(BaseMeasurement,viewsets.ReadOnlyModelViewSet):
    permission_classes=[IsAuthenticated]; serializer_class=FuelMeasurementSerializer
    filter_backends=[DjangoFilterBackend,filters.OrderingFilter]; filterset_fields=['trip','is_fuel_theft','trip__truck']; ordering=['-timestamp']
    def get_queryset(self): return self.owner_qs(FuelMeasurement.objects.all())
    @action(detail=False,methods=['get'])
    def live(self,request):
        truck_id=request.query_params.get('truck_id'); qs=self.get_queryset()
        if truck_id: qs=qs.filter(trip__truck_id=truck_id)
        return Response(FuelMeasurementSerializer(qs.first()).data if qs.exists() else None)
    @action(detail=False,methods=['get'])
    def historique(self,request):
        qs=self.get_queryset()[:200]; return Response(FuelMeasurementSerializer(qs,many=True).data)
class GPSPositionViewSet(BaseMeasurement,viewsets.ReadOnlyModelViewSet):
    permission_classes=[IsAuthenticated]; serializer_class=GPSPositionSerializer
    filter_backends=[DjangoFilterBackend,filters.OrderingFilter]; filterset_fields=['trip','is_stationary','is_abnormal_stop','trip__truck']; ordering=['-timestamp']
    def get_queryset(self): return self.owner_qs(GPSPosition.objects.all())
    @action(detail=False,methods=['get'])
    def latest(self,request):
        user_role = get_user_role(request.user)
        trucks=Truck.objects.all() if request.user.is_superuser or user_role == 'ADMIN' else Truck.objects.filter(owner=request.user)
        out=[]
        for truck in trucks:
            trip=truck.get_current_trip()
            pos=GPSPosition.objects.filter(trip=trip).first() if trip else None
            if pos: out.append({'truck_id':truck.truck_id,'position':{'lat':pos.latitude,'lng':pos.longitude},'speed':pos.speed_kmh,'timestamp':pos.timestamp})
        return Response(out)
