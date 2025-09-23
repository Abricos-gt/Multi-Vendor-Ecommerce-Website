@echo off
REM Configure Chapa environment variables before starting the backend
REM Replace the placeholder values with your actual keys/URLs
set "CHAPA_SECRET_KEY=REPLACE_WITH_YOUR_SECRET_KEY"
set "CHAPA_PUBLIC_KEY=CHAPUBK_TEST-t6g0CREkXdEK5EFhOfHVSbowju4osAch"
set "CHAPA_BASE_URL=https://api.chapa.co"
set "CHAPA_RETURN_URL=http://localhost:8085/#/order-confirmation"
set "CHAPA_CALLBACK_URL=http://localhost:5000/payments/chapa/callback"
REM Set this to true to keep user on Chapa receipt page (no redirect back)
set "CHAPA_DISABLE_RETURN=false"

cd backend
python app.py
pause
