# Implementation Plan: Dynamic Admin Dashboard

## Goal Description
The objective is to transform the remaining static pages (`executive_revenue.html`, `fare_surge.html`, `predictive_heatmaps.html`, and `login.html`) in the Saradhigo Django dashboard into dynamic pages, driven by backend data. We will split the work into three logical phases and implement Phase 1. 

## Proposed Changes

We will introduce a phased approach to building the dynamic dashboard components.

### Phase 2: Real-time WebSocket Integration (Current Focus)
In this phase, we will integrate Django Channels to support real-time updates for driver locations, ride requests, and trip statuses.

#### Infrastructure Setup
- **[NEW]** Install dependencies: `daphne`, `channels`, `channels-redis`.
- **[MODIFY] [settings.py](file:///c:/Users/chint/OneDrive/Desktop/saradhigo/saradhigo_admin/settings.py)**:
    - Add `daphne` to `INSTALLED_APPS` (at the top).
    - Add `channels` to `INSTALLED_APPS`.
    - Set `ASGI_APPLICATION = 'saradhigo_admin.asgi.application'`.
    - Configure `CHANNEL_LAYERS` (using `InMemoryChannelLayer` for local dev or `RedisChannelLayer` if Redis is available).
- **[MODIFY] [asgi.py](file:///c:/Users/chint/OneDrive/Desktop/saradhigo/saradhigo_admin/asgi.py)**:
    - Wrap the application with `ProtocolTypeRouter` and `URLRouter`.
    - Add `AuthMiddlewareStack`.

#### Backend Implementation
- **[NEW] [consumers.py](file:///c:/Users/chint/OneDrive/Desktop/saradhigo/dashboard/consumers.py)**:
    - `DriverLocationConsumer`: Handle `ws/driver/location/`. Broadcast location to groups.
    - `RideRequestConsumer`: Handle `ws/ride/request/`. Broadcast new ride requests to nearby drivers.
    - `TripStatusConsumer`: Handle `ws/ride/trip/<trip_id>/`. Manage trip lifecycle updates.
- **[NEW] [routing.py](file:///c:/Users/chint/OneDrive/Desktop/saradhigo/dashboard/routing.py)**:
    - Define `websocket_urlpatterns`.

#### Frontend Integration
- **[MODIFY] [fleet_monitor.html](file:///c:/Users/chint/OneDrive/Desktop/saradhigo/templates/fleet_monitor.html)**:
    - Connect to `ws/driver/location/`.
    - Update car markers on the map based on incoming telemetry.
- **[MODIFY] [predictive_heatmaps.html](file:///c:/Users/chint/OneDrive/Desktop/saradhigo/templates/predictive_heatmaps.html)**:
    - Integrate live demand pulses if applicable.

### Phase 3: Advanced Analytics and Actions (Future)
- Implement date-range filtering for Executive Revenue.
- Wire up the "Update Global Config" and "Dispatch Supply Alerts" buttons to actual backend `POST` update endpoints.
- Secure all API endpoints with Token/Session Authentication.

## Verification Plan

### Automated Tests
- Run Django unit tests (if any) to ensure the newly added context processors and models do not break the views.
- Command: `python manage.py test dashboard`

### Manual Verification
1. Open the Django admin or use a mock data script (`load_mock_data.py`) to generate entries for new models (Surge Zones, Configurations).
2. Start the Django development server: `python manage.py runserver`
3. Navigate to `/executive-revenue/` and verify that the metrics reflect the mock rides.
4. Navigate to `/fare-surge/` and verify the global configs and table data match the DB.
5. Navigate to `/predictive-heatmaps/` and verify the network balance metrics accurately reflect the current DB state.
