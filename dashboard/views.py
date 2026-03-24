from django.shortcuts import render
from .models import Driver, Vehicle, Ride, SupportTicket

def login_view(request):
    return render(request, 'login.html')

def fleet_monitor_view(request):
    drivers = Driver.objects.all()
    vehicles = Vehicle.objects.all()
    context = {'drivers': drivers, 'vehicles': vehicles, 'active_count': drivers.filter(status='ACTIVE').count()}
    return render(request, 'fleet_monitor.html', context)

def driver_onboarding_view(request):
    drivers = Driver.objects.all()
    return render(request, 'driver_onboarding.html', {'drivers': drivers})

def dispute_support_view(request):
    tickets = SupportTicket.objects.all().order_by('-created_at')
    return render(request, 'dispute_support.html', {'tickets': tickets})

def executive_revenue_view(request):
    return render(request, 'executive_revenue.html')

def driver_loyalty_view(request):
    top_drivers = Driver.objects.order_by('-rating')[:5]
    return render(request, 'driver_loyalty.html', {'top_drivers': top_drivers})

def fare_surge_view(request):
    return render(request, 'fare_surge.html')

def payment_dashboard_view(request):
    rides = Ride.objects.all().order_by('-date')
    return render(request, 'payment_dashboard.html', {'rides': rides})

def predictive_heatmaps_view(request):
    return render(request, 'predictive_heatmaps.html')
