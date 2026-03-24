import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saradhigo_admin.settings')
django.setup()

from dashboard.models import (
    Driver, Vehicle, Ride, SupportTicket,
    GlobalConfiguration, SurgeZone, HeatmapDemand
)


def run():
    print("Clearing old data...")
    HeatmapDemand.objects.all().delete()
    SurgeZone.objects.all().delete()
    GlobalConfiguration.objects.all().delete()
    SupportTicket.objects.all().delete()
    Ride.objects.all().delete()
    Vehicle.objects.all().delete()
    Driver.objects.all().delete()

    print("Creating Drivers...")
    d1 = Driver.objects.create(name="Vikram Rathore",  status="ACTIVE",   rating=4.98, total_trips=1204, total_revenue=Decimal('4280.00'))
    d2 = Driver.objects.create(name="Priya Sharma",    status="ON_TRIP",  rating=4.95, total_trips=850,  total_revenue=Decimal('3912.00'))
    d3 = Driver.objects.create(name="Arjun Singh",     status="OFFLINE",  rating=4.89, total_trips=950,  total_revenue=Decimal('3240.00'))
    d4 = Driver.objects.create(name="Elena Rodriguez", status="ACTIVE",   rating=4.92, total_trips=600,  total_revenue=Decimal('2100.00'))

    print("Creating Vehicles...")
    Vehicle.objects.create(make_model="Toyota Camry",    license_plate="MH01 AB 1234", class_type="Business Sedan", status="AVAILABLE",  driver=d1)
    Vehicle.objects.create(make_model="Honda City",      license_plate="MH02 CD 5678", class_type="Business Sedan", status="IN_USE",     driver=d2)
    Vehicle.objects.create(make_model="Toyota Fortuner", license_plate="MH03 EF 9012", class_type="SUV Elite",      status="MAINTENANCE",driver=d3)
    Vehicle.objects.create(make_model="Hyundai Verna",   license_plate="MH04 GH 3456", class_type="Luxury Auto",   status="AVAILABLE",  driver=d4)

    print("Creating Rides (with vehicle_class for revenue breakdown)...")
    Ride.objects.create(rider_name="Sebastian Vancore", driver=d4, status="COMPLETED",   fare=Decimal('842.50'),  vehicle_class="Luxury Auto")
    Ride.objects.create(rider_name="Aditi Kulkarni",    driver=d1, status="COMPLETED",   fare=Decimal('2450.00'), vehicle_class="SUV Elite")
    Ride.objects.create(rider_name="Neha Kapoor",       driver=d1, status="COMPLETED",   fare=Decimal('1800.00'), vehicle_class="SUV Elite")
    Ride.objects.create(rider_name="Rajan Mehta",       driver=d2, status="COMPLETED",   fare=Decimal('1250.00'), vehicle_class="Business Sedan")
    Ride.objects.create(rider_name="Fatima Sheikh",     driver=d2, status="COMPLETED",   fare=Decimal('980.00'),  vehicle_class="Business Sedan")
    Ride.objects.create(rider_name="Rahul Mishra",      driver=d2, status="IN_PROGRESS", fare=Decimal('150.00'),  vehicle_class="Business Sedan")
    Ride.objects.create(rider_name="Vijay Pratap",      driver=d3, status="CANCELLED",   fare=Decimal('0.00'),    vehicle_class="SUV Elite")

    print("Creating Support Tickets...")
    SupportTicket.objects.create(
        rider_name="Sebastian Vancore", driver=d4, status="OPEN", priority="URGENT",
        description="The driver took a longer route. Estimated fare was ₹680 but was charged ₹842.50."
    )
    SupportTicket.objects.create(
        rider_name="Amit Patel", status="PENDING", priority="HIGH",
        description="Vehicle was swerving through traffic at high speeds..."
    )
    SupportTicket.objects.create(
        rider_name="Sneha Rao", status="OPEN", priority="MEDIUM",
        description="I entered the code FIRSTRIDE but it didn't discount..."
    )

    print("Creating Global Configuration...")
    GlobalConfiguration.objects.create(
        pk=1, base_fare=Decimal('50.00'), surge_multiplier=Decimal('1.5'),
        surge_cap=Decimal('4.0'), per_km_rate=Decimal('12.00'), per_min_rate=Decimal('1.50')
    )

    print("Creating Surge Zones...")
    SurgeZone.objects.create(zone_name="Downtown Central",   multiplier=Decimal('2.4'), requests_per_hour=1240, active_drivers=82,  is_active=True)
    SurgeZone.objects.create(zone_name="Airport Terminal",   multiplier=Decimal('2.1'), requests_per_hour=890,  active_drivers=54,  is_active=True)
    SurgeZone.objects.create(zone_name="Financial District", multiplier=Decimal('1.8'), requests_per_hour=650,  active_drivers=120, is_active=True)
    SurgeZone.objects.create(zone_name="Jubilee Hills",      multiplier=Decimal('1.5'), requests_per_hour=430,  active_drivers=38,  is_active=True)
    SurgeZone.objects.create(zone_name="HITEC City",         multiplier=Decimal('1.3'), requests_per_hour=320,  active_drivers=95,  is_active=True)

    print("Creating Heatmap Demand Zones...")
    HeatmapDemand.objects.create(zone_name="Financial District (BKC)", predicted_surge=Decimal('2.1'), predicted_at_time="18:00", reason="High volume office exit predicted",   is_active=True)
    HeatmapDemand.objects.create(zone_name="Airport Terminal 2",       predicted_surge=Decimal('1.8'), predicted_at_time="19:30", reason="Arrival wave incoming (14 flights)", is_active=True)
    HeatmapDemand.objects.create(zone_name="Bandra West",              predicted_surge=Decimal('1.6'), predicted_at_time="20:00", reason="Evening dining surge expected",       is_active=True)

    print("✅ Mock data loaded successfully!")


if __name__ == '__main__':
    run()
