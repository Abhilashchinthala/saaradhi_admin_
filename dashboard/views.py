from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from decimal import Decimal

from .models import Driver, Vehicle, Ride, SupportTicket, GlobalConfiguration, SurgeZone, HeatmapDemand


def login_view(request):
    if request.user.is_authenticated:
        return redirect('fleet_monitor')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('fleet_monitor')
        else:
            error = "Invalid credentials. Please try again."
    return render(request, 'login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def fleet_monitor_view(request):
    drivers = Driver.objects.all()
    vehicles = Vehicle.objects.all()
    context = {
        'drivers': drivers,
        'vehicles': vehicles,
        'active_count': drivers.filter(status='ACTIVE').count(),
        'on_trip_count': drivers.filter(status='ON_TRIP').count(),
        'offline_count': drivers.filter(status='OFFLINE').count(),
        'total_vehicles': vehicles.count(),
        'in_use_vehicles': vehicles.filter(status='IN_USE').count(),
    }
    return render(request, 'fleet_monitor.html', context)


@login_required(login_url='login')
def driver_onboarding_view(request):
    drivers = Driver.objects.all()
    return render(request, 'driver_onboarding.html', {'drivers': drivers})


@login_required(login_url='login')
def dispute_support_view(request):
    tickets = SupportTicket.objects.all().order_by('-created_at')
    context = {
        'tickets': tickets,
        'open_count': tickets.filter(status='OPEN').count(),
        'urgent_count': tickets.filter(priority='URGENT').count(),
        'total_count': tickets.count(),
    }
    return render(request, 'dispute_support.html', context)


@login_required(login_url='login')
def executive_revenue_view(request):
    # Compute GBV from completed rides
    completed_rides = Ride.objects.filter(status='COMPLETED')
    gbv = completed_rides.aggregate(total=Sum('fare'))['total'] or Decimal('0')
    platform_revenue = gbv * Decimal('0.20')
    take_rate = 20.0

    # Revenue per vehicle class
    class_revenue = {}
    total_class_revenue = Decimal('0')
    for cls in ['SUV Elite', 'Business Sedan', 'Luxury Auto']:
        rev = completed_rides.filter(vehicle_class=cls).aggregate(total=Sum('fare'))['total'] or Decimal('0')
        class_revenue[cls] = rev
        total_class_revenue += rev

    class_breakdown = []
    for cls, rev in class_revenue.items():
        pct = round((rev / total_class_revenue * 100), 1) if total_class_revenue > 0 else 0
        class_breakdown.append({'name': cls, 'revenue': rev, 'pct': pct})

    # Fleet utilization
    total_vehicles = Vehicle.objects.count()
    in_use = Vehicle.objects.filter(status='IN_USE').count()
    fleet_utilization = round((in_use / total_vehicles * 100), 1) if total_vehicles > 0 else 0

    context = {
        'gbv': gbv,
        'platform_revenue': platform_revenue,
        'take_rate': take_rate,
        'fleet_utilization': fleet_utilization,
        'class_breakdown': class_breakdown,
        'total_rides': completed_rides.count(),
    }
    return render(request, 'executive_revenue.html', context)


@login_required(login_url='login')
def driver_loyalty_view(request):
    top_drivers = Driver.objects.order_by('-rating')[:5]
    return render(request, 'driver_loyalty.html', {'top_drivers': top_drivers})


@login_required(login_url='login')
def fare_surge_view(request):
    # Get or create a single global config row
    config, _ = GlobalConfiguration.objects.get_or_create(pk=1)
    surge_zones = SurgeZone.objects.filter(is_active=True).order_by('-multiplier')

    peak_zone = surge_zones.first()
    avg_multiplier = 0
    if surge_zones.exists():
        total_m = sum(z.multiplier for z in surge_zones)
        avg_multiplier = round(total_m / surge_zones.count(), 1)

    context = {
        'config': config,
        'surge_zones': surge_zones,
        'active_zones_count': surge_zones.count(),
        'peak_zone': peak_zone,
        'avg_multiplier': avg_multiplier,
    }
    return render(request, 'fare_surge.html', context)


@login_required(login_url='login')
def payment_dashboard_view(request):
    rides = Ride.objects.all().order_by('-date')
    total_payments = rides.filter(status='COMPLETED').aggregate(total=Sum('fare'))['total'] or Decimal('0')
    context = {
        'rides': rides,
        'total_payments': total_payments,
        'completed_count': rides.filter(status='COMPLETED').count(),
        'cancelled_count': rides.filter(status='CANCELLED').count(),
    }
    return render(request, 'payment_dashboard.html', context)


@login_required(login_url='login')
def predictive_heatmaps_view(request):
    all_drivers = Driver.objects.count()
    active_drivers = Driver.objects.filter(status='ACTIVE').count() + Driver.objects.filter(status='ON_TRIP').count()
    pending_rides = Ride.objects.filter(status='IN_PROGRESS').count()

    # Supply/demand ratio
    demand_zones = HeatmapDemand.objects.filter(is_active=True).order_by('-predicted_surge')
    total_requests = Ride.objects.filter(status='IN_PROGRESS').count()
    supply_ratio = round((active_drivers / (active_drivers + pending_rides + 1)) * 100) if (active_drivers + pending_rides) > 0 else 50
    deficit_pct = 100 - supply_ratio

    context = {
        'active_drivers': active_drivers,
        'total_drivers': all_drivers,
        'pending_rides': pending_rides,
        'demand_zones': demand_zones,
        'supply_ratio': supply_ratio,
        'deficit_pct': deficit_pct,
        'network_status': 'Optimum Efficiency' if deficit_pct < 20 else 'High Demand',
    }
    return render(request, 'predictive_heatmaps.html', context)

