# SaaradhiGo Admin Dashboard: Complete Technical Guide

This document provides a comprehensive overview of the **SaaradhiGo Admin Dashboard**, a central control system for a modern ride-hailing platform. This guide is designed for beginners to understand the architecture, code, and execution process.

---

## 1. Project Overview
**SaaradhiGo** (formerly VahanGo) is a ride-hailing platform. The folder you are looking at is the **Admin Dashboard**, built using the **Django** web framework. It allows administrators to monitor drivers, manage fares, view revenue analytics, and handle customer support.

### Key Features:
- **God View (Fleet Monitor):** Real-time tracking of active drivers and vehicles.
- **Revenue Analytics:** Detailed breakdown of earnings and fleet utilization.
- **Fare & Surge Management:** Real-time control over pricing and surge multipliers.
- **Predictive Heatmaps:** Demand forecasting for different city zones.
- **KYC & Onboarding:** Managing driver registrations and documents.

---

## 2. Technology Stack
- **Language:** Python
- **Framework:** Django (Web logic and server)
- **Database:** SQLite (Local development database)
- **Real-time:** Django Channels (for live updates)
- **Frontend:** HTML5, Vanilla CSS, and JavaScript (integrated via Django Templates)
- **Data Tools:** Mock data scripts for simulation.

---

## 3. Directory Structure
Understanding where files live is the first step:

```text
saradhigo/
├── dashboard/              # Main application logic
│   ├── models.py           # Database structure (Tables)
│   ├── views.py            # Business logic (What happens when you click)
│   ├── urls.py             # Route mappings (URL to View)
│   └── ...
├── saradhigo_admin/        # Project settings
│   ├── settings.py         # Global configuration (DB, Apps, Security)
│   ├── urls.py             # Main routing entry point
│   ├── asgi.py             # Real-time server configuration
│   └── wsgi.py             # Web server entry point
├── templates/              # HTML files (The UI)
├── static/                 # CSS, Images, and JavaScript files
├── manage.py               # Django management script (The control tool)
├── load_mock_data.py       # Script to fill the app with demo data
└── db.sqlite3              # The actual database file
```

---

## 4. Understanding the Code (Deep Dive)

### A. The Data (models.py)
The database is defined in `dashboard/models.py`. Think of these as Excel tables:
- **Driver:** Stores name, rating, status (Active/Offline), and total earnings.
- **Vehicle:** Links a car (model, plate) to a specific driver.
- **Ride:** Records every trip (rider name, fare, status, vehicle type).
- **GlobalConfiguration:** Stores the "rules" of the platform, like the base fare (e.g., ₹50.00).
- **SurgeZone:** Defines areas where prices are currently higher due to demand.

### B. The Logic (views.py)
When a user visits a page, a "View" function in `dashboard/views.py` runs. 
- **`fleet_monitor_view`**: Queries the database for all drivers and counts how many are active.
- **`executive_revenue_view`**: Calculates the Gross Booking Value (GBV) by summing up all completed ride fares.
- **`fare_surge_view`**: Allows admins to update the `GlobalConfiguration` settings via a form.

### C. The Interface (Templates)
The UI is built using Django's template engine. 
- **`base.html`**: The skeleton containing the sidebar and navigation.
- **`fleet_monitor.html`**: Displays cards with driver counts and a table of fleet status.
- **`executive_revenue.html`**: Uses CSS and simple logic to show revenue charts and stats.

---

## 5. Process Flow
How does a request work?

1. **User Action:** You click on "Revenue Analytics" in the sidebar.
2. **Routing:** `urls.py` sees the request for `/executive-revenue/` and sends it to `views.executive_revenue_view`.
3. **Logic & Data:** The View function talks to the Database (`Ride` model), fetching all "Completed" rides. It calculates the total money made.
4. **Rendering:** The View sends this data to the `executive_revenue.html` template.
5. **Display:** Your browser shows the updated page with the correct revenue numbers.

---

## 6. Execution Guide (How to Run from Scratch)

Follow these steps to get the app running on your computer:

### Step 1: Set up the environment
Open your terminal in the project folder and create a virtual environment:
```powershell
python -m venv env
.\env\Scripts\activate
```

### Step 2: Install dependencies
Install the required Python packages (Django, Channels, etc.):
```powershell
pip install django channels daphne
```

### Step 3: Prepare the Database
Create the database tables based on the models:
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Step 4: Load Mock Data
The app will be empty initially. Run the mock script to see data:
```powershell
python load_mock_data.py
```

### Step 5: Start the Server
Run the development server:
```powershell
python manage.py runserver
```

### Step 6: Access the App
Open your browser and go to: `http://127.0.0.1:8000/`

---

## 7. Summary for Team Explanation
When explaining to your team, use these key points:
- **"It's a Django-based monitoring system for our fleet."**
- **"Data Integrity:** Everything is stored in structured models (Drivers, Rides, Zones)."
- **"Dynamic Control:** We can change the entire platform's pricing in seconds through the 'Fare & Surge' panel."
- **"Real-time Readiness:** The architecture uses ASGI and Channels, meaning we can push live updates to the dashboard without refreshing."

---

> [!TIP]
> **To Save as PDF:** 
> 1. Open this file in a Markdown viewer (like VS Code or GitHub).
> 2. Right-click and choose **Print**.
> 3. Select **Save as PDF** as your printer destination.
