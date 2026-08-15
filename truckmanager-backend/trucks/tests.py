from django.contrib.auth.models import User
from django.test import TestCase

from dashboard.services import DashboardService
from trucks.models import Truck
from trucks.serializers import TruckListSerializer


class TruckIdentifierTests(TestCase):
    def test_truck_id_is_generated_if_missing(self):
        owner = User.objects.create_user(
            username='owner2',
            email='owner2@test.com',
            password='pass1234',
        )

        truck = Truck.objects.create(
            truck_id='',
            license_plate='AB-123-CD',
            brand='Volvo',
            model='FH',
            year=2024,
            max_capacity_kg=15000,
            fuel_tank_capacity_l=400,
            owner=owner,
        )

        self.assertRegex(truck.truck_id, r'^TRK-\d{6}$')

    def test_truck_id_is_unique(self):
        owner = User.objects.create_user(
            username='owner3',
            email='owner3@test.com',
            password='pass1234',
        )

        truck_a = Truck.objects.create(
            truck_id='TRK-000001',
            license_plate='AB-123-CD',
            brand='Volvo',
            model='FH',
            year=2024,
            max_capacity_kg=15000,
            fuel_tank_capacity_l=400,
            owner=owner,
        )
        truck_b = Truck.objects.create(
            truck_id='TRK-000002',
            license_plate='EF-456-GH',
            brand='Mercedes',
            model='Actros',
            year=2023,
            max_capacity_kg=16000,
            fuel_tank_capacity_l=450,
            owner=owner,
        )

        self.assertNotEqual(truck_a.truck_id, truck_b.truck_id)
        self.assertTrue(truck_a.truck_id.startswith('TRK-'))
        self.assertTrue(truck_b.truck_id.startswith('TRK-'))

    def test_non_owner_cannot_access_another_owner_truck_realtime_data(self):
        owner = User.objects.create_user(
            username='owner4',
            email='owner4@test.com',
            password='pass1234',
        )
        other_user = User.objects.create_user(
            username='otheruser',
            email='otheruser@test.com',
            password='pass1234',
        )

        truck = Truck.objects.create(
            truck_id='TRK-000003',
            license_plate='GH-789-IJ',
            brand='Iveco',
            model='Stralis',
            year=2022,
            max_capacity_kg=12000,
            fuel_tank_capacity_l=350,
            owner=owner,
        )

        with self.assertRaises(Truck.DoesNotExist):
            DashboardService.get_realtime_data(truck.id, other_user)

    def test_truck_list_serializer_includes_operational_settings(self):
        owner = User.objects.create_user(
            username='owner5',
            email='owner5@test.com',
            password='pass1234',
        )

        truck = Truck.objects.create(
            truck_id='TRK-000004',
            license_plate='KL-012-MN',
            brand='Renault',
            model='D',
            year=2021,
            max_capacity_kg=14000,
            fuel_tank_capacity_l=380,
            owner=owner,
            overload_threshold_kg=5500,
            fuel_theft_threshold_l=4.5,
            fuel_tolerance_threshold_l=3.2,
            abnormal_stop_minutes=40,
            low_fuel_threshold_percent=18,
            speed_limit_kmh=85,
            cost_per_liter=650,
            revenue_per_ton=220000,
            purchase_price=17500000,
            tco_months=24,
        )

        payload = TruckListSerializer(truck).data

        self.assertEqual(payload['overload_threshold_kg'], 5500)
        self.assertEqual(payload['fuel_theft_threshold_l'], 4.5)
        self.assertEqual(payload['fuel_tolerance_threshold_l'], 3.2)
        self.assertEqual(payload['abnormal_stop_minutes'], 40)
        self.assertEqual(payload['low_fuel_threshold_percent'], 18)
        self.assertEqual(payload['speed_limit_kmh'], 85)
        self.assertEqual(payload['cost_per_liter'], 650)
        self.assertEqual(payload['revenue_per_ton'], 220000)
        self.assertEqual(payload['purchase_price'], 17500000)
        self.assertEqual(payload['tco_months'], 24)
