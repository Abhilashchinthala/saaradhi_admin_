# SaaradhiGo: Complete Line-by-Line Technical Breakdown

This document provides a granular explanation of every major line of code in the project. It is written to help a beginner understand *how* and *why* things are written this way.

---

## 1. The Data Models (`dashboard/models.py`)

This file tells the database how to store our information.

### `class Driver(models.Model):`
- `name = models.CharField(max_length=100)`: Stores the driver's name as text.
- `status = models.CharField(...)`: Uses a "choice" list (`ACTIVE`, `ON_TRIP`, `OFFLINE`) to restrict what can be typed here.
- `rating = models.FloatField()`: Stores a decimal number for star ratings.
- `total_revenue = models.DecimalField(max_digits=10, decimal_places=2)`: Stores money with exactly 2 decimal places (like ₹100.50).

### `class Vehicle(models.Model):`
- `driver = models.ForeignKey(Driver, ...)`: This is a **Relationship**. It creates a connection where one driver can have one vehicle assigned to them.

---

## 2. The Logic Layer (`dashboard/views.py`)

This file handles the "brain work" when you visit a page.

### `login_view(request):` (Line 12)
- `username = request.POST.get('username')`: Grabs what you typed in the login box.
- `user = authenticate(request, username=username, password=password)`: Checks if the username and password match any user in the system.
- `login(request, user)`: Starts a "Session" so the website remembers you are logged in.

### `executive_revenue_view(request):` (Line 68)
- `start_date_str = request.GET.get('start_date')`: Checks the URL for a date (e.g., `?start_date=2024-01-01`).
- `completed_rides = Ride.objects.filter(status='COMPLETED')`: Asks the database for a list of all finished rides.
- `gbv = completed_rides.aggregate(total=Sum('fare'))['total']`: This is a mathematical "Sum" operation. It adds up all the `fare` amounts in that list.
- `platform_revenue = gbv * Decimal('0.20')`: Multiplies the total by 0.20 to calculate the 20% tax/commission.

---

## 3. The Real-Time Layer (`dashboard/consumers.py`)

This file manages **WebSockets**, allowing the map to update instantly.

### `class DriverLocationConsumer(AsyncWebsocketConsumer):` (Line 5)
- `async def connect(self):`: This runs the moment a driver connects to the server.
- `self.group_name = 'drivers'`: This assigns the driver to a specific "chat room" or channel called `drivers`.
- `await self.channel_layer.group_add(...)`: Actually puts the driver into that room.
- `async def receive(self, text_data):`: This runs whenever the driver sends their GPS location to the server.
- `await self.channel_layer.group_send(...)`: This "broadcasts" that location to everyone else (like the Admin Dashboard).

---

## 4. The Interactive Interface (`templates/fleet_monitor.html`)

This HTML file contains the "God View" map and some JavaScript.

### The JavaScript Section (Line 96)
- `const socket = new WebSocket(...)`: This line connects the browser to the real-time server we discussed above.
- `socket.onmessage = function(e) { ... }`: This "listener" waits for the server to send a driver's new location.
- `updateDriverMarker(data)`: This is a custom function that moves the car icon on the map.
- `const marker = document.createElement('div')`: This creates a new car icon on the fly if a new driver joins.
- `marker.style.top = top + '%'`: This actually moves the icon's position on your screen.

---

## 5. Main Routing (`dashboard/urls.py`)

This file maps the address you type in the browser to the logic in `views.py`.

- `path('', views.fleet_monitor_view, name='fleet_monitor')`: This says "If the address is empty (the homepage), run the `fleet_monitor_view` function."
- `path('login/', views.login_view, name='login')`: Maps the `/login/` address to the login page.

---

## 6. Project Setup (`saradhigo_admin/settings.py`)

The "Settings" for the entire application.

- `DEBUG = True`: This tells Django to show error messages if something goes wrong (used only during development).
- `ALLOWED_HOSTS = []`: A security list of which websites are allowed to host this code (empty means 'localhost').
- `DATABASES = { ... }`: Tells the app to use the `db.sqlite3` file to save your drivers and rides.
- `STATIC_URL = 'static/'`: Tells Django where to find your images, CSS, and styling files.

---

## 7. Mock Data Loader (`load_mock_data.py`)

This is a script you run once to add sample data.

- `django.setup()`: This "boots up" Django so we can talk to the database from a simple script.
- `Driver.objects.all().delete()`: This clears out any existing data so we start fresh.
- `Driver.objects.create(...)`: This line creates a new entry in your database for a driver like "Vikram Rathore."
