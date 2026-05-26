from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import (
    GlobalConfiguration, Ride, HeatmapDemand, Driver, Vehicle, 
    SupportTicket, DriverDocument, AdminNotification, SurgeZone, DispatchActionLog
)
from .forms import GlobalConfigurationForm
from decimal import Decimal
from django.utils import timezone
from django.core.paginator import Paginator


class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='password')

    def test_login_success(self):
        response = self.client.post(reverse('login'), {'username': 'admin', 'password': 'password'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('fleet_monitor'))

    def test_login_failure(self):
        response = self.client.post(reverse('login'), {'username': 'admin', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid credentials. Please try again.")

    def test_logout_redirect(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

    def test_unauthenticated_redirect(self):
        # Accessing protected dashboard page redirects to login
        protected_urls = [
            reverse('fleet_monitor'),
            reverse('driver_onboarding'),
            reverse('dispute_support'),
            reverse('executive_revenue'),
            reverse('driver_loyalty'),
            reverse('fare_surge'),
            reverse('payment_dashboard'),
            reverse('predictive_heatmaps'),
            reverse('api_search'),
            reverse('api_notifications'),
        ]
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith(reverse('login')))


class FleetMonitorTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='password')
        self.client.login(username='admin', password='password')
        
        # Drivers in different states
        Driver.objects.create(name="Driver A", rating=4.5, total_trips=10, total_revenue=100.0, status="ACTIVE")
        Driver.objects.create(name="Driver B", rating=4.2, total_trips=15, total_revenue=150.0, status="ON_TRIP")
        Driver.objects.create(name="Driver C", rating=4.0, total_trips=5, total_revenue=50.0, status="OFFLINE")
        
        # Vehicles
        Vehicle.objects.create(make_model="Sedan", license_plate="XYZ-123", class_type="Business Sedan", status="AVAILABLE")
        Vehicle.objects.create(make_model="SUV", license_plate="ABC-456", class_type="SUV Elite", status="IN_USE")

    def test_fleet_monitor_counts(self):
        response = self.client.get(reverse('fleet_monitor'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['active_count'], 1)
        self.assertEqual(response.context['on_trip_count'], 1)
        self.assertEqual(response.context['offline_count'], 1)
        self.assertEqual(response.context['total_vehicles'], 2)
        self.assertEqual(response.context['in_use_vehicles'], 1)


class DriverOnboardingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='password')
        self.client.login(username='admin', password='password')
        
        # Drivers with different onboarding statuses
        self.d1 = Driver.objects.create(name="Driver Pending", rating=4.0, total_trips=0, total_revenue=0.0, onboarding_status="KYC_SUBMITTED")
        self.d2 = Driver.objects.create(name="Driver Approved", rating=4.5, total_trips=0, total_revenue=0.0, onboarding_status="APPROVED")
        self.d3 = Driver.objects.create(name="Driver Rejected", rating=3.5, total_trips=0, total_revenue=0.0, onboarding_status="REJECTED")
        
        # Create documents for self.d1
        self.doc1 = DriverDocument.objects.create(driver=self.d1, doc_type="DL", status="PENDING")
        self.doc2 = DriverDocument.objects.create(driver=self.d1, doc_type="RC", status="PENDING")

    def test_driver_onboarding_filter_all(self):
        response = self.client.get(reverse('driver_onboarding'), {'status': 'ALL'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['drivers']), 3)

    def test_driver_onboarding_filter_pending(self):
        response = self.client.get(reverse('driver_onboarding'), {'status': 'PENDING'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['drivers']), 1)
        self.assertEqual(response.context['drivers'][0].name, "Driver Pending")

    def test_driver_onboarding_filter_approved(self):
        response = self.client.get(reverse('driver_onboarding'), {'status': 'APPROVED'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['drivers']), 1)
        self.assertEqual(response.context['drivers'][0].name, "Driver Approved")

    def test_driver_onboarding_filter_rejected(self):
        response = self.client.get(reverse('driver_onboarding'), {'status': 'REJECTED'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['drivers']), 1)
        self.assertEqual(response.context['drivers'][0].name, "Driver Rejected")

    def test_approve_driver_endpoint(self):
        # Approving a driver should update statuses and create notification
        response = self.client.post(reverse('approve_driver', args=[self.d1.pk]))
        self.assertEqual(response.status_code, 302)
        
        self.d1.refresh_from_db()
        self.assertEqual(self.d1.onboarding_status, "APPROVED")
        self.assertEqual(self.doc1.status, "PENDING") # Need to refresh doc
        self.doc1.refresh_from_db()
        self.assertEqual(self.doc1.status, "APPROVED")
        
        # Check notification
        self.assertTrue(AdminNotification.objects.filter(title="Driver Approved").exists())

    def test_reject_driver_endpoint(self):
        response = self.client.post(reverse('reject_driver', args=[self.d1.pk]))
        self.assertEqual(response.status_code, 302)
        
        self.d1.refresh_from_db()
        self.assertEqual(self.d1.onboarding_status, "REJECTED")
        self.doc1.refresh_from_db()
        self.assertEqual(self.doc1.status, "REJECTED")
        
        # Check notification
        self.assertTrue(AdminNotification.objects.filter(title="Driver Rejected").exists())

    def test_approve_driver_not_found(self):
        response = self.client.post(reverse('approve_driver', args=[9999]))
        self.assertEqual(response.status_code, 302)

    def test_reject_driver_not_found(self):
        response = self.client.post(reverse('reject_driver', args=[9999]))
        self.assertEqual(response.status_code, 302)


class DisputeSupportTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='password')
        self.client.login(username='admin', password='password')
        
        self.driver = Driver.objects.create(name="Driver X", rating=4.5, total_trips=2, total_revenue=20.0)
        
        SupportTicket.objects.create(rider_name="Rider A", driver=self.driver, status="OPEN", priority="URGENT", description="Charged extra")
        SupportTicket.objects.create(rider_name="Rider B", driver=self.driver, status="OPEN", priority="MEDIUM", description="Driver was late")
        SupportTicket.objects.create(rider_name="Rider C", driver=self.driver, status="CLOSED", priority="LOW", description="Lost item found")

    def test_dispute_support_counts_and_list(self):
        response = self.client.get(reverse('dispute_support'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['open_count'], 2)
        self.assertEqual(response.context['urgent_count'], 1)
        self.assertEqual(response.context['total_count'], 3)
        self.assertEqual(len(response.context['tickets']), 3)


class PaymentDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='password')
        self.client.login(username='admin', password='password')
        
        self.driver = Driver.objects.create(name="Driver P", rating=4.5, total_trips=10, total_revenue=1000.0)
        Ride.objects.create(rider_name="Rider X", driver=self.driver, status="COMPLETED", fare=Decimal('150.00'), vehicle_class="Business Sedan")
        Ride.objects.create(rider_name="Rider Y", driver=self.driver, status="COMPLETED", fare=Decimal('250.00'), vehicle_class="SUV Elite")
        Ride.objects.create(rider_name="Rider Z", driver=self.driver, status="CANCELLED", fare=Decimal('50.00'), vehicle_class="Luxury Auto")

    def test_payment_dashboard_aggregates(self):
        response = self.client.get(reverse('payment_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_payments'], Decimal('400.00'))
        self.assertEqual(response.context['completed_count'], 2)
        self.assertEqual(response.context['cancelled_count'], 1)


class DriverLoyaltyTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='password')
        self.client.login(username='admin', password='password')

    def test_loyalty_tier_computation(self):
        d_plat = Driver.objects.create(name="Plat", rating=4.9, total_trips=1050, total_revenue=20000)
        d_gold = Driver.objects.create(name="Gold", rating=4.7, total_trips=550, total_revenue=10000)
        d_silv = Driver.objects.create(name="Silv", rating=4.5, total_trips=250, total_revenue=5000)
        d_bron = Driver.objects.create(name="Bron", rating=4.0, total_trips=50, total_revenue=500)
        
        self.assertEqual(d_plat.loyalty_tier, "PLATINUM")
        self.assertEqual(d_gold.loyalty_tier, "GOLD")
        self.assertEqual(d_silv.loyalty_tier, "SILVER")
        self.assertEqual(d_bron.loyalty_tier, "BRONZE")

    def test_driver_loyalty_view(self):
        Driver.objects.create(name="LDriver", rating=4.8, total_trips=100, total_revenue=1000, onboarding_status="APPROVED")
        response = self.client.get(reverse('driver_loyalty'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['active_loyalty_drivers'], 1)


class PredictiveHeatmapTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='password')
        self.client.login(username='admin', password='password')
        
        Driver.objects.create(name="D1", rating=4.5, total_trips=10, total_revenue=100.0, status="ACTIVE")
        Driver.objects.create(name="D2", rating=4.5, total_trips=10, total_revenue=100.0, status="OFFLINE")
        
        # Ride in progress
        driver = Driver.objects.create(name="D3", rating=4.5, total_trips=10, total_revenue=100.0, status="ON_TRIP")
        Ride.objects.create(rider_name="R1", driver=driver, status="IN_PROGRESS", fare=100.0)
        
        HeatmapDemand.objects.create(zone_name="Zone A", predicted_surge=2.0, is_active=True)

    def test_predictive_heatmaps_view(self):
        response = self.client.get(reverse('predictive_heatmaps'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['active_drivers'], 2) # D1 (ACTIVE) + D3 (ON_TRIP)
        self.assertEqual(response.context['total_drivers'], 3)
        self.assertEqual(response.context['pending_rides'], 1)
        self.assertEqual(len(response.context['demand_zones']), 1)


class SearchTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='password')
        self.client.login(username='admin', password='password')
        
        self.driver = Driver.objects.create(name="Ashok Kumar", rating=4.8, total_trips=15, total_revenue=2000.0)
        Ride.objects.create(rider_name="Vikram Singh", driver=self.driver, status="COMPLETED", fare=150.0)

    def test_search_by_driver_name(self):
        response = self.client.get(reverse('api_search'), {'q': 'Ashok'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertTrue(len(data['results']) > 0)
        self.assertEqual(data['results'][0]['type'], 'driver')
        self.assertEqual(data['results'][0]['title'], 'Ashok Kumar')

    def test_search_by_rider_name(self):
        response = self.client.get(reverse('api_search'), {'q': 'Vikram'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertTrue(len(data['results']) > 0)
        self.assertEqual(data['results'][0]['type'], 'ride')
        self.assertIn('Vikram Singh', data['results'][0]['title'])

    def test_search_empty_query(self):
        response = self.client.get(reverse('api_search'), {'q': ''})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(len(data['results']), 0)


class NotificationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='password')
        self.client.login(username='admin', password='password')
        
        self.n1 = AdminNotification.objects.create(title="Alert A", message="Details", notification_type="ALERT", is_read=False)
        self.n2 = AdminNotification.objects.create(title="Info B", message="Details", notification_type="INFO", is_read=True)

    def test_api_notifications_list(self):
        response = self.client.get(reverse('api_notifications'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        # Only unread notification is returned
        self.assertEqual(len(data['notifications']), 1)
        self.assertEqual(data['notifications'][0]['title'], "Alert A")

    def test_mark_notification_read(self):
        response = self.client.post(reverse('mark_notification_read', args=[self.n1.pk]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        
        self.n1.refresh_from_db()
        self.assertTrue(self.n1.is_read)

    def test_mark_notification_read_not_found(self):
        response = self.client.post(reverse('mark_notification_read', args=[9999]))
        self.assertEqual(response.status_code, 404)


class FormValidationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='password')
        self.client.login(username='admin', password='password')
        self.config = GlobalConfiguration.objects.create(pk=1, base_fare=Decimal('50.00'))

    def test_global_config_form_valid(self):
        form_data = {
            'base_fare': 60.00,
            'surge_multiplier': 1.5,
            'surge_cap': 3.5,
            'per_km_rate': 12.00,
            'per_min_rate': 1.80
        }
        form = GlobalConfigurationForm(data=form_data, instance=self.config)
        self.assertTrue(form.is_valid())

    def test_global_config_form_invalid(self):
        # base_fare cannot be negative
        form_data = {
            'base_fare': -10.00,
            'surge_multiplier': 1.5,
            'surge_cap': 3.5,
            'per_km_rate': 12.00,
            'per_min_rate': 1.80
        }
        form = GlobalConfigurationForm(data=form_data, instance=self.config)
        self.assertFalse(form.is_valid())

    def test_dispatch_alert_view_invalid_zone(self):
        response = self.client.post(reverse('dispatch_alert'), {'zone_id': 9999})
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data['status'], 'error')
