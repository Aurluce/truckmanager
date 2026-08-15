from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from trucks.models import Truck
from trips.models import Trip
from measurements.models import WeightMeasurement,FuelMeasurement,GPSPosition
from alerts.models import Alert

def device_truck(request):
    key=request.headers.get('X-API-Key') or request.data.get('api_key')
    device=request.headers.get('X-Device-ID') or request.data.get('camion_id') or request.data.get('truck_id')
    if not key and not device: return None
    qs=Truck.objects.all()
    if key: qs=qs.filter(api_key=key)
    else: qs=qs.filter(esp32_device_id=device)
    return qs.first()

def get_trip(truck, timestamp=None, start_location='GPS'):
    trip=truck.get_current_trip()
    if trip: return trip
    return Trip.objects.create(truck=truck,start_time=timestamp or timezone.now(),start_location=start_location)

class DeviceTelemetryView(APIView):
    permission_classes=[permissions.AllowAny]
    def post(self,request):
        truck=device_truck(request)
        if not truck: return Response({'error':'Camion ou clé API invalide'},status=401)
        data=request.data; ts=data.get('timestamp')
        from django.utils.dateparse import parse_datetime
        timestamp=parse_datetime(ts) if isinstance(ts,str) else None
        gps=data.get('gps') or {}
        trip=get_trip(truck,timestamp)
        created={'weight':False,'fuel':False,'gps':False,'alerts':0}
        if data.get('poids_kg') is not None:
            weight=float(data['poids_kg']); overloaded=weight>truck.overload_threshold_kg
            WeightMeasurement.objects.create(trip=trip,raw_weight_kg=weight,filtered_weight_kg=weight,calibrated_weight_kg=weight,is_overloaded=overloaded)
            created['weight']=True
            if overloaded:
                Alert.objects.create(truck=truck,trip=trip,alert_type='OVERLOAD',message=f'Surcharge détectée: {weight:.1f} kg',threshold_value=truck.overload_threshold_kg,actual_value=weight)
        if data.get('carburant_pct') is not None:
            pct=float(data['carburant_pct']); liters=pct*truck.fuel_tank_capacity_l/100
            previous=FuelMeasurement.objects.filter(trip=trip).order_by('-timestamp').first()
            drop=(previous.fuel_level_liters-liters) if previous else 0
            tolerance_threshold = float(getattr(truck, 'fuel_tolerance_threshold_l', truck.fuel_theft_threshold_l) or truck.fuel_theft_threshold_l)
            theft=drop>=tolerance_threshold and (not gps.get('vitesse_kmh') or float(gps.get('vitesse_kmh',0))<5)
            FuelMeasurement.objects.create(trip=trip,fuel_level_percent=pct,fuel_level_liters=liters,
                speed_kmh=gps.get('vitesse_kmh'),engine_rpm=data.get('rpm'),engine_load=data.get('charge_moteur'),
                fuel_consumed_liters=max(drop,0),is_fuel_theft=theft,fuel_drop_amount=max(drop,0))
            created['fuel']=True
            if theft:
                Alert.objects.create(truck=truck,trip=trip,alert_type='FUEL_THEFT',message=f'Baisse carburant de {drop:.1f} L',threshold_value=tolerance_threshold,actual_value=drop)
            if pct<=truck.low_fuel_threshold_percent:
                Alert.objects.create(truck=truck,trip=trip,alert_type='LOW_FUEL',message=f'Niveau carburant bas: {pct:.1f}%',threshold_value=truck.low_fuel_threshold_percent,actual_value=pct)
        if gps.get('lat') is not None and gps.get('lng') is not None:
            speed=float(gps.get('vitesse_kmh',gps.get('speed_kmh',0)) or 0)
            stationary=speed<3
            last=GPSPosition.objects.filter(trip=trip).order_by('-timestamp').first()
            abnormal=False
            if stationary and last and (timestamp or timezone.now())-last.timestamp>timedelta(minutes=truck.abnormal_stop_minutes):
                abnormal=True
            GPSPosition.objects.create(trip=trip,latitude=float(gps['lat']),longitude=float(gps['lng']),speed_kmh=speed,
                altitude=gps.get('altitude'),heading=gps.get('heading'),accuracy=gps.get('accuracy'),
                is_stationary=stationary,is_abnormal_stop=abnormal)
            created['gps']=True
            if abnormal:
                Alert.objects.create(truck=truck,trip=trip,alert_type='ABNORMAL_STOP',message='Arrêt anormal détecté',threshold_value=truck.abnormal_stop_minutes,actual_value=truck.abnormal_stop_minutes)
            if speed>truck.speed_limit_kmh:
                Alert.objects.create(truck=truck,trip=trip,alert_type='SPEEDING',message=f'Excès de vitesse: {speed:.1f} km/h',threshold_value=truck.speed_limit_kmh,actual_value=speed)
        for alert_type in data.get('alertes',[]) or []:
            mapping={'surcharge':'OVERLOAD','vol_carburant':'FUEL_THEFT','arrêt_anormal':'ABNORMAL_STOP','arret_anormal':'ABNORMAL_STOP'}
            code=mapping.get(str(alert_type),str(alert_type).upper())
            if code in dict(Alert.AlertType.choices):
                Alert.objects.create(truck=truck,trip=trip,alert_type=code,message=f'Alerte embarquée: {alert_type}',threshold_value=0,actual_value=0,details={'source':'ESP32'})
                created['alerts']+=1
        return Response({'success':True,'truck_id':truck.truck_id,'trip_id':trip.id,'stored':created},status=201)

class DeviceWeightView(APIView):
    permission_classes=[permissions.AllowAny]
    def post(self,request):
        data=dict(request.data); data.setdefault('timestamp',timezone.now().isoformat())
        r=DeviceTelemetryView().post(type('Req',(),{'headers':request.headers,'data':data})())
        return r
class DeviceFuelView(APIView):
    permission_classes=[permissions.AllowAny]
    def post(self,request):
        data=dict(request.data); data.setdefault('timestamp',timezone.now().isoformat())
        r=DeviceTelemetryView().post(type('Req',(),{'headers':request.headers,'data':data})())
        return r
class DeviceGPSView(APIView):
    permission_classes=[permissions.AllowAny]
    def post(self,request):
        data=dict(request.data); data.setdefault('timestamp',timezone.now().isoformat())
        r=DeviceTelemetryView().post(type('Req',(),{'headers':request.headers,'data':data})())
        return r
class DeviceAlertView(APIView):
    permission_classes=[permissions.AllowAny]
    def post(self,request):
        data=dict(request.data); data.setdefault('timestamp',timezone.now().isoformat())
        r=DeviceTelemetryView().post(type('Req',(),{'headers':request.headers,'data':data})())
        return r


class DeviceLoadingView(APIView):
    permission_classes=[permissions.AllowAny]
    def post(self,request):
        truck=device_truck(request)
        if not truck: return Response({'error':'Camion ou clé API invalide'},401)
        trip=get_trip(truck)
        from loadings.models import Loading
        from django.utils.dateparse import parse_datetime
        obj=Loading.objects.create(trip=trip,product_name=request.data.get('product_name','Produit non renseigné'),
            product_type=request.data.get('product_type',''),weight_kg=float(request.data.get('weight_kg',request.data.get('poids_kg',0))),
            weight_verified=bool(request.data.get('weight_verified',True)))
        return Response({'id':obj.id,'truck_id':truck.truck_id,'trip_id':trip.id,'status':'received'},201)
