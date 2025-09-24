import os

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')

 
# Admin Configuration (read from environment for security)
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', '')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '')

# CORS Configuration (support comma-separated list)
_cors_origins = os.getenv('CORS_ORIGINS', '*').strip()
if _cors_origins == '*' or not _cors_origins:
    CORS_ORIGINS = '*'
else:
    CORS_ORIGINS = [o.strip() for o in _cors_origins.split(',') if o.strip()]

# App Configuration
DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
HOST = os.getenv('FLASK_HOST', '127.0.0.1')
PORT = int(os.getenv('FLASK_PORT', '5000'))
