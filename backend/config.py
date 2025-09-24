import os
from urllib.parse import quote_plus

# Database Configuration
# Prefer DATABASE_URL if provided; otherwise build from PG* vars to avoid URL encoding issues
_database_url_env = os.getenv('DATABASE_URL', '').strip()
if _database_url_env:
    DATABASE_URL = _database_url_env
else:
    _pg_host = os.getenv('PGHOST')
    _pg_port = os.getenv('PGPORT', '5432')
    _pg_user = os.getenv('PGUSER')
    _pg_password = os.getenv('PGPASSWORD')
    _pg_db = os.getenv('PGDATABASE')
    _pg_sslmode = os.getenv('PGSSLMODE', 'require')
    if all([_pg_host, _pg_user, _pg_password, _pg_db]):
        # Safely encode password for URL
        _pwd = quote_plus(_pg_password)
        DATABASE_URL = f"postgresql+psycopg2://{_pg_user}:{_pwd}@{_pg_host}:{_pg_port}/{_pg_db}?sslmode={_pg_sslmode}"
    else:
        DATABASE_URL = 'sqlite:///app.db'

 
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
