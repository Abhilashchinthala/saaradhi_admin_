from django.urls import path
from . import views

urlpatterns = [
    path('', views.fleet_monitor_view, name='fleet_monitor'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('driver-onboarding/', views.driver_onboarding_view, name='driver_onboarding'),
    path('driver-onboarding/<int:pk>/approve/', views.approve_driver_view, name='approve_driver'),
    path('driver-onboarding/<int:pk>/reject/', views.reject_driver_view, name='reject_driver'),
    path('dispute-support/', views.dispute_support_view, name='dispute_support'),
    path('executive-revenue/', views.executive_revenue_view, name='executive_revenue'),
    path('driver-loyalty/', views.driver_loyalty_view, name='driver_loyalty'),
    path('fare-surge/', views.fare_surge_view, name='fare_surge'),
    path('payment-dashboard/', views.payment_dashboard_view, name='payment_dashboard'),
    path('predictive-heatmaps/', views.predictive_heatmaps_view, name='predictive_heatmaps'),
    path('dispatch-alert/', views.dispatch_alert_view, name='dispatch_alert'),
    path('api/global-config/', views.update_global_config_view, name='api_global_config'),
    path('api/search/', views.search_view, name='api_search'),
    path('api/notifications/', views.notifications_api_view, name='api_notifications'),
    path('api/notifications/<int:pk>/read/', views.mark_notification_read_view, name='mark_notification_read'),
]
