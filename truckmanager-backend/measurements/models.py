from django.db import models
from trips.models import Trip

class WeightMeasurement(models.Model):
    trip=models.ForeignKey(Trip,on_delete=models.CASCADE,related_name='weight_measurements')
    raw_weight_kg=models.FloatField()
    filtered_weight_kg=models.FloatField()
    calibrated_weight_kg=models.FloatField()
    is_overloaded=models.BooleanField(default=False)
    timestamp=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-timestamp']; indexes=[models.Index(fields=['trip','timestamp'])]
class FuelMeasurement(models.Model):
    trip=models.ForeignKey(Trip,on_delete=models.CASCADE,related_name='fuel_measurements')
    fuel_level_percent=models.FloatField()
    fuel_level_liters=models.FloatField()
    speed_kmh=models.FloatField(null=True,blank=True)
    engine_rpm=models.IntegerField(null=True,blank=True)
    engine_load=models.FloatField(null=True,blank=True)
    fuel_consumed_liters=models.FloatField(default=0)
    is_fuel_theft=models.BooleanField(default=False)
    fuel_drop_amount=models.FloatField(default=0)
    timestamp=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-timestamp']; indexes=[models.Index(fields=['trip','timestamp'])]
class GPSPosition(models.Model):
    trip=models.ForeignKey(Trip,on_delete=models.CASCADE,related_name='gps_positions')
    latitude=models.FloatField()
    longitude=models.FloatField()
    altitude=models.FloatField(null=True,blank=True)
    speed_kmh=models.FloatField(default=0)
    heading=models.IntegerField(null=True,blank=True)
    accuracy=models.FloatField(null=True,blank=True)
    is_stationary=models.BooleanField(default=False)
    is_abnormal_stop=models.BooleanField(default=False)
    timestamp=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-timestamp']; indexes=[models.Index(fields=['trip','timestamp'])]
