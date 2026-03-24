from django.contrib import admin
from .models import Driver, Vehicle, Ride, SupportTicket, GlobalConfiguration, SurgeZone, HeatmapDemand

admin.site.register(Driver)
admin.site.register(Vehicle)
admin.site.register(Ride)
admin.site.register(SupportTicket)
admin.site.register(GlobalConfiguration)
admin.site.register(SurgeZone)
admin.site.register(HeatmapDemand)
