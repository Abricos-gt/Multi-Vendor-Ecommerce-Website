import os

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')

 
# Admin Configuration
ADMIN_EMAIL = 'abrishg.tesfamichael@gmail.com'
ADMIN_PASSWORD = '09900990'

# CORS Configuration
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

# App Configuration
DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
HOST = os.getenv('FLASK_HOST', '127.0.0.1')
PORT = int(os.getenv('FLASK_PORT', '5000'))
