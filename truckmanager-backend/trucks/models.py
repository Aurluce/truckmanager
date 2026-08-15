from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Truck(models.Model):
    truck_id = models.CharField(max_length=50, unique=True, db_index=True)
    license_plate = models.CharField(max_length=20)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    max_capacity_kg = models.FloatField(validators=[MinValueValidator(0)])
    fuel_tank_capacity_l = models.FloatField(validators=[MinValueValidator(0)])
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trucks')
    driver = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='driven_trucks'
    )

    # Embarqué ESP32 / OBD
    esp32_device_id = models.CharField(max_length=80, blank=True, null=True, unique=True)
    esp32_mac_address = models.CharField(max_length=32, blank=True, null=True)
    firmware_version = models.CharField(max_length=40, blank=True, default='')
    api_key = models.CharField(max_length=128, blank=True, null=True, unique=True)

    # Seuils métier
    overload_threshold_kg = models.FloatField(default=3000, validators=[MinValueValidator(0)])
    fuel_theft_threshold_l = models.FloatField(default=2.0, validators=[MinValueValidator(0)])
    fuel_tolerance_threshold_l = models.FloatField(default=2.0, validators=[MinValueValidator(0)])
    abnormal_stop_minutes = models.IntegerField(default=30, validators=[MinValueValidator(1)])
    low_fuel_threshold_percent = models.FloatField(default=15, validators=[MinValueValidator(0)])
    speed_limit_kmh = models.FloatField(default=90, validators=[MinValueValidator(0)])

    # Paramétrage financier
    cost_per_km = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cost_per_liter = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    revenue_per_ton = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    purchase_price = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='Prix d\'achat')
    tco_months = models.IntegerField(default=12, validators=[MinValueValidator(1)], verbose_name='Durée TCO (mois)')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['truck_id']),
            models.Index(fields=['owner', 'is_active']),
        ]

    def generate_unique_truck_id(self):
        last = Truck.objects.filter(truck_id__startswith='TRK-').order_by('-id').first()
        n = 0
        if last:
            try: n = int(last.truck_id.replace('TRK-', ''))
            except ValueError: pass
        self.truck_id = f'TRK-{n+1:06d}'

    def save(self, *args, **kwargs):
        if not self.truck_id or not self.truck_id.strip():
            self.generate_unique_truck_id()
        else:
            self.truck_id = self.truck_id.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.truck_id} - {self.license_plate}"

    def get_current_trip(self):
        return self.trips.filter(status='IN_PROGRESS').first()
