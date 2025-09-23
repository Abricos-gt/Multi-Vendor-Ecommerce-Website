<div align="center">

# Marketplace App (Vue + Flask)

Operational marketplace with multi-vendor catalogs, Chapa payments, admin dashboards, analytics and real-time updates.

</div>

## Overview

Purpose: A multi‑vendor ecommerce platform where multiple vendors can register, list and sell their products, while customers browse, cart, and checkout. Admins manage vendors, catalog, orders, refunds, and monitor performance with built‑in analytics.

- Frontend: Vue 2/3 SPA (in `src/`), charting via `vue-chartjs`.
- Backend: Flask + SQLAlchemy (in `backend/`).
- Payments: Chapa checkout with webhook/callback verification.
- Dashboards: Admin analytics (orders summary, sales over time, top categories), vendor management, refunds.

## Features

- Multi-vendor cart → single or per‑vendor order creation
- Chapa payment initialization, callback verification, and optional return URL suppression
- Orders lifecycle: pending → paid/failed → completed/cancelled
- Admin dashboard: counters, charts, recent orders
- Vendor applications review and product management
- Refund requests and processing

## Quick Start

### 1) Prerequisites

- Node 18+
- Python 3.11+ (virtualenv recommended)

### 2) Frontend Setup

```bash
npm install
npm run serve
```

Frontend runs on `http://localhost:8085` by default (see `vue.config.js`).

### 3) Backend Setup

Create and activate a virtual environment or use the bundled `backend/venv`.

```bash
cd backend
pip install -r requirements.txt
```

Environment configuration (Windows PowerShell / .bat):

```bat
REM Edit and run at repo root
start_backend.bat
```

Important environment variables (see `backend/app.py`):

- `CHAPA_SECRET_KEY`: Your Chapa secret key (required for live checkout)
- `CHAPA_BASE_URL`: `https://api.chapa.co`
- `CHAPA_CALLBACK_URL`: e.g. `http://localhost:5000/payments/chapa/callback`
- `CHAPA_RETURN_URL`: e.g. `http://localhost:8085/#/order-confirmation` (optional)
- `CHAPA_DISABLE_RETURN`: set to `true` to keep users on Chapa receipt page (no redirect)
- `CHAPA_OFFLINE`: set to `true` to simulate payments during local development

Run backend:

```bash
python backend/app.py
```

Backend runs on `http://localhost:5000` by default.

## Payment Flow (Chapa)

1. Place Order (pending):
   - `POST /payments/checkout` creates order(s) and returns `checkout_url`.
2. Redirect to Chapa (optional):
   - Frontend navigates to `checkout_url` when Chapa is selected.
   - To stay on the receipt page, set `CHAPA_DISABLE_RETURN=true`.
3. Webhook/Callback Verification:
   - `POST /payments/chapa/callback` verifies `tx_ref` via Chapa `verify` API and updates order status.
   - Idempotent: safe on duplicate callbacks.
4. Order Confirmation Page:
   - `#/order-confirmation` shows verification result and audit trail.

## Analytics Endpoints

- `GET /api/analytics/orders_summary` → `{ total, pending, completed, cancelled, paid, failed }`
- `GET /api/analytics/sales_over_time?days=30&metric=amount|count` → `{ labels, values, metric }`
- `GET /api/analytics/top_categories` → array of `{ category, orders }`
- `GET /admin/orders?range=30d&limit=50` → recent orders list

## Admin Dashboard

- Counters: total, pending, completed (auto-refresh every 15s)
- Recent Orders table (auto-refresh every 15s)
- Charts (`src/components/DashboardChart.vue`):
  - Top Vendors (horizontal bar, top-5)
  - Vendor Applications (line + 3-period moving average)
  - Products over time, products by category, refunds by status

## Development Scripts

```bash
npm run serve       # start frontend dev server
npm run build       # production build
npm run lint        # lint and fix
```

## Project Structure

```
backend/               Flask app, models, payments, analytics
  app.py               Main Flask application
  requirements.txt     Python dependencies
  uploads/             Static uploads (carousel)
src/                   Vue SPA source
  views/               App views (Admin, Cart, OrderConfirmation, etc.)
  components/          Reusable components (DashboardChart, Navbar, etc.)
  http.js              Axios wrapper
  store.js             Simple client-side state
public/                Static assets
```

## Security Notes

- Never expose `CHAPA_SECRET_KEY` on the frontend. Use backend only.
- Validate webhook authenticity if Chapa provides signatures.
- Sanitize and validate user inputs on both client and server.

## Troubleshooting

- No redirect after checkout: verify backend is running and `POST /payments/checkout` returns `checkout_url`.
- Want to stay on Chapa receipt screen: set `CHAPA_DISABLE_RETURN=true` and restart backend.
- Order not updating after payment: ensure `CHAPA_CALLBACK_URL` is reachable and configured in Chapa; check backend logs for callback errors.

## License

MIT

## Author

Abrha Gebrehiwet Tesfamichael

