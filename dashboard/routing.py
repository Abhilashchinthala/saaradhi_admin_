from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/driver/location/$', consumers.DriverLocationConsumer.as_asgi()),
    re_path(r'ws/ride/request/$', consumers.RideRequestConsumer.as_asgi()),
    re_path(r'ws/ride/trip/(?P<trip_id>\w+)/$', consumers.TripStatusConsumer.as_asgi()),
    re_path(r'ws/admin/dashboard/$', consumers.AdminDashboardConsumer.as_asgi()),
]
