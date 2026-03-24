# Implementation Plan: Dynamic Admin Dashboard

## Goal Description
The objective is to transform the remaining static pages (`executive_revenue.html`, `fare_surge.html`, `predictive_heatmaps.html`, and `login.html`) in the Saradhigo Django dashboard into dynamic pages, driven by backend data. We will split the work into three logical phases and implement Phase 1. 

## Proposed Changes

We will introduce a phased approach to building the dynamic dashboard components.

### Phase 1: Core Dynamic Data Integration (Current Focus)
In this phase, we will connect the currently static templates to the Django backend using mock data and backend calculations.

#### [MODIFY] `dashboard/models.py`
- Add `SurgeZone` model to store active surge areas, multipliers, and request counts.
- Add `GlobalConfiguration` model for base fare, surge multipliers, and caps.
- Add `HeatmapDemand` model to store zone-wise demand for the predictive pulse.

#### [MODIFY] `dashboard/views.py`
- `executive_revenue_view`: Compute total gross booking value (GBV), platform revenue (20% take rate), and split revenue by vehicle class using the existing `Ride` model.
- `fare_surge_view`: Fetch global configuration and active surge zones from the database.
- `predictive_heatmaps_view`: Pass data regarding active drivers, unmet requests, and predicted surge zones.
- `login_view`: Implement basic authentication or redirect logic.

#### [MODIFY] `templates/executive_revenue.html`
- Replace hardcoded revenue numbers (₹42.8M, etc.) with Django template tags `{{ total_revenue }}`, `{{ platform_revenue }}`, etc.

#### [MODIFY] `templates/fare_surge.html`
- Render the 'Active Surge Zones' table using a `{% for zone in surge_zones %}` loop.
- Populate the Global Configuration form with dynamic values.

#### [MODIFY] `templates/predictive_heatmaps.html`
- Replace hardcoded "Predicted Surge" and "Network Balance" numbers with backend variables.

### Phase 2: Real-time WebSocket Integration (Future)
- Integrate Django Channels.
- Set up WebSocket consumers as per `WEBSOCKET_API_DOCS.md` (e.g., `ws/driver/location/`).
- Update the Fleet Monitor and Predictive Heatmaps to reflect real-time driver coordinates and live demand pulses.

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
