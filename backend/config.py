import os

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg2://postgres:123456789@localhost:5432/x-vendor')

# Email Configuration
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USER = os.getenv('EMAIL_USER', 'your-email@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your-app-password')

# Admin Configuration
ADMIN_EMAIL = 'abrishg.tesfamichael@gmail.com'
ADMIN_PASSWORD = '09900990'

# CORS Configuration
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

# App Configuration
DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
HOST = os.getenv('FLASK_HOST', '127.0.0.1')
PORT = int(os.getenv('FLASK_PORT', '8088'))
