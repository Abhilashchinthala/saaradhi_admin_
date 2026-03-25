from django.urls import path
from . import views

urlpatterns = [
    path('', views.fleet_monitor_view, name='fleet_monitor'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('driver-onboarding/', views.driver_onboarding_view, name='driver_onboarding'),
    path('dispute-support/', views.dispute_support_view, name='dispute_support'),
    path('executive-revenue/', views.executive_revenue_view, name='executive_revenue'),
    path('driver-loyalty/', views.driver_loyalty_view, name='driver_loyalty'),
    path('fare-surge/', views.fare_surge_view, name='fare_surge'),
    path('payment-dashboard/', views.payment_dashboard_view, name='payment_dashboard'),
    path('predictive-heatmaps/', views.predictive_heatmaps_view, name='predictive_heatmaps'),
    path('dispatch-alert/', views.dispatch_alert_view, name='dispatch_alert'),
]
