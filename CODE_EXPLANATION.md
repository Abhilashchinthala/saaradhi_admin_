# SaaradhiGo: Complete Code Explanation Guide

This document explains exactly what is happening in the code, breaking down each major file into its core components for a beginner.

---
    
## 1. Database Layer (`dashboard/models.py`)
This file defines the **Models**, which are blueprints for the data you store. Every class here becomes a table in your database.

### `class Driver(models.Model):`
- **`name = models.CharField(...)`**: Stores the driver's name as text.
- **`status`**: A text field with choices (`ACTIVE`, `ON_TRIP`, `OFFLINE`). This tracks if a driver can take a ride right now.
- **`rating = models.FloatField()`**: A decimal number (e.g., 4.8) for driver ratings.
- **`total_revenue = models.DecimalField()`**: Tracks exactly how much the driver has earned.

### `class Vehicle(models.Model):`
- **`make_model`**: The car type (e.g., "Toyota Camry").
- **`license_plate`**: The unique number plate of the vehicle.
- **`driver = models.ForeignKey(Driver, ...)`**: This **connects** a vehicle to a driver. It's like saying "This car belongs to this person."

### `class Ride(models.Model):`
- **`rider_name`**: Name of the person who booked the ride.
- **`driver`**: Connects to the `Driver` who took them.
- **`status`**: Tracks if the ride is `COMPLETED`, `IN_PROGRESS`, or `CANCELLED`.
- **`fare`**: The total cost of the trip.

---

## 2. Business Logic Layer (`dashboard/views.py`)
This is where the "brains" of the app live. These functions handle what happens when a user clicks on something.

### `fleet_monitor_view(request):`
- **Goal**: Show the "God View" of all active drivers.
- **`drivers = Driver.objects.all()`**: This line asks the database for every single driver.
- **`active_count = drivers.filter(status='ACTIVE').count()`**: This filters the list to only count people who are currently online.
- **`return render(request, 'fleet_monitor.html', context)`**: This takes all the data and sends it to the HTML file so the user can see it.

### `executive_revenue_view(request):`
- **Goal**: Show the company's financial stats.
- **`completed_rides = Ride.objects.filter(status='COMPLETED')`**: Only looks at rides that actually finished successfully.
- **`gbv = completed_rides.aggregate(total=Sum('fare'))['total']`**: Sums up all the fares from those rides to get the total money made (Gross Booking Value).
- **`platform_revenue = gbv * Decimal('0.20')`**: Calculates 20% commission for the platform.

### `fare_surge_view(request):`
- **Goal**: Let admins change the global pricing.
- **`if request.method == 'POST':`**: Checks if the user clicked the "Save" button to submit data.
- **`config.base_fare = Decimal(request.POST.get('base_fare'))`**: Grabs the new price you typed into the website and saves it to the database.

---

## 3. Real-Time Layer (`dashboard/consumers.py`)
This uses **WebSockets** (Django Channels) to push data to the screen instantly, without ever refreshing the page.

### `class DriverLocationConsumer(AsyncWebsocketConsumer):`
- **`connect()`**: When a driver's app starts, it connects to a "hub" called the `drivers` group.
- **`receive()`**: Triggered when the driver sends their new Latitude and Longitude (location).
- **`group_send()`**: Immediately broadcasts that location to everyone else in the group (like the Admin Dashboard "God View").
- **`driver_location_update()`**: This is the final step that actually pushes the new map marker position to the admin's browser.

---

## 4. Website Addresses (`dashboard/urls.py`)
This file maps search bar addresses (URLs) to the functions in `views.py`.

- **`path('', views.fleet_monitor_view, ...)`**: If you just go to the homepage, it shows the Fleet Monitor.
- **`path('fare-surge/', ...)`**: If you add `/fare-surge/` to the URL, it opens the pricing manager.

---

## 5. Main Configuration (`saradhigo_admin/settings.py`)
The master settings for the whole project.

- **`INSTALLED_APPS`**: Tells Django which modules to load (like our `dashboard` and the `channels` real-time module).
- **`DATABASES`**: Tells Django to store everything in the `db.sqlite3` file on your computer.
- **`CHANNEL_LAYERS`**: Configures the real-time "engine" that allows different parts of the app to talk to each other without delay.

---

## 6. How it All Works Together
1. **User** types a URL (e.g., `/executive-revenue/`).
2. **URLs** routes that request to a **View**.
3. **View** asks the **Models** for data (e.g., "Give me all the ride fares").
4. **View** does some math (e.g., "Summarize the fares").
5. **View** sends the result to the **Template** (HTML).
6. **Consumer** works in the background to keep the map and stats updating live without refreshing.
