from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum, Count, Q, Avg
from django.utils.dateparse import parse_date
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from decimal import Decimal
from .models import Driver, Vehicle, Ride, SupportTicket, GlobalConfiguration, SurgeZone, HeatmapDemand, DispatchActionLog, DriverDocument, AdminNotification
from .forms import GlobalConfigurationForm
from django.core.paginator import Paginator
from .rate_limit import rate_limit


def login_view(request):
    if request.user.is_authenticated:
        return redirect('fleet_monitor')
    error = None
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
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
    status_filter = request.GET.get('status', 'ALL')
    drivers = Driver.objects.all().order_by('-id')
    
    if status_filter == 'PENDING':
        drivers = drivers.filter(onboarding_status__in=['PENDING_KYC', 'KYC_SUBMITTED'])
    elif status_filter == 'APPROVED':
        drivers = drivers.filter(onboarding_status='APPROVED')
    elif status_filter == 'REJECTED':
        drivers = drivers.filter(onboarding_status='REJECTED')
        
    pending_reviews_count = Driver.objects.filter(onboarding_status__in=['PENDING_KYC', 'KYC_SUBMITTED']).count()
    approved_count = Driver.objects.filter(onboarding_status='APPROVED').count()
    
    # Pagination for the review queue
    paginator = Paginator(drivers, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Selection details
    selected_driver_id = request.GET.get('selected_driver')
    selected_driver = None
    if selected_driver_id:
        try:
            selected_driver = Driver.objects.get(pk=selected_driver_id)
        except Driver.DoesNotExist:
            pass
    if not selected_driver and page_obj.object_list:
        selected_driver = page_obj.object_list[0]
        
    documents = []
    if selected_driver:
        documents = DriverDocument.objects.filter(driver=selected_driver)
        
    context = {
        'page_obj': page_obj,
        'drivers': page_obj.object_list,
        'selected_driver': selected_driver,
        'documents': documents,
        'pending_reviews_count': pending_reviews_count,
        'approved_count': approved_count,
        'status_filter': status_filter,
    }
    return render(request, 'driver_onboarding.html', context)


@login_required(login_url='login')
def approve_driver_view(request, pk):
    if request.method == 'POST':
        try:
            driver = Driver.objects.get(pk=pk)
            driver.onboarding_status = 'APPROVED'
            driver.save()
            driver.documents.all().update(status='APPROVED')
            
            AdminNotification.objects.create(
                title="Driver Approved",
                message=f"Driver {driver.name} has been successfully approved.",
                notification_type="INFO"
            )
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok'})
            return redirect(reverse('driver_onboarding') + f'?selected_driver={pk}')
        except Driver.DoesNotExist:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Driver not found'}, status=404)
            return redirect('driver_onboarding')
    return redirect('driver_onboarding')


@login_required(login_url='login')
def reject_driver_view(request, pk):
    if request.method == 'POST':
        try:
            driver = Driver.objects.get(pk=pk)
            driver.onboarding_status = 'REJECTED'
            driver.save()
            driver.documents.all().update(status='REJECTED')
            
            AdminNotification.objects.create(
                title="Driver Rejected",
                message=f"Driver {driver.name} has been rejected.",
                notification_type="WARNING"
            )
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok'})
            return redirect(reverse('driver_onboarding') + f'?selected_driver={pk}')
        except Driver.DoesNotExist:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Driver not found'}, status=404)
            return redirect('driver_onboarding')
    return redirect('driver_onboarding')


@login_required(login_url='login')
def dispute_support_view(request):
    tickets = SupportTicket.objects.all().order_by('-created_at')
    open_count = tickets.filter(status='OPEN').count()
    urgent_count = tickets.filter(priority='URGENT').count()
    total_count = tickets.count()
    
    # Pagination
    paginator = Paginator(tickets, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Selected ticket details
    selected_ticket_id = request.GET.get('selected_ticket')
    selected_ticket = None
    if selected_ticket_id:
        try:
            selected_ticket = SupportTicket.objects.get(pk=selected_ticket_id)
        except SupportTicket.DoesNotExist:
            pass
    if not selected_ticket and page_obj.object_list:
        selected_ticket = page_obj.object_list[0]
        
    context = {
        'page_obj': page_obj,
        'tickets': page_obj.object_list,
        'selected_ticket': selected_ticket,
        'open_count': open_count,
        'urgent_count': urgent_count,
        'total_count': total_count,
    }
    return render(request, 'dispute_support.html', context)


@login_required(login_url='login')
def executive_revenue_view(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # Compute GBV from completed rides
    completed_rides = Ride.objects.filter(status='COMPLETED')
    
    if start_date_str:
        completed_rides = completed_rides.filter(date__date__gte=parse_date(start_date_str))
    if end_date_str:
        completed_rides = completed_rides.filter(date__date__lte=parse_date(end_date_str))

    gbv = completed_rides.aggregate(total=Sum('fare'))['total'] or Decimal('0')
    platform_revenue = gbv * Decimal('0.20')
    take_rate = 20.0

    # Revenue per vehicle class
    class_totals = completed_rides.values('vehicle_class').annotate(total=Sum('fare'))
    class_revenue = {item['vehicle_class']: item['total'] or Decimal('0') for item in class_totals}
    
    total_class_revenue = Decimal('0')
    classes = ['SUV Elite', 'Business Sedan', 'Luxury Auto']
    for cls in classes:
        total_class_revenue += class_revenue.get(cls, Decimal('0'))

    class_breakdown = []
    for cls in classes:
        rev = class_revenue.get(cls, Decimal('0'))
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
        'start_date': start_date_str,
        'end_date': end_date_str,
    }
    return render(request, 'executive_revenue.html', context)


@login_required(login_url='login')
def driver_loyalty_view(request):
    drivers = Driver.objects.all().order_by('-rating', '-total_trips')
    # Pagination
    paginator = Paginator(drivers, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    total_trips = Driver.objects.aggregate(total=Sum('total_trips'))['total'] or 0
    total_miles = total_trips * 12
    
    context = {
        'page_obj': page_obj,
        'drivers': page_obj.object_list,
        'total_miles': f"{total_miles:,}",
        'active_loyalty_drivers': Driver.objects.filter(onboarding_status='APPROVED').count(),
    }
    return render(request, 'driver_loyalty.html', context)


@login_required(login_url='login')
def fare_surge_view(request):
    config, _ = GlobalConfiguration.objects.get_or_create(pk=1)
    error = None
    form = GlobalConfigurationForm(instance=config)

    if request.method == 'POST':
        if 'update_global' in request.POST:
            form = GlobalConfigurationForm(request.POST, instance=config)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('fare_surge'))
            else:
                error = "Invalid settings configuration."

    surge_zones = SurgeZone.objects.filter(is_active=True).order_by('-multiplier')
    peak_zone = surge_zones.first()
    
    # Use database aggregation instead of calculating average in Python memory
    avg_mult_val = surge_zones.aggregate(avg=Avg('multiplier'))['avg'] or Decimal('1.0')
    avg_multiplier = round(avg_mult_val, 1)

    context = {
        'config': config,
        'surge_zones': surge_zones,
        'active_zones_count': surge_zones.count(),
        'peak_zone': peak_zone,
        'avg_multiplier': avg_multiplier,
        'form': form,
        'error': error,
    }
    return render(request, 'fare_surge.html', context)


@login_required(login_url='login')
def payment_dashboard_view(request):
    rides = Ride.objects.all().order_by('-date')
    total_payments = rides.filter(status='COMPLETED').aggregate(total=Sum('fare'))['total'] or Decimal('0')
    completed_count = rides.filter(status='COMPLETED').count()
    cancelled_count = rides.filter(status='CANCELLED').count()
    
    # Pagination
    paginator = Paginator(rides, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'rides': page_obj.object_list,
        'total_payments': total_payments,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
    }
    return render(request, 'payment_dashboard.html', context)


@login_required(login_url='login')
def predictive_heatmaps_view(request):
    all_drivers = Driver.objects.count()
    active_drivers = Driver.objects.filter(status__in=['ACTIVE', 'ON_TRIP']).count()
    pending_rides = Ride.objects.filter(status='IN_PROGRESS').count()

    # Supply/demand ratio
    demand_zones = HeatmapDemand.objects.filter(is_active=True).order_by('-predicted_surge')
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
        'dispatch_logs': DispatchActionLog.objects.all().order_by('-created_at')[:5],
    }
    return render(request, 'predictive_heatmaps.html', context)


@rate_limit(max_requests=20, window_seconds=60)
@login_required
def dispatch_alert_view(request):
    if request.method == 'POST':
        zone_id = request.POST.get('zone_id')
        try:
            zone = HeatmapDemand.objects.get(id=zone_id)
        except HeatmapDemand.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Zone not found'}, status=404)
            
        DispatchActionLog.objects.create(
            zone_name=zone.zone_name,
            admin_user=request.user.username,
            details=f"Manual dispatch alert triggered for {zone.zone_name}."
        )
        return JsonResponse({'status': 'ok', 'message': f'Alert dispatched for {zone.zone_name}'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@rate_limit(max_requests=60, window_seconds=60)
@login_required(login_url='login')
def search_view(request):
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        # Search drivers by name or ID
        drivers = Driver.objects.filter(Q(name__icontains=q) | Q(id__icontains=q))[:5]
        for d in drivers:
            results.append({
                'type': 'driver',
                'title': d.name,
                'subtitle': f"Driver ID: #{d.id} • Rating: {d.rating} • Status: {d.status}",
                'url': reverse('driver_onboarding') + f'?selected_driver={d.id}',
            })
        
        # Search rides by rider name
        rides = Ride.objects.filter(rider_name__icontains=q)[:5]
        for r in rides:
            results.append({
                'type': 'ride',
                'title': f"Ride for {r.rider_name}",
                'subtitle': f"Driver: {r.driver.name} • Fare: ₹{r.fare} • Status: {r.status}",
                'url': reverse('payment_dashboard') + f'?q={r.rider_name}',
            })
    return JsonResponse({'status': 'ok', 'results': results})


@rate_limit(max_requests=60, window_seconds=60)
@login_required(login_url='login')
def notifications_api_view(request):
    notifications = AdminNotification.objects.filter(is_read=False).order_by('-created_at')
    data = []
    for n in notifications:
        data.append({
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'notification_type': n.notification_type,
            'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return JsonResponse({'status': 'ok', 'notifications': data})


@rate_limit(max_requests=30, window_seconds=60)
@login_required(login_url='login')
def mark_notification_read_view(request, pk):
    if request.method == 'POST':
        try:
            n = AdminNotification.objects.get(pk=pk)
            n.is_read = True
            n.save()
            return JsonResponse({'status': 'ok'})
        except AdminNotification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@rate_limit(max_requests=15, window_seconds=60)
@login_required(login_url='login')
def update_global_config_view(request):
    """AJAX endpoint to update global fare configuration without page reload."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

    config, _ = GlobalConfiguration.objects.get_or_create(pk=1)
    form = GlobalConfigurationForm(request.POST, instance=config)
    if form.is_valid():
        form.save()
        return JsonResponse({
            'status': 'ok',
            'message': 'Global configuration updated successfully.',
            'config': {
                'base_fare': str(config.base_fare),
                'surge_multiplier': str(config.surge_multiplier),
                'surge_cap': str(config.surge_cap),
                'per_km_rate': str(config.per_km_rate),
                'per_min_rate': str(config.per_min_rate),
            }
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Validation failed.',
            'errors': form.errors,
        }, status=422)
