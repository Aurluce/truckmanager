from django.core.management.base import BaseCommand
from django.utils import timezone
from reports.services import build_daily_data
from reports.models import Report
from trucks.models import Truck
import hashlib
class Command(BaseCommand):
    help='Génère les rapports journaliers de tous les camions.'
    def handle(self,*args,**options):
        d=timezone.localdate()
        for truck in Truck.objects.filter(is_active=True):
            data=build_daily_data(truck,d)
            signature=hashlib.sha256(f'{truck.truck_id}|{d}|{data["distance"]:.3f}|{data["fuel"]:.3f}|{data["weight"]:.3f}'.encode()).hexdigest()
            Report.objects.update_or_create(truck=truck,report_date=d,defaults={
                'total_trips':data['trips'].count(),'total_distance_km':data['distance'],'total_weight_kg':data['weight'],
                'total_fuel_consumed_l':data['fuel'],'avg_fuel_consumption_l_100km':data['l100'],'avg_fuel_per_ton_km':data['lton'],
                'total_revenue':data['revenue'],'total_fuel_cost':data['fuel_cost'],'total_alerts':data['alerts'].count(),
                'resolved_alerts':data['alerts'].filter(status='RESOLVED').count(),'signature_hash':signature,'pdf_generated_at':timezone.now()
            })
        self.stdout.write(self.style.SUCCESS(f'Rapports du {d} générés.'))
