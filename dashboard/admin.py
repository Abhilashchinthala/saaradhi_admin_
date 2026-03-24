from django.contrib import admin
from .models import Driver, Vehicle, Ride, SupportTicket

admin.site.register(Driver)
admin.site.register(Vehicle)
admin.site.register(Ride)
admin.site.register(SupportTicket)
