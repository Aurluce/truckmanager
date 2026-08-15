import math
from django.db import models
from trucks.models import Truck
class Trip(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS='IN_PROGRESS','En cours'; COMPLETED='COMPLETED','Terminé'; CANCELLED='CANCELLED','Annulé'
    truck=models.ForeignKey(Truck,on_delete=models.CASCADE,related_name='trips')
    start_time=models.DateTimeField()
    end_time=models.DateTimeField(null=True,blank=True)
    start_location=models.CharField(max_length=255,default='Non renseigné')
    end_location=models.CharField(max_length=255,null=True,blank=True)
    total_distance_km=models.FloatField(default=0)
    total_fuel_consumed_l=models.FloatField(default=0)
    avg_fuel_consumption_l_100km=models.FloatField(default=0)
    avg_fuel_per_ton_km=models.FloatField(default=0)
    max_weight_kg=models.FloatField(default=0)
    avg_weight_kg=models.FloatField(default=0)
    status=models.CharField(max_length=20,choices=Status.choices,default=Status.IN_PROGRESS)
    created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        ordering=['-start_time']; indexes=[models.Index(fields=['truck','start_time']),models.Index(fields=['status'])]
    def calculate_distance(self):
        points=list(self.gps_positions.order_by('timestamp').values_list('latitude','longitude'))
        total=0
        r=6371.0
        for (a,b),(c,d) in zip(points,points[1:]):
            p1,p2=math.radians(a),math.radians(c); dp=math.radians(c-a); dl=math.radians(d-b)
            h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
            total+=2*r*math.asin(math.sqrt(h))
        return round(total,3)
    def recalculate(self):
        from django.db.models import Avg,Max,Sum
        distance=self.calculate_distance()
        fuel=self.fuel_measurements.aggregate(s=Sum('fuel_consumed_liters'))['s'] or 0
        avg_weight=self.weight_measurements.aggregate(a=Avg('calibrated_weight_kg'))['a'] or 0
        max_weight=self.weight_measurements.aggregate(m=Max('calibrated_weight_kg'))['m'] or 0
        self.total_distance_km=distance; self.total_fuel_consumed_l=fuel
        self.avg_weight_kg=round(avg_weight,2); self.max_weight_kg=round(max_weight,2)
        self.avg_fuel_consumption_l_100km=round(fuel*100/distance,2) if distance else 0
        self.avg_fuel_per_ton_km=round(fuel/(avg_weight/1000),2) if avg_weight else 0
        self.save()
