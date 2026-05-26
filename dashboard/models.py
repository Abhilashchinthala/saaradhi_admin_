from django.db import models


class Driver(models.Model):
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[('ACTIVE', 'Active'), ('ON_TRIP', 'On Trip'), ('OFFLINE', 'Offline')])
    rating = models.FloatField()
    total_trips = models.IntegerField()
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    onboarding_status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING_KYC', 'Pending KYC'),
            ('KYC_SUBMITTED', 'KYC Submitted'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected')
        ],
        default='APPROVED'
    )

    def __str__(self):
        return self.name

    @property
    def loyalty_tier(self):
        if self.total_trips >= 1000 and self.rating >= 4.9:
            return 'PLATINUM'
        elif self.total_trips >= 500 and self.rating >= 4.7:
            return 'GOLD'
        elif self.total_trips >= 200 and self.rating >= 4.5:
            return 'SILVER'
        else:
            return 'BRONZE'


class Vehicle(models.Model):
    make_model = models.CharField(max_length=100)
    license_plate = models.CharField(max_length=20)
    class_type = models.CharField(max_length=50)  # e.g., SUV Elite, Business Sedan
    status = models.CharField(max_length=20, choices=[('AVAILABLE', 'Available'), ('IN_USE', 'In Use'), ('MAINTENANCE', 'Maintenance')])
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicles')

    def __str__(self):
        return self.make_model


class Ride(models.Model):
    rider_name = models.CharField(max_length=100)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='rides')
    status = models.CharField(max_length=20, choices=[('COMPLETED', 'Completed'), ('IN_PROGRESS', 'In Progress'), ('CANCELLED', 'Cancelled')])
    fare = models.DecimalField(max_digits=8, decimal_places=2)
    vehicle_class = models.CharField(
        max_length=50,
        choices=[('SUV Elite', 'SUV Elite'), ('Business Sedan', 'Business Sedan'), ('Luxury Auto', 'Luxury Auto')],
        default='Business Sedan'
    )
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


class GlobalConfiguration(models.Model):
    """Stores the global fare configuration for the platform."""
    base_fare = models.DecimalField(max_digits=8, decimal_places=2, default=5.50)
    surge_multiplier = models.DecimalField(max_digits=4, decimal_places=1, default=1.5)
    surge_cap = models.DecimalField(max_digits=4, decimal_places=1, default=4.0)
    per_km_rate = models.DecimalField(max_digits=6, decimal_places=2, default=12.00)
    per_min_rate = models.DecimalField(max_digits=6, decimal_places=2, default=1.50)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Global Configuration"

    def __str__(self):
        return f"Global Config (Base: ₹{self.base_fare}, Surge: {self.surge_multiplier}x)"


class SurgeZone(models.Model):
    """Represents a geographic area currently under dynamic surge pricing."""
    zone_name = models.CharField(max_length=100)
    multiplier = models.DecimalField(max_digits=4, decimal_places=1, default=1.0)
    requests_per_hour = models.IntegerField(default=0)
    active_drivers = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.zone_name} ({self.multiplier}x)"


class HeatmapDemand(models.Model):
    """Stores predicted demand zones for the Predictive Pulse heatmap."""
    zone_name = models.CharField(max_length=100)
    predicted_surge = models.DecimalField(max_digits=4, decimal_places=1, default=1.0)
    predicted_at_time = models.CharField(max_length=10, default="18:00")  # e.g., "18:00"
    reason = models.CharField(max_length=200, default="High volume exit predicted")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.zone_name} - {self.predicted_surge}x at {self.predicted_at_time}"


class DispatchActionLog(models.Model):
    zone_name = models.CharField(max_length=100)
    action_type = models.CharField(max_length=50, default="SUPPLY_ALERT")
    admin_user = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action_type} for {self.zone_name} at {self.created_at}"


class DriverDocument(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(
        max_length=20,
        choices=[
            ('DL', 'Driving License'),
            ('RC', 'Registration Certificate'),
            ('INSURANCE', 'Insurance'),
            ('AADHAAR', 'Aadhaar Card')
        ]
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected')
        ],
        default='PENDING'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.doc_type} for {self.driver.name} ({self.status})"


class AdminNotification(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=[('ALERT', 'Alert'), ('INFO', 'Info'), ('WARNING', 'Warning')],
        default='INFO'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.created_at}"

