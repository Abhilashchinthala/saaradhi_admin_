from django.db import models

class Driver(models.Model):
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[('ACTIVE', 'Active'), ('ON_TRIP', 'On Trip'), ('OFFLINE', 'Offline')])
    rating = models.FloatField()
    total_trips = models.IntegerField()
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Vehicle(models.Model):
    make_model = models.CharField(max_length=100)
    license_plate = models.CharField(max_length=20)
    class_type = models.CharField(max_length=50) # e.g., SUV Elite, Business Sedan
    status = models.CharField(max_length=20, choices=[('AVAILABLE', 'Available'), ('IN_USE', 'In Use'), ('MAINTENANCE', 'Maintenance')])
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicles')

    def __str__(self):
        return self.make_model

class Ride(models.Model):
    rider_name = models.CharField(max_length=100)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='rides')
    status = models.CharField(max_length=20, choices=[('COMPLETED', 'Completed'), ('IN_PROGRESS', 'In Progress'), ('CANCELLED', 'Cancelled')])
    fare = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ride for {self.rider_name} by {self.driver.name}"

class SupportTicket(models.Model):
    rider_name = models.CharField(max_length=100)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='tickets', null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('OPEN', 'Open'), ('CLOSED', 'Closed'), ('PENDING', 'Pending')])
    priority = models.CharField(max_length=20, choices=[('URGENT', 'Urgent'), ('HIGH', 'High'), ('MEDIUM', 'Medium'), ('LOW', 'Low')])
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket from {self.rider_name}"
