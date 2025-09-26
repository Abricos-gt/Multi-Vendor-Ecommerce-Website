import os
from urllib.parse import quote_plus

# Database Configuration
# Prefer DATABASE_URL if provided; otherwise build from PG* vars to avoid URL encoding issues
_database_url_env = os.getenv('DATABASE_URL', '').strip()
def _normalize_database_url(url: str) -> str:
    try:
        if not url:
            return url
        # Normalize scheme for SQLAlchemy
        if url.startswith('postgres://'):
            url = 'postgresql://' + url[len('postgres://'):]
        # Prefer explicit driver for Postgres when missing
        scheme = url.split('://', 1)[0]
        lower_scheme = scheme.lower()
        # If not a Postgres URL, ensure we do NOT carry an sslmode query param
        if not lower_scheme.startswith('postgresql') and 'sslmode=' in url.lower():
            base, _, query = url.partition('?')
            if query:
                # remove sslmode from query string
                parts = [p for p in query.split('&') if not p.lower().startswith('sslmode=')]
                url = base if not parts else base + '?' + '&'.join(parts)
        if url.startswith('postgresql://') and '+psycopg2' not in lower_scheme and '+psycopg' not in lower_scheme and '+pg8000' not in lower_scheme:
            url = 'postgresql+psycopg2://' + url[len('postgresql://'):]
        # Ensure TLS parameter, tailored per driver
        if lower_scheme.startswith('postgresql'):
            lower_url = url.lower()
            if '+pg8000' in lower_scheme:
                # pg8000 uses 'ssl' boolean param instead of sslmode
                if 'sslmode=' in lower_url and 'ssl=' not in lower_url:
                    # replace sslmode with ssl=true
                    url = url.replace('sslmode=require', 'ssl=true').replace('sslmode=prefer', 'ssl=true')
                if 'ssl=' not in url.lower():
                    sep = '&' if '?' in url else '?'
                    url = f"{url}{sep}ssl=true"
            else:
                # psycopg2/psycopg accept sslmode in DSN
                if 'sslmode=' not in lower_url:
                    sep = '&' if '?' in url else '?'
                    url = f"{url}{sep}sslmode=require"
        return url
    except Exception:
        return url

if _database_url_env:
    DATABASE_URL = _normalize_database_url(_database_url_env)
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
