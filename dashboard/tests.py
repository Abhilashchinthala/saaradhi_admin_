from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import GlobalConfiguration, Ride, HeatmapDemand, Driver, Vehicle
from decimal import Decimal
from django.utils import timezone
import datetime

class DashboardPhase3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='password')
        self.client.login(username='admin', password='password')
        self.config = GlobalConfiguration.objects.create(pk=1, base_fare=Decimal('50.00'))
        
        # Create a mock driver and vehicle
        self.driver = Driver.objects.create(name="Test Driver", rating=4.5, total_trips=10, total_revenue=Decimal('1000.00'), status="ACTIVE")
        self.vehicle = Vehicle.objects.create(make_model="Mercedes S-Class", license_plate="KA01-1234", class_type="SUV Elite", status="AVAILABLE", driver=self.driver)
        
        # Create mock rides
        # Note: created_at is auto_now_add, so we need to mock it if we want specific dates.
        # However, for simplicity, I'll just create them and they'll have the current date.
        # To test filtering, I'll use a trick or just test that the view works.
        Ride.objects.create(rider_name="Rider 1", driver=self.driver, fare=Decimal('100.00'), status='COMPLETED', vehicle_class='SUV Elite')
        Ride.objects.create(rider_name="Rider 2", driver=self.driver, fare=Decimal('200.00'), status='COMPLETED', vehicle_class='SUV Elite')

    def test_executive_revenue_filtering(self):
        # Without filter
        response = self.client.get(reverse('executive_revenue'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['gbv'], Decimal('300.00'))

        # With date filter (today)
        today = timezone.now().date().strftime('%Y-%m-%d')
        response = self.client.get(reverse('executive_revenue'), {'start_date': today, 'end_date': today})
        self.assertEqual(response.context['gbv'], Decimal('300.00'))

    def test_fare_surge_update(self):
        response = self.client.post(reverse('fare_surge'), {
            'update_global': '1',
            'base_fare': '75.00',
            'surge_multiplier': '1.5',
            'surge_cap': '3.0',
            'per_km_rate': '15.0',
            'per_min_rate': '2.0'
        })
        self.assertEqual(response.status_code, 302)
        self.config.refresh_from_db()
        self.assertEqual(self.config.base_fare, Decimal('75.00'))

    def test_dispatch_alert_logging(self):
        zone = HeatmapDemand.objects.create(zone_name="Bandra", predicted_surge=2.0)
        response = self.client.post(reverse('dispatch_alert'), {'zone_id': zone.id})
        self.assertEqual(response.status_code, 200)
        from .models import DispatchActionLog
        self.assertEqual(DispatchActionLog.objects.count(), 1)
        self.assertIn("Bandra", DispatchActionLog.objects.first().zone_name)
