from django.db.models import Sum,Avg,Count
from django.utils import timezone
from datetime import timedelta
from trucks.models import Truck
from trips.models import Trip
from measurements.models import WeightMeasurement,FuelMeasurement,GPSPosition
from alerts.models import Alert
from loadings.models import Loading
from core.models import get_user_role

class DashboardService:
    @staticmethod
    def owner_filter(qs,user,prefix=''):
        user_role = get_user_role(user)
        return qs if user.is_superuser or user_role == 'ADMIN' else qs.filter(**{f'{prefix}owner':user})

    @staticmethod
    def get_realtime_data(truck_id, user=None):
        if user is not None:
            user_role = get_user_role(user)
            if not user.is_superuser and user_role != 'ADMIN':
                truck = Truck.objects.filter(id=truck_id, owner=user).first()
                if not truck:
                    raise Truck.DoesNotExist(f"Truck with id={truck_id} does not exist for user {user}")
            else:
                truck = Truck.objects.get(id=truck_id)
        else:
            truck = Truck.objects.get(id=truck_id)

        trip=truck.get_current_trip()

        # Dernière position GPS connue (via tous les trajets du camion)
        last_gps = GPSPosition.objects.filter(trip__truck=truck).order_by('-timestamp').first()

        if not trip:
            # Camion sans trajet en cours → IDLE ou OFFLINE selon la fraîcheur des données
            status = 'OFFLINE'
            last_update = None
            if last_gps:
                last_update = last_gps.timestamp
                elapsed = (timezone.now() - last_gps.timestamp).total_seconds()
                if elapsed < 3600:  # Moins d'1 heure → IDLE
                    status = 'IDLE'
            return {
                'id':truck.id,
                'truck_id':truck.truck_id,
                'license_plate':truck.license_plate,
                'status':status,
                'trip_id':None,
                'current_weight':0,
                'fuel_level':0,
                'fuel_liters':0,
                'speed':last_gps.speed_kmh if last_gps else 0,
                'position':{'lat':last_gps.latitude,'lng':last_gps.longitude} if last_gps else None,
                'last_update':last_update,
                'engine_rpm':0,
                'engine_load':0,
            }

        w=WeightMeasurement.objects.filter(trip=trip).first()
        f=FuelMeasurement.objects.filter(trip=trip).first()
        g=GPSPosition.objects.filter(trip=trip).first()

        # Position : dernière du trajet en cours, sinon dernière connue du camion
        position = None
        if g:
            position = {'lat':g.latitude,'lng':g.longitude}
        elif last_gps:
            position = {'lat':last_gps.latitude,'lng':last_gps.longitude}

        return {
            'id':truck.id,
            'truck_id':truck.truck_id,
            'license_plate':truck.license_plate,
            'status':'IN_TRIP',
            'trip_id':trip.id,
            'start_time':trip.start_time,
            'duration':(timezone.now()-trip.start_time).total_seconds()/3600,
            'current_weight':w.calibrated_weight_kg if w else 0,
            'fuel_level':f.fuel_level_percent if f else 0,
            'fuel_liters':f.fuel_level_liters if f else 0,
            'speed':g.speed_kmh if g else (f.speed_kmh if f else 0),
            'position':position,
            'last_update':max([x.timestamp for x in [w,f,g] if x] or [trip.start_time]),
            'engine_rpm':f.engine_rpm if f else 0,
            'engine_load':f.engine_load if f else 0,
            'is_overloaded':w.is_overloaded if w else False
        }

    @staticmethod
    def fleet(user,truck_id=None):
        qs=Truck.objects.filter(is_active=True)
        user_role = get_user_role(user)
        if not user.is_superuser and user_role != 'ADMIN': qs=qs.filter(owner=user)
        if truck_id: qs=qs.filter(id=truck_id)
        out=[]
        for t in qs:
            d=DashboardService.get_realtime_data(t.id, user)
            out.append(d)
        return out

    @staticmethod
    def summary(user,days=30,truck_id=None):
        trucks=Truck.objects.filter(is_active=True)
        user_role = get_user_role(user)
        if not user.is_superuser and user_role != 'ADMIN': trucks=trucks.filter(owner=user)
        if truck_id: trucks=trucks.filter(id=truck_id)
        trips=Trip.objects.filter(truck__in=trucks,start_time__gte=timezone.now()-timedelta(days=days))
        completed=trips.filter(status='COMPLETED')
        distance=completed.aggregate(s=Sum('total_distance_km'))['s'] or 0
        fuel=completed.aggregate(s=Sum('total_fuel_consumed_l'))['s'] or 0
        alerts=Alert.objects.filter(truck__in=trucks,triggered_at__gte=timezone.now()-timedelta(days=days))
        weight=WeightMeasurement.objects.filter(trip__in=trips).aggregate(a=Avg('calibrated_weight_kg'))['a'] or 0
        revenue=sum(float(t.revenue_per_ton or 0)*float((Loading.objects.filter(trip__in=completed,trip__truck=t).aggregate(s=Sum('weight_kg'))['s'] or 0))/1000 for t in trucks)
        fuel_cost=sum(float(t.cost_per_liter or 0)*float(completed.filter(truck=t).aggregate(s=Sum('total_fuel_consumed_l'))['s'] or 0) for t in trucks)
        return {'period_days':days,'trucks':{'total':trucks.count(),'active':trucks.filter(is_active=True).count(),'in_trip':trucks.filter(trips__status='IN_PROGRESS').distinct().count()},
                'trips':{'total':trips.count(),'completed':completed.count(),'distance_km':round(distance,2),'fuel_l':round(fuel,2),'consumption_l_100km':round(fuel*100/distance,2) if distance else 0,'avg_weight_kg':round(weight,2)},
                'alerts':{'total':alerts.count(),'pending':alerts.filter(status='PENDING').count(),'critical':alerts.filter(alert_type__in=['OVERLOAD','FUEL_THEFT']).filter(status='PENDING').count()},
                'financial':{'revenue_fcfa':round(revenue,0),'fuel_cost_fcfa':round(fuel_cost,0),'margin_fcfa':round(revenue-fuel_cost,0)}}