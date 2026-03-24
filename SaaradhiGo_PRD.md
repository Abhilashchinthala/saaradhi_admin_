# Product Requirements Document: SaaradhiGo

## 1. Executive Summary

**SaaradhiGo** (formerly VahanGo) is a modern ride-hailing platform engineered to deliver safe, reliable, and transparent urban mobility. Designed from the ground up with a driver-first philosophy, SaaradhiGo utilizes a high-performance technology stack (Flutter for cross-platform mobile, Django for scalable backend services) to ensure real-time responsiveness and an unparalleled user experience.

*   **Problem Statement:** The current urban mobility market is plagued by unpredictable surge pricing algorithms, deep driver dissatisfaction leading to high cancellation rates, and a lack of inclusive features catering to diverse demographics (e.g., senior citizens, carpooling enthusiasts).
*   **Value Proposition:**
    *   **For Riders:** Fair, transparent pricing algorithms, specialized safety features, and a seamless, premium user interface.
    *   **For Drivers:** Transparent earnings with higher take-home percentages, instant wallet payouts, and comprehensive destination visibility prior to acceptance.
*   **Business Objectives:** Achieve 10,000 active monthly riders and 2,000 active drivers within the first 6 months post-MVP launch in the target operational city.

---

## 2. Product Vision & Positioning

*   **Vision:** To become the central, indispensable app for all urban transportation needs, harmonizing rider convenience with driver empowerment and well-being.
*   **Market Positioning:** A premium, "Driver-First" platform that intrinsically leads to superior Rider experiences through enhanced supply reliability and motivated partners.
*   **Key Success Metrics (KPIs):**
    *   Fulfillment Rate: > 90% (Rides requested vs. Rides successfully completed).
    *   Average ETA (Estimated Time of Arrival): < 5 Minutes.
    *   App Stability: < 0.1% crash rate per session.

---

## 3. Project Scope

| Category | In-Scope (MVP Phase) | Out-of-Scope (Future Iterations) |
| :--- | :--- | :--- |
| **Service Offerings** | Standard Auto/Car Ride, Bike Taxi | Inter-city Rentals, Parcel Delivery, Scheduled Rides, Multi-stop routing |
| **Geographic Focus** | Single City Launch (e.g., Hyderabad) | Multi-city expansion, International support |
| **Payment Gateways** | UPI, Credit/Debit Cards (via Razorpay), Cash | Cryptocurrency integration |
| **Core Features** | Real-time tracking, Dynamic Fare Engine, Admin KPI Dashboard, Rating System | Advanced ML-driven Demand Prediction |
| **Pricing Model** | Automated Dynamic Pricing (Supply/Demand based) | Manual Surge Overrides |

---

## 4. User Personas

### 4.1 The Rider
*   **Profile:** 20-35 year-old urban professional or student.
*   **Needs:** Reliable pickup ETAs, transparent upfront pricing, robust safety features (SOS), and a lag-free booking experience.
*   **Pain Points:** Drivers cancelling post-acceptance, lagging map interfaces, and hidden fees.

### 4.2 The Driver
*   **Profile:** 30-45 year-old gig economy worker, vehicle owner-operator.
*   **Needs:** Consistent stream of requests, clear visibility into earnings per trip, and rapid payout mechanisms.
*   **Pain Points:** High platform commission fees, obscured pickup/drop locations prior to acceptance.

### 4.3 The Senior Citizen (Inclusive Design)
*   **Profile:** 60+ year-old individual requiring structured mobility support.
*   **Needs:** High-contrast, user-friendly UI (larger typography, intuitive icons), local language support, and priority safety monitoring.
*   **Pain Points:** Complex booking flows and difficulty communicating with drivers.

### 4.4 The Administrator
*   **Profile:** Central Operations Manager at SaaradhiGo.
*   **Needs:** Real-time visibility into active network ("God View"), dispute resolution tools, and financial/performance analytics.

---

## 5. Core User Journeys

### 5.1 Rider Journey
1.  **Onboarding:** Secure login via SMS OTP -> Profile creation -> Location permission granting.
2.  **Booking Initiation:** Input Destination -> View Fare Estimates (Standard/Bike) -> Select Vehicle Class -> Confirm Request.
3.  **Active Ride:** Real-time pairing -> Driver approach tracking -> OTP verification at pickup -> En-route live tracking.
4.  **Completion:** Automated payment processing or Cash handover -> Rate and Review Driver experience.

### 5.2 Driver Journey
1.  **Registration & KYC:** Document upload (DL, RC, Insurance) -> Admin verification -> Profile activation.
2.  **Shift Management:** Toggle "Go Online" status -> Continuous GPS polling active.
3.  **Request Fulfillment:** Receive Dispatch Alert (showing pickup, drop, and expected earnings) -> Accept -> Navigate to Pickup -> Start Trip -> Navigate to Destination -> Complete Trip.
4.  **Financials:** Review trip earnings ledger -> Request withdrawal to linked account.

---

## 6. Functional Requirements 

### 6.1 Rider Application (Mobile)
*   **FR-R01 Authentication:** Seamless phone number login supported by SMS OTP. 
*   **FR-R02 Interactive Map:** Live map displaying current location and "ghost cars" representing available nearby drivers.
*   **FR-R03 Fare Estimation Engine:** Display precise fare boundaries based on real-time distance and estimated duration before confirmation.
*   **FR-R04 Matchmaking Pulse:** Visual feedback indicating active search for nearby drivers (Timeout: 60s).
*   **FR-R05 Safety Toolkit:** One-tap SOS emergency button and live trip sharing capabilities.
*   **FR-R06 Ride History:** Comprehensive history module detailing past trips, paginated lists, and downloadable invoices.
*   **FR-R07 Location Management:** Ability to save and quickly select frequent locations (Home, Work).

### 6.2 Driver Application (Mobile)
*   **FR-D01 Document Management UI:** Interface to photograph and upload compliance documents with clear status indicators (Pending/Approved).
*   **FR-D02 Enhanced Request Card:** High-contrast, rapidly legible popup indicating Pickup Distance, Rider Rating, and Estimated Net Earnings.
*   **FR-D03 In-App Navigation:** Integrated turn-by-turn routing utilizing mapping SDKs.
*   **FR-D04 Earnings Wallet:** Real-time balance dashboard with detailed commission breakdowns and direct withdrawal functionality.
*   **FR-D05 Status Toggling:** Hard toggle for Online/Offline availability regulating dispatch engine eligibility.

### 6.3 Admin Dashboard (Web)
*   **FR-A01 God View Map:** Real-time geospatial tracking of all active online drivers and localized trip statuses.
*   **FR-A02 User Management:** Full CRUD operations for Rider/Driver profiles and manual KYC verification workflows.
*   **FR-A03 Financial Analytics:** Reporting suite detailing daily/weekly gross booking value (GBV), platform revenue, and driver payouts.
*   **FR-A04 Dispute Resolution:** Ticketing system interface for handling fare disputes and reported safety incidents.

### 6.4 Backend Services & Engines
*   **FR-B01 Geo-Spatial Matchmaking:** High-performance spatial querying (e.g., PostGIS/Redis Geo) to locate optimal drivers within an X-km radius based on proximity and rating.
*   **FR-B02 Dynamic Pricing Engine:** Real-time fare computation formula factoring Base Fare, Per-Km Rate, Per-Minute Rate, and local Surge Multipliers.
*   **FR-B03 Real-Time Synchronization:** WebSockets infrastructure to maintain instantaneous state synchronization between Rider, Driver, and Server throughout the trip lifecycle.

---

## 7. Non-Functional Requirements (NFRs)

*   **NFR-01 Performance:** Critical API endpoints (Booking, Matchmaking) must resolve in < 200ms.
*   **NFR-02 Scalability:** WebSockets architecture must seamlessly sustain a minimum of 10,000 concurrent active connections per regional cluster.
*   **NFR-03 Reliability:** Platform must maintain a 99.9% Uptime SLA.
*   **NFR-04 Security:** All Personally Identifiable Information (PII) must be encrypted at rest. All real-time communication mandated via WSS/HTTPS protocols.
*   **NFR-05 Localization:** Complete application UI support for English and key regional languages (e.g., Telugu, Hindi).

---

## 8. Technical Architecture Overview

*   **Client Applications:** Flutter (Dart) implementing Clean Architecture / MVVM patterns.
*   **API Gateway:** Nginx for secure ingress, reverse proxying, and load balancing.
*   **Core Backend Services:** Python / Django REST Framework.
*   **Real-time Infrastructure:** Django Channels operating with a Redis ASGI backend.
*   **Primary Datastore:** PostgreSQL with PostGIS extensions for complex spatial relations.
*   **Asynchronous Processing:** Celery task queues utilizing Redis as the message broker for deferred operations (OTP dispatches, final settlement processing).
