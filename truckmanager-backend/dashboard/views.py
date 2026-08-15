from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .services import DashboardService
from trucks.models import Truck
from alerts.models import Alert
from loadings.models import Loading
from trips.models import Trip
from measurements.models import WeightMeasurement,FuelMeasurement,GPSPosition
from core.models import get_user_role
class DashboardSummaryView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        return Response(DashboardService.summary(request.user,int(request.query_params.get('days',30)),request.query_params.get('truck_id')))
class RealtimeDataView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,truck_id):
        t=get_object_or_404(Truck,id=truck_id)
        user_role = get_user_role(request.user)
        if not request.user.is_superuser and user_role != 'ADMIN' and t.owner!=request.user:
            return Response({'error':'Accès refusé'},403)
        return Response(DashboardService.get_realtime_data(t.id, request.user))
class FleetMapView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request): return Response(DashboardService.fleet(request.user,request.query_params.get('truck_id')))
class DashboardSeriesView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        truck_id=request.query_params.get('truck_id'); days=min(int(request.query_params.get('days',1)),30)
        qs=Trip.objects.filter(start_time__gte=__import__('django').utils.timezone.now()-__import__('datetime').timedelta(days=days))
        user_role = get_user_role(request.user)
        if not request.user.is_superuser and user_role != 'ADMIN':
            qs=qs.filter(truck__owner=request.user)
        if truck_id: qs=qs.filter(truck_id=truck_id)
        out=[]
        for trip in qs.order_by('start_time'):
            out.append({'trip_id':trip.id,'truck_id':trip.truck.truck_id,'start_time':trip.start_time,'distance_km':trip.total_distance_km,'fuel_l':trip.total_fuel_consumed_l,'weight_kg':trip.max_weight_kg})
        return Response(out)
class DashboardAlertsView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        qs=Alert.objects.select_related('truck')
        user_role = get_user_role(request.user)
        if not request.user.is_superuser and user_role != 'ADMIN':
            qs=qs.filter(truck__owner=request.user)
        return Response([{'id':a.id,'truck_id':a.truck.truck_id,'type':a.get_alert_type_display(),'alert_type':a.alert_type,'message':a.message,'status':a.status,'triggered_at':a.triggered_at,'actual_value':a.actual_value,'threshold_value':a.threshold_value} for a in qs[:20]])
class DashboardLoadsView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        qs=Loading.objects.select_related('trip__truck')
        user_role = get_user_role(request.user)
        if not request.user.is_superuser and user_role != 'ADMIN':
            qs=qs.filter(trip__truck__owner=request.user)
        return Response([{'id':x.id,'truck_id':x.trip.truck.truck_id,'trip_id':x.trip_id,'product_name':x.product_name,'weight_kg':x.weight_kg,'photo':request.build_absolute_uri(x.photo.url) if x.photo else None,'is_validated':x.is_validated,'created_at':x.created_at} for x in qs[:20]])
