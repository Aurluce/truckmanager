"""
Commande de seed pour insérer des données de test dans toutes les tables.
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal

from core.models import UserProfile
from trucks.models import Truck
from trips.models import Trip
from measurements.models import WeightMeasurement, FuelMeasurement, GPSPosition
from alerts.models import Alert
from loadings.models import Loading
from reports.models import Report


class Command(BaseCommand):
    help = "Insère des données de test dans toutes les tables (propriétaire ID=7)"

    def handle(self, *args, **options):
        self.stdout.write("Début du seed des données de test...")

        # ============================================================
        # 1. VÉRIFICATION DU PROPRIÉTAIRE (ID=7)
        # ============================================================
        try:
            owner = User.objects.get(pk=7)
        except User.DoesNotExist:
            self.stderr.write("ERREUR : L'utilisateur propriétaire avec ID=7 n'existe pas.")
            self.stderr.write("Créez d'abord un utilisateur avec ID=7 puis relancez cette commande.")
            return

        # S'assurer que le profil du propriétaire est OWNER
        profile, _ = UserProfile.objects.get_or_create(
            user=owner,
            defaults={'role': UserProfile.ROLE_OWNER, 'company_name': 'Transports Douala SARL'}
        )
        profile.role = UserProfile.ROLE_OWNER
        profile.company_name = profile.company_name or 'Transports Douala SARL'
        profile.phone_number = profile.phone_number or '+237 690 000 007'
        profile.save()
        self.stdout.write(f"✓ Propriétaire confirmé : {owner.username} (ID={owner.id})")

        # ============================================================
        # 2. CRÉATION DES CONDUCTEURS (DRIVERS)
        # ============================================================
        drivers = []
        driver_data = [
            {'username': 'driver1', 'first_name': 'Jean', 'last_name': 'Mbarga', 'phone': '+237 690 111 111'},
            {'username': 'driver2', 'first_name': 'Paul', 'last_name': 'Nkoulou', 'phone': '+237 690 222 222'},
            {'username': 'driver3', 'first_name': 'Marie', 'last_name': 'Essomba', 'phone': '+237 690 333 333'},
        ]
        for d in driver_data:
            user, created = User.objects.get_or_create(
                username=d['username'],
                defaults={
                    'first_name': d['first_name'],
                    'last_name': d['last_name'],
                    'email': f"{d['username']}@truckmanager.com",
                }
            )
            if created:
                user.set_password('test1234')
                user.save()
            # Profil conducteur (rôle OWNER par défaut, mais on le garde simple)
            UserProfile.objects.get_or_create(
                user=user,
                defaults={'phone_number': d['phone'], 'role': UserProfile.ROLE_OWNER}
            )
            drivers.append(user)
            self.stdout.write(f"✓ Conducteur : {user.username} (ID={user.id})")

        # ============================================================
        # 3. CRÉATION DES CAMIONS (TRUCKS)
        # ============================================================
        trucks = []
        truck_data = [
            {
                'truck_id': 'TRK-000001', 'license_plate': 'LT-1234-AB', 'brand': 'Mercedes-Benz',
                'model': 'Actros 1845', 'year': 2021, 'max_capacity_kg': 18000,
                'fuel_tank_capacity_l': 600, 'driver': drivers[0],
                'esp32_device_id': 'ESP32-001', 'esp32_mac_address': 'AA:BB:CC:DD:EE:01',
                'firmware_version': '1.2.0', 'api_key': 'api_key_truck_001',
                'overload_threshold_kg': 17000, 'fuel_theft_threshold_l': 2.0,
                'abnormal_stop_minutes': 30, 'low_fuel_threshold_percent': 15,
                'speed_limit_kmh': 90, 'cost_per_km': Decimal('350.00'),
                'cost_per_liter': Decimal('650.00'), 'revenue_per_ton': Decimal('25000.00'),
            },
            {
                'truck_id': 'TRK-000002', 'license_plate': 'LT-5678-CD', 'brand': 'Volvo',
                'model': 'FH 460', 'year': 2022, 'max_capacity_kg': 20000,
                'fuel_tank_capacity_l': 700, 'driver': drivers[1],
                'esp32_device_id': 'ESP32-002', 'esp32_mac_address': 'AA:BB:CC:DD:EE:02',
                'firmware_version': '1.2.1', 'api_key': 'api_key_truck_002',
                'overload_threshold_kg': 19000, 'fuel_theft_threshold_l': 2.5,
                'abnormal_stop_minutes': 25, 'low_fuel_threshold_percent': 12,
                'speed_limit_kmh': 85, 'cost_per_km': Decimal('400.00'),
                'cost_per_liter': Decimal('700.00'), 'revenue_per_ton': Decimal('28000.00'),
            },
            {
                'truck_id': 'TRK-000003', 'license_plate': 'LT-9012-EF', 'brand': 'Scania',
                'model': 'R 500', 'year': 2020, 'max_capacity_kg': 16000,
                'fuel_tank_capacity_l': 550, 'driver': drivers[2],
                'esp32_device_id': 'ESP32-003', 'esp32_mac_address': 'AA:BB:CC:DD:EE:03',
                'firmware_version': '1.1.9', 'api_key': 'api_key_truck_003',
                'overload_threshold_kg': 15000, 'fuel_theft_threshold_l': 1.8,
                'abnormal_stop_minutes': 35, 'low_fuel_threshold_percent': 18,
                'speed_limit_kmh': 95, 'cost_per_km': Decimal('320.00'),
                'cost_per_liter': Decimal('620.00'), 'revenue_per_ton': Decimal('23000.00'),
            },
        ]
        for t in truck_data:
            truck, created = Truck.objects.get_or_create(
                truck_id=t['truck_id'],
                defaults={
                    'license_plate': t['license_plate'],
                    'brand': t['brand'],
                    'model': t['model'],
                    'year': t['year'],
                    'max_capacity_kg': t['max_capacity_kg'],
                    'fuel_tank_capacity_l': t['fuel_tank_capacity_l'],
                    'owner': owner,
                    'driver': t['driver'],
                    'esp32_device_id': t['esp32_device_id'],
                    'esp32_mac_address': t['esp32_mac_address'],
                    'firmware_version': t['firmware_version'],
                    'api_key': t['api_key'],
                    'overload_threshold_kg': t['overload_threshold_kg'],
                    'fuel_theft_threshold_l': t['fuel_theft_threshold_l'],
                    'abnormal_stop_minutes': t['abnormal_stop_minutes'],
                    'low_fuel_threshold_percent': t['low_fuel_threshold_percent'],
                    'speed_limit_kmh': t['speed_limit_kmh'],
                    'cost_per_km': t['cost_per_km'],
                    'cost_per_liter': t['cost_per_liter'],
                    'revenue_per_ton': t['revenue_per_ton'],
                    'is_active': True,
                }
            )
            trucks.append(truck)
            self.stdout.write(f"✓ Camion : {truck.truck_id} ({truck.license_plate})")

        # ============================================================
        # 4. CRÉATION DES TRAJETS (TRIPS)
        # ============================================================
        now = timezone.now()
        trips = []
        trip_data = [
            {
                'truck': trucks[0], 'start_time': now - timedelta(days=2, hours=3),
                'end_time': now - timedelta(days=2), 'start_location': 'Douala',
                'end_location': 'Yaoundé', 'total_distance_km': 250.5,
                'total_fuel_consumed_l': 85.3, 'avg_fuel_consumption_l_100km': 34.05,
                'avg_fuel_per_ton_km': 0.021, 'max_weight_kg': 16500,
                'avg_weight_kg': 15200, 'status': Trip.Status.COMPLETED,
            },
            {
                'truck': trucks[0], 'start_time': now - timedelta(days=1, hours=2),
                'end_time': None, 'start_location': 'Yaoundé',
                'end_location': 'Bafoussam', 'total_distance_km': 0,
                'total_fuel_consumed_l': 0, 'avg_fuel_consumption_l_100km': 0,
                'avg_fuel_per_ton_km': 0, 'max_weight_kg': 0,
                'avg_weight_kg': 0, 'status': Trip.Status.IN_PROGRESS,
            },
            {
                'truck': trucks[1], 'start_time': now - timedelta(days=3, hours=4),
                'end_time': now - timedelta(days=3, hours=1), 'start_location': 'Douala',
                'end_location': 'Kribi', 'total_distance_km': 180.2,
                'total_fuel_consumed_l': 62.8, 'avg_fuel_consumption_l_100km': 34.85,
                'avg_fuel_per_ton_km': 0.019, 'max_weight_kg': 18500,
                'avg_weight_kg': 17200, 'status': Trip.Status.COMPLETED,
            },
            {
                'truck': trucks[1], 'start_time': now - timedelta(days=1, hours=5),
                'end_time': now - timedelta(days=1, hours=2), 'start_location': 'Kribi',
                'end_location': 'Ebolowa', 'total_distance_km': 120.0,
                'total_fuel_consumed_l': 40.5, 'avg_fuel_consumption_l_100km': 33.75,
                'avg_fuel_per_ton_km': 0.018, 'max_weight_kg': 17800,
                'avg_weight_kg': 16500, 'status': Trip.Status.COMPLETED,
            },
            {
                'truck': trucks[2], 'start_time': now - timedelta(days=2, hours=6),
                'end_time': now - timedelta(days=2, hours=2), 'start_location': 'Douala',
                'end_location': 'Ngaoundéré', 'total_distance_km': 620.0,
                'total_fuel_consumed_l': 210.0, 'avg_fuel_consumption_l_100km': 33.87,
                'avg_fuel_per_ton_km': 0.022, 'max_weight_kg': 14500,
                'avg_weight_kg': 13800, 'status': Trip.Status.COMPLETED,
            },
            {
                'truck': trucks[2], 'start_time': now - timedelta(hours=8),
                'end_time': None, 'start_location': 'Ngaoundéré',
                'end_location': 'Garoua', 'total_distance_km': 0,
                'total_fuel_consumed_l': 0, 'avg_fuel_consumption_l_100km': 0,
                'avg_fuel_per_ton_km': 0, 'max_weight_kg': 0,
                'avg_weight_kg': 0, 'status': Trip.Status.IN_PROGRESS,
            },
        ]
        for t in trip_data:
            trip, created = Trip.objects.get_or_create(
                truck=t['truck'],
                start_time=t['start_time'],
                defaults={
                    'end_time': t['end_time'],
                    'start_location': t['start_location'],
                    'end_location': t['end_location'],
                    'total_distance_km': t['total_distance_km'],
                    'total_fuel_consumed_l': t['total_fuel_consumed_l'],
                    'avg_fuel_consumption_l_100km': t['avg_fuel_consumption_l_100km'],
                    'avg_fuel_per_ton_km': t['avg_fuel_per_ton_km'],
                    'max_weight_kg': t['max_weight_kg'],
                    'avg_weight_kg': t['avg_weight_kg'],
                    'status': t['status'],
                }
            )
            trips.append(trip)
            self.stdout.write(f"✓ Trajet : {trip.id} ({trip.start_location} → {trip.end_location or '...'})")

        # ============================================================
        # 5. MESURES DE POIDS (WEIGHT MEASUREMENTS)
        # ============================================================
        weight_count = 0
        for trip in trips:
            # Génère 5 mesures de poids par trajet
            base_weight = 14000 + (trip.truck.id % 3) * 1000
            for i in range(5):
                raw = base_weight + i * 150 + (i % 2) * 50
                filtered = raw - 20
                calibrated = filtered - 10
                is_overloaded = calibrated > trip.truck.overload_threshold_kg
                WeightMeasurement.objects.get_or_create(
                    trip=trip,
                    timestamp=trip.start_time + timedelta(minutes=30 * i),
                    defaults={
                        'raw_weight_kg': raw,
                        'filtered_weight_kg': filtered,
                        'calibrated_weight_kg': calibrated,
                        'is_overloaded': is_overloaded,
                    }
                )
                weight_count += 1
        self.stdout.write(f"✓ {weight_count} mesures de poids insérées")

        # ============================================================
        # 6. MESURES DE CARBURANT (FUEL MEASUREMENTS)
        # ============================================================
        fuel_count = 0
        for trip in trips:
            # Génère 5 mesures de carburant par trajet
            base_fuel = 80.0
            for i in range(5):
                fuel_level = max(5.0, base_fuel - i * 12)
                fuel_liters = fuel_level / 100 * trip.truck.fuel_tank_capacity_l
                speed = 60 + (i * 5) % 40
                rpm = 1200 + i * 150
                engine_load = 40 + (i * 7) % 30
                consumed = 8.5 + i * 1.2
                is_theft = (i == 3 and trip.id % 2 == 0)
                drop = 15.0 if is_theft else 0.0
                FuelMeasurement.objects.get_or_create(
                    trip=trip,
                    timestamp=trip.start_time + timedelta(minutes=30 * i),
                    defaults={
                        'fuel_level_percent': fuel_level,
                        'fuel_level_liters': fuel_liters,
                        'speed_kmh': speed,
                        'engine_rpm': rpm,
                        'engine_load': engine_load,
                        'fuel_consumed_liters': consumed,
                        'is_fuel_theft': is_theft,
                        'fuel_drop_amount': drop,
                    }
                )
                fuel_count += 1
        self.stdout.write(f"✓ {fuel_count} mesures de carburant insérées")

        # ============================================================
        # 7. POSITIONS GPS (GPS POSITIONS)
        # ============================================================
        gps_count = 0
        # Coordonnées approximatives des villes camerounaises
        cities = {
            'Douala': (4.0511, 9.7679),
            'Yaoundé': (3.8480, 11.5021),
            'Bafoussam': (5.4778, 10.4176),
            'Kribi': (2.9373, 9.9077),
            'Ebolowa': (2.9000, 11.1500),
            'Ngaoundéré': (7.3277, 13.5847),
            'Garoua': (9.3014, 13.3977),
        }
        for trip in trips:
            start = cities.get(trip.start_location, (4.0511, 9.7679))
            end = cities.get(trip.end_location, (4.0511, 9.7679))
            # Interpolation linéaire entre départ et arrivée
            for i in range(6):
                t = i / 5.0
                lat = start[0] + (end[0] - start[0]) * t
                lon = start[1] + (end[1] - start[1]) * t
                speed = 50 + (i * 8) % 40
                is_stationary = (i == 2)
                is_abnormal = (i == 2 and trip.id % 3 == 0)
                GPSPosition.objects.get_or_create(
                    trip=trip,
                    timestamp=trip.start_time + timedelta(minutes=45 * i),
                    defaults={
                        'latitude': round(lat, 6),
                        'longitude': round(lon, 6),
                        'altitude': 200 + i * 15,
                        'speed_kmh': speed,
                        'heading': (i * 45) % 360,
                        'accuracy': 3.5 + i * 0.3,
                        'is_stationary': is_stationary,
                        'is_abnormal_stop': is_abnormal,
                    }
                )
                gps_count += 1
        self.stdout.write(f"✓ {gps_count} positions GPS insérées")

        # ============================================================
        # 8. ALERTES (ALERTS)
        # ============================================================
        alert_count = 0
        alert_data = [
            {
                'truck': trucks[0], 'trip': trips[0], 'alert_type': Alert.AlertType.OVERLOAD,
                'message': 'Surcharge détectée : 16 500 kg pour un seuil de 17 000 kg',
                'threshold_value': 17000, 'actual_value': 16500,
                'status': Alert.Status.RESOLVED, 'details': {'weight': 16500, 'threshold': 17000},
            },
            {
                'truck': trucks[0], 'trip': trips[1], 'alert_type': Alert.AlertType.LOW_FUEL,
                'message': 'Niveau de carburant bas : 8%',
                'threshold_value': 15, 'actual_value': 8,
                'status': Alert.Status.PENDING, 'details': {'fuel_percent': 8},
            },
            {
                'truck': trucks[1], 'trip': trips[2], 'alert_type': Alert.AlertType.FUEL_THEFT,
                'message': 'Chute de carburant suspecte : -15 L',
                'threshold_value': 2.5, 'actual_value': 15,
                'status': Alert.Status.IN_PROGRESS, 'details': {'drop': 15, 'threshold': 2.5},
            },
            {
                'truck': trucks[1], 'trip': trips[3], 'alert_type': Alert.AlertType.SPEEDING,
                'message': 'Excès de vitesse : 95 km/h (limite 85 km/h)',
                'threshold_value': 85, 'actual_value': 95,
                'status': Alert.Status.PENDING, 'details': {'speed': 95, 'limit': 85},
            },
            {
                'truck': trucks[2], 'trip': trips[4], 'alert_type': Alert.AlertType.ABNORMAL_STOP,
                'message': 'Arrêt anormal détecté : 45 minutes',
                'threshold_value': 35, 'actual_value': 45,
                'status': Alert.Status.RESOLVED, 'details': {'minutes': 45, 'threshold': 35},
            },
            {
                'truck': trucks[2], 'trip': trips[5], 'alert_type': Alert.AlertType.MAINTENANCE,
                'message': 'Maintenance requise : kilométrage élevé',
                'threshold_value': 100000, 'actual_value': 102500,
                'status': Alert.Status.PENDING, 'details': {'km': 102500},
            },
        ]
        for a in alert_data:
            alert, created = Alert.objects.get_or_create(
                truck=a['truck'],
                trip=a['trip'],
                alert_type=a['alert_type'],
                message=a['message'],
                defaults={
                    'threshold_value': a['threshold_value'],
                    'actual_value': a['actual_value'],
                    'details': a['details'],
                    'status': a['status'],
                }
            )
            if created:
                alert_count += 1
        self.stdout.write(f"✓ {alert_count} alertes insérées")

        # ============================================================
        # 9. CHARGEMENTS (LOADINGS)
        # ============================================================
        loading_count = 0
        loading_data = [
            {
                'trip': trips[0], 'product_name': 'Ciment', 'product_type': 'Matériaux',
                'weight_kg': 15000, 'weight_verified': True, 'is_validated': True,
                'validated_by': owner, 'validated_at': now - timedelta(days=2, hours=2),
            },
            {
                'trip': trips[1], 'product_name': 'Sable', 'product_type': 'Matériaux',
                'weight_kg': 16000, 'weight_verified': True, 'is_validated': False,
            },
            {
                'trip': trips[2], 'product_name': 'Bois', 'product_type': 'Bois',
                'weight_kg': 18000, 'weight_verified': True, 'is_validated': True,
                'validated_by': owner, 'validated_at': now - timedelta(days=3, hours=3),
            },
            {
                'trip': trips[3], 'product_name': 'Cacao', 'product_type': 'Agriculture',
                'weight_kg': 17000, 'weight_verified': False, 'is_validated': False,
            },
            {
                'trip': trips[4], 'product_name': 'Coton', 'product_type': 'Agriculture',
                'weight_kg': 14000, 'weight_verified': True, 'is_validated': True,
                'validated_by': owner, 'validated_at': now - timedelta(days=2, hours=1),
            },
            {
                'trip': trips[5], 'product_name': 'Arachides', 'product_type': 'Agriculture',
                'weight_kg': 13500, 'weight_verified': False, 'is_validated': False,
            },
        ]
        for l in loading_data:
            loading, created = Loading.objects.get_or_create(
                trip=l['trip'],
                product_name=l['product_name'],
                defaults={
                    'product_type': l['product_type'],
                    'weight_kg': l['weight_kg'],
                    'weight_verified': l['weight_verified'],
                    'is_validated': l['is_validated'],
                    'validated_by': l.get('validated_by'),
                    'validated_at': l.get('validated_at'),
                }
            )
            if created:
                loading_count += 1
        self.stdout.write(f"✓ {loading_count} chargements insérés")

        # ============================================================
        # 10. RAPPORTS (REPORTS)
        # ============================================================
        report_count = 0
        for truck in trucks:
            for days_ago in [1, 2, 3]:
                report_date = (now - timedelta(days=days_ago)).date()
                # Calculer des valeurs cohérentes
                total_trips = 2
                total_distance = 400 + truck.id * 50
                total_duration = 8.5
                total_weight = 30000 + truck.id * 2000
                avg_weight = total_weight / total_trips
                total_fuel = 130 + truck.id * 20
                avg_fuel_100 = total_fuel * 100 / total_distance
                avg_fuel_ton = total_fuel / (avg_weight / 1000)
                total_revenue = Decimal(str(total_weight / 1000 * 25000))
                total_fuel_cost = Decimal(str(total_fuel * 650))
                profit = (total_revenue - total_fuel_cost) / total_revenue * 100
                report, created = Report.objects.get_or_create(
                    truck=truck,
                    report_date=report_date,
                    defaults={
                        'total_trips': total_trips,
                        'total_distance_km': total_distance,
                        'total_duration_hours': total_duration,
                        'total_weight_kg': total_weight,
                        'avg_weight_kg': avg_weight,
                        'total_fuel_consumed_l': total_fuel,
                        'avg_fuel_consumption_l_100km': round(avg_fuel_100, 2),
                        'avg_fuel_per_ton_km': round(avg_fuel_ton, 3),
                        'total_revenue': total_revenue,
                        'total_fuel_cost': total_fuel_cost,
                        'profit_margin': round(profit, 2),
                        'total_alerts': 2,
                        'resolved_alerts': 1,
                    }
                )
                if created:
                    report_count += 1
        self.stdout.write(f"✓ {report_count} rapports insérés")

        # ============================================================
        # RÉSUMÉ FINAL
        # ============================================================
        self.stdout.write(self.style.SUCCESS("\n✅ Seed terminé avec succès !"))
        self.stdout.write(f"   Propriétaire : {owner.username} (ID={owner.id})")
        self.stdout.write(f"   Conducteurs : {len(drivers)}")
        self.stdout.write(f"   Camions : {len(trucks)}")
        self.stdout.write(f"   Trajets : {len(trips)}")
        self.stdout.write(f"   Mesures de poids : {weight_count}")
        self.stdout.write(f"   Mesures de carburant : {fuel_count}")
        self.stdout.write(f"   Positions GPS : {gps_count}")
        self.stdout.write(f"   Alertes : {alert_count}")
        self.stdout.write(f"   Chargements : {loading_count}")
        self.stdout.write(f"   Rapports : {report_count}")