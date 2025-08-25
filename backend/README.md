Backend
=====

This directory is reserved for backend services.

Suggested structure:
- src/ — server source code
- package.json — backend dependencies and scripts
- .env — environment variables (do not commit)

Quick start (Flask):
1) cd backend
2) python -m venv .venv && .venv\Scripts\activate (Windows PowerShell)
3) pip install -r requirements.txt
4) Copy .env.example to .env and adjust if needed
5) python app.py

Endpoints:
- GET /health
- POST /auth/register {name,email}
- POST /auth/admin
- POST /vendors/apply {user_id,license_url,id_card_url}
- GET /vendors/applications
- POST /vendors/applications/<id>/status {status: pending|approved|rejected}
- POST /products {vendor_user_id,name,description,price,image_url}
- GET /products
- POST /orders {user_id, items:[{product_id,quantity}]}
- GET /orders


