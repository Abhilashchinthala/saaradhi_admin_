import os
import django
import random
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saradhigo_admin.settings')
django.setup()

from dashboard.models import Driver, Vehicle, Ride, SupportTicket

def run():
    print("Clearing old data...")
    SupportTicket.objects.all().delete()
    Ride.objects.all().delete()
    Vehicle.objects.all().delete()
    Driver.objects.all().delete()

    print("Creating Drivers...")
    d1 = Driver.objects.create(name="Vikram Rathore", status="ACTIVE", rating=4.98, total_trips=1204, total_revenue=Decimal('4280.00'))
    d2 = Driver.objects.create(name="Priya Sharma", status="ON_TRIP", rating=4.95, total_trips=850, total_revenue=Decimal('3912.00'))
    d3 = Driver.objects.create(name="Arjun Singh", status="OFFLINE", rating=4.89, total_trips=950, total_revenue=Decimal('3240.00'))
    d4 = Driver.objects.create(name="Elena Rodriguez", status="ACTIVE", rating=4.92, total_trips=600, total_revenue=Decimal('2100.00'))

    print("Creating Vehicles...")
    Vehicle.objects.create(make_model="Toyota Camry", license_plate="MH01 AB 1234", class_type="Business Sedan", status="AVAILABLE", driver=d1)
    Vehicle.objects.create(make_model="Honda City", license_plate="MH02 CD 5678", class_type="Business Sedan", status="IN_USE", driver=d2)
    Vehicle.objects.create(make_model="Toyota Fortuner", license_plate="MH03 EF 9012", class_type="SUV Elite", status="MAINTENANCE", driver=d3)
    Vehicle.objects.create(make_model="Hyundai Verna", license_plate="MH04 GH 3456", class_type="Luxury Auto", status="AVAILABLE", driver=d4)

    print("Creating Rides...")
    Ride.objects.create(rider_name="Sebastian Vancore", driver=d4, status="COMPLETED", fare=Decimal('42.50'))
    Ride.objects.create(rider_name="Aditi Kulkarni", driver=d1, status="COMPLETED", fare=Decimal('2450.00'))
    Ride.objects.create(rider_name="Rahul Mishra", driver=d2, status="IN_PROGRESS", fare=Decimal('150.00'))
    Ride.objects.create(rider_name="Vijay Pratap", driver=d3, status="CANCELLED", fare=Decimal('0.00'))

    print("Creating Support Tickets...")
    SupportTicket.objects.create(
        rider_name="Sebastian Vancore", 
        driver=d4, 
        status="OPEN", 
        priority="URGENT", 
        description="The driver took a longer route than shown in the app. My estimated fare was $28.00 but I was charged $42.50."
    )
    SupportTicket.objects.create(
        rider_name="Amit Patel", 
        status="PENDING", 
        priority="HIGH", 
        description="Vehicle was swerving through traffic at high speeds..."
    )
    SupportTicket.objects.create(
        rider_name="Sneha Rao", 
        status="OPEN", 
        priority="MEDIUM", 
        description="I entered the code FIRSTRIDE but it didn't discount..."
    )

    print("Mock data loaded successfully!")

if __name__ == '__main__':
    run()
