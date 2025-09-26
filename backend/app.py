import os
import hmac
import hashlib
import traceback
import secrets
import json
import requests
import uuid
from flask_mail import Mail, Message
from sqlalchemy import text
import threading
import requests as _requests
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, redirect, session, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask import make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import psycopg2
from config import DATABASE_URL, ADMIN_EMAIL, ADMIN_PASSWORD, CORS_ORIGINS, DEBUG, HOST, PORT
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from pathlib import Path

def _sanitize_db_url(url: str) -> str:
    try:
        if not url:
            return url
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        # Remove sslmode for non-Postgres
        if not scheme.startswith('postgresql') and 'sslmode=' in (parsed.query or '').lower():
            q = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True) if k.lower() != 'sslmode']
            return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(q), parsed.fragment))
        # For pg8000, translate sslmode to ssl=true
        if scheme.startswith('postgresql') and '+pg8000' in scheme and 'sslmode=' in (parsed.query or '').lower():
            q = [(('ssl' if k.lower() == 'sslmode' else k), ('true' if k.lower() == 'sslmode' else v)) for k, v in parse_qsl(parsed.query, keep_blank_values=True)]
            return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(q), parsed.fragment))
        return url
    except Exception:
        return url

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Final safety normalization at runtime
_DATABASE_URL_EFFECTIVE = _sanitize_db_url(DATABASE_URL)
try:
    # Redact password when logging
    _safe_for_log = _DATABASE_URL_EFFECTIVE
    if '://' in _safe_for_log and '@' in _safe_for_log:
        prefix, rest = _safe_for_log.split('://', 1)
        userinfo, hostpart = rest.split('@', 1) if '@' in rest else ('', rest)
        if ':' in userinfo:
            user, _pwd = userinfo.split(':', 1)
            userinfo = f"{user}:***"
        _safe_for_log = f"{prefix}://{userinfo}@{hostpart}"
    print(f"[INFO] Using DATABASE_URL: {_safe_for_log}")
except Exception:
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = _DATABASE_URL_EFFECTIVE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
_engine_options = {
    'pool_pre_ping': True,
    'pool_recycle': 280,
    'pool_size': int(os.getenv('SQL_POOL_SIZE', '5')),
    'max_overflow': int(os.getenv('SQL_MAX_OVERFLOW', '10')),
    'pool_timeout': int(os.getenv('SQL_POOL_TIMEOUT', '30'))
}

# Only pass sslmode for Postgres psycopg/psycopg2 drivers; pg8000 uses a different param
_db_url_lower = _DATABASE_URL_EFFECTIVE.lower()
if _db_url_lower.startswith('postgresql') and '+pg8000' not in _db_url_lower:
    _engine_options['connect_args'] = { 'sslmode': os.getenv('PGSSLMODE', 'require') }

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = _engine_options
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

# Chapa configuration
CHAPA_SECRET_KEY = os.getenv('CHAPA_SECRET_KEY', 'CHASECK_TEST-u8NBsVdJPjJxF78Fe9rkS52wHe5GGaG5')
CHAPA_BASE_URL = os.getenv('CHAPA_BASE_URL', 'https://api.chapa.co')
CHAPA_RETURN_URL = os.getenv('CHAPA_RETURN_URL', 'https://afrashop.netlify.app/#/order-confirmation')
CHAPA_CALLBACK_URL = os.getenv('CHAPA_CALLBACK_URL', 'https://multi-vendor-ecommerce-website.onrender.com/payments/chapa/callback')
CHAPA_OFFLINE = os.getenv('CHAPA_OFFLINE', 'false').lower() in ('1','true','yes','on')
CHAPA_WEBHOOK_SECRET = os.getenv('CHAPA_WEBHOOK_SECRET', '').strip()
CHAPA_DISABLE_RETURN = os.getenv('CHAPA_DISABLE_RETURN', 'false').lower() in ('1','true','yes','on')

# Log key presence at startup for easier diagnostics
try:
    if not CHAPA_SECRET_KEY:
        print('[WARN] CHAPA_SECRET_KEY not set in environment')
    else:
        print(f"[INFO] CHAPA_SECRET_KEY loaded ({len(CHAPA_SECRET_KEY)} chars)")
except Exception:
    pass

# File upload configuration
UPLOAD_FOLDER = 'uploads'
CAROUSEL_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'carousel')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Create upload directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CAROUSEL_UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CAROUSEL_UPLOAD_FOLDER'] = CAROUSEL_UPLOAD_FOLDER

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')

# Initialize extensions
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
mail = Mail(app)

# Configure CORS
CORS(app, origins=CORS_ORIGINS)

# ----------------------
# Health check
# ----------------------
@app.route('/healthz', methods=['GET'])
def healthz():
    try:
        # Quick DB check (optional): run lightweight SELECT 1 for SQL-based backends
        try:
            with db.engine.connect() as connection:
                connection.execute(text('SELECT 1'))
        except Exception:
            # If DB is not reachable, still return 200 to indicate app is up
            pass
        return jsonify({
            'status': 'ok',
            'version': os.getenv('APP_VERSION', 'v1'),
            'time': datetime.utcnow().isoformat() + 'Z'
        }), 200
    except Exception:
        return jsonify({'status': 'error'}), 500

# Commerce settings
COMMISSION_RATE = float(os.getenv('COMMISSION_RATE', '0.10'))

# ----------------------
# File Upload Helpers
# ----------------------
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    """Generate a unique filename to avoid conflicts"""
    name, ext = os.path.splitext(filename)
    unique_id = str(uuid.uuid4())[:8]
    return f"{name}_{unique_id}{ext}"

# ----------------------
# Chapa Helpers
# ----------------------
def _is_valid_email(value: str) -> bool:
    try:
        if not value or not isinstance(value, str):
            return False
        v = value.strip().lower()
        return '@' in v and '.' in v and ' ' not in v and len(v) <= 254
    except Exception:
        return False

def _chapa_headers():
    # Sanitize secret to ASCII-only for HTTP headers
    secret = (CHAPA_SECRET_KEY or '').strip()
    cleaned = ''.join(ch for ch in secret if ord(ch) < 128)
    if cleaned != secret:
        print('[WARN] CHAPA_SECRET_KEY contained non-ASCII characters; sanitized for header use.')
    return {
        'Authorization': f'Bearer {cleaned}',
        'Content-Type': 'application/json'
    }

def initiate_chapa_payment(amount: float, currency: str, customer: dict, tx_ref: str) -> dict:
    """Create a Chapa checkout session and return response JSON."""
    if CHAPA_OFFLINE:
        # Offline/dev mode: simulate a checkout by redirecting straight back with tx_ref
        try:
            return_url = CHAPA_RETURN_URL
            sep = '&' if '?' in return_url else '?'
            if 'tx_ref=' not in return_url:
                return_url = f"{return_url}{sep}tx_ref={tx_ref}"
        except Exception:
            return_url = CHAPA_RETURN_URL
        return {'status': 'success', 'data': {'checkout_url': return_url}}
    if not CHAPA_SECRET_KEY:
        return {'error': 'CHAPA_SECRET_KEY not configured'}
    email = (customer.get('email') or '').strip().lower()
    if not _is_valid_email(email):
        email = 'customer@example.com'
    first_name = (customer.get('first_name') or customer.get('name') or 'Customer').strip() or 'Customer'
    last_name = (customer.get('last_name') or '').strip()
    phone_number = (customer.get('phone') or '').strip()
    # Intentionally omit return_url so Chapa stays on receipt page

    payload = {
        'amount': f"{amount:.2f}",
        'currency': currency,
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'phone_number': phone_number,
        'tx_ref': tx_ref,
        'callback_url': CHAPA_CALLBACK_URL,
    }
    try:
        resp = requests.post(f"{CHAPA_BASE_URL}/v1/transaction/initialize", headers=_chapa_headers(), json=payload, timeout=20)
        try:
            data = resp.json()
        except Exception:
            data = {'status_code': resp.status_code, 'text': resp.text}
        # Print non-success for easier diagnostics
        if (isinstance(data, dict) and data.get('status') != 'success') or resp.status_code >= 400:
            print(f"[CHAPA INIT ERROR] status={resp.status_code} body={data}")
        return data
    except Exception as e:
        if CHAPA_OFFLINE:
            # Fallback to simulated success in offline mode
            return {'status': 'success', 'data': {'checkout_url': return_url}}
        return {'error': f'Failed to initiate payment: {e}'}

def verify_chapa_transaction(tx_ref: str) -> dict:
    """Verify a Chapa transaction by tx_ref."""
    if CHAPA_OFFLINE:
        return {'status': 'success', 'data': {'status': 'success', 'tx_ref': tx_ref, 'amount': None, 'currency': 'ETB'}}
    if not CHAPA_SECRET_KEY:
        return {'error': 'CHAPA_SECRET_KEY not configured'}
    try:
        resp = requests.get(f"{CHAPA_BASE_URL}/v1/transaction/verify/{tx_ref}", headers=_chapa_headers(), timeout=20)
        return resp.json()
    except Exception as e:
        return {'error': f'Failed to verify transaction: {e}'}

# ----------------------
# Admin Settings Helpers
# ----------------------
def _load_admin_settings() -> dict:
    try:
        instance_dir = Path(app.instance_path)
        instance_dir.mkdir(parents=True, exist_ok=True)
        settings_path = instance_dir / 'admin_settings.json'
        if settings_path.exists():
            with settings_path.open('r', encoding='utf-8') as f:
                return json.load(f) or {}
    except Exception:
        pass
    return {}

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')  # user, vendor, admin
    email_verified = db.Column(db.Boolean, default=False)
    account_status = db.Column(db.String(20), default='active')  # active, pending_verification, suspended
    verification_token = db.Column(db.String(100), nullable=True)
    verification_expires = db.Column(db.DateTime, nullable=True)
    notification_preferences = db.Column(db.Text, nullable=True)  # JSON string
    privacy_preferences = db.Column(db.Text, nullable=True)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    stock_quantity = db.Column(db.Integer, default=0)
    colors = db.Column(db.String(500), nullable=True)  # JSON string
    sizes = db.Column(db.String(500), nullable=True)   # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CarouselSlide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=False)
    cta_text = db.Column(db.String(100), nullable=True)
    cta_url = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, shipped, delivered, completed, cancelled
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed, refunded
    payment_method = db.Column(db.String(50), nullable=True)
    payment_reference = db.Column(db.String(100), nullable=True)
    parent_order_id = db.Column(db.Integer, nullable=True)
    shipping_address = db.Column(db.Text, nullable=True)
    receipt_url = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    color = db.Column(db.String(50), nullable=True)
    size = db.Column(db.String(50), nullable=True)

class VendorApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    license_url = db.Column(db.String(500), nullable=True)
    id_card_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    admin_notes = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship
    user = db.relationship('User', backref='vendor_application')

class Refund(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, processed, failed
    admin_notes = db.Column(db.Text, nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)
    payment_reference = db.Column(db.String(100), nullable=True)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ----------------------
# Commerce extensions: parent order, wallets, withdrawals
# ----------------------

class ParentOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    tx_ref = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending_payment, paid, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VendorWallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    balance = db.Column(db.Float, default=0.0)
    pending = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WalletLedger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)
    parent_order_id = db.Column(db.Integer, db.ForeignKey('parent_order.id'), nullable=True)
    type = db.Column(db.String(20), nullable=False)  # pending_credit, credit, debit, payout
    amount = db.Column(db.Float, nullable=False)
    commission_rate = db.Column(db.Float, nullable=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WithdrawalRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, paid, rejected
    method = db.Column(db.String(50), nullable=True)
    account_ref = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ----------------------
# Commission and wallet helpers
# ----------------------

def _ensure_wallet(vendor_id: int) -> VendorWallet:
    wallet = VendorWallet.query.filter_by(vendor_id=vendor_id).first()
    if not wallet:
        wallet = VendorWallet(vendor_id=vendor_id, balance=0.0, pending=0.0)
        db.session.add(wallet)
        db.session.flush()
    return wallet

def _apply_pending_commission(order: Order):
    """When an order is paid/confirmed, move pending credit into wallet.pending.
    We'll release to balance when order is completed (delivery confirmed or auto-complete).
    Commission is deducted at this stage and recorded in the ledger.
    """
    try:
        # Find vendor from first order item (orders are per vendor in split); fall back by majority
        items = OrderItem.query.filter_by(order_id=order.id).all()
        if not items:
            return
        first_product = Product.query.get(items[0].product_id)
        if not first_product:
            return
        vendor_id = first_product.vendor_id
        gross = sum(i.price * i.quantity for i in items)
        commission = round(gross * COMMISSION_RATE, 2)
        net = round(gross - commission, 2)
        wallet = _ensure_wallet(vendor_id)
        wallet.pending = (wallet.pending or 0.0) + net
        db.session.add(WalletLedger(
            vendor_id=vendor_id,
            order_id=order.id,
            type='pending_credit',
            amount=net,
            commission_rate=COMMISSION_RATE,
            description=f'Pending net after {int(COMMISSION_RATE*100)}% commission'
        ))
    except Exception:
        pass

# ----------------------
# Order creation helper (compatible with DBs missing parent_order_id)
# ----------------------

def _insert_order_compat(user_id: int, total_amount: float, status: str, payment_status: str, shipping_address_json: str, parent_order_id: int | None):
    """Insert order using ORM when possible; fallback to raw SQL excluding parent column if DB lacks it."""
    try:
        has_parent_col = True
        if db.engine.name == 'sqlite':
            has_parent_col = _sqlite_has_column('order', 'parent_order_id')
        if has_parent_col:
            order = Order(
                user_id=user_id,
                total_amount=total_amount,
                status=status,
                payment_status=payment_status,
                shipping_address=shipping_address_json,
                parent_order_id=parent_order_id
            )
            db.session.add(order)
            db.session.flush()
            return order
        # Fallback: raw insert without parent_order_id
        now = datetime.utcnow().isoformat(sep=' ')
        sql = (
            'INSERT INTO "order" (user_id, total_amount, status, payment_status, payment_method, payment_reference, shipping_address, created_at, updated_at) '
            'VALUES (:user_id, :total_amount, :status, :payment_status, NULL, NULL, :shipping_address, :created_at, :updated_at)'
        )
        params = {
            'user_id': user_id,
            'total_amount': total_amount,
            'status': status,
            'payment_status': payment_status,
            'shipping_address': shipping_address_json,
            'created_at': now,
            'updated_at': now,
        }
        res = db.session.execute(text(sql), params)
        db.session.flush()
        inserted_id = res.lastrowid
        class OrderLite:
            def __init__(self, inserted_id: int):
                self.id = inserted_id
                self._raw = True
        return OrderLite(inserted_id)
    except Exception:
        raise

def _release_commission_on_complete(order: Order):
    try:
        items = OrderItem.query.filter_by(order_id=order.id).all()
        if not items:
            return
        first_product = Product.query.get(items[0].product_id)
        if not first_product:
            return
        vendor_id = first_product.vendor_id
        gross = sum(i.price * i.quantity for i in items)
        commission = round(gross * COMMISSION_RATE, 2)
        net = round(gross - commission, 2)
        wallet = _ensure_wallet(vendor_id)
        # Move from pending to balance
        wallet.pending = max(0.0, (wallet.pending or 0.0) - net)
        wallet.balance = (wallet.balance or 0.0) + net
        db.session.add(WalletLedger(
            vendor_id=vendor_id,
            order_id=order.id,
            type='credit',
            amount=net,
            commission_rate=COMMISSION_RATE,
            description='Release to withdrawable balance on completion'
        ))
    except Exception:
        pass

# Email functions
def _send_mail_async(app: Flask, msg: Message):
    with app.app_context():
        try:
            mail.send(msg)
            print(f"Email sent successfully to {msg.recipients}")
        except Exception as e:
            print(f"Failed to send email: {e}")

def send_mail_background(msg: Message):
    thread = threading.Thread(target=_send_mail_async, args=(app, msg))
    thread.daemon = True
    thread.start()

# Routes
@app.get('/')
def root_index():
    return jsonify({'ok': True, 'service': 'backend'})

@app.get('/vendors/<int:vendor_id>/wallet')
def get_vendor_wallet(vendor_id: int):
    try:
        wallet = _ensure_wallet(vendor_id)
        return jsonify({ 'vendor_id': vendor_id, 'balance': wallet.balance or 0.0, 'pending': wallet.pending or 0.0 })
    except Exception as e:
        return jsonify({'error': f'Failed to load wallet: {e}'}), 500

@app.post('/admin/dev/create-tables')
def admin_create_tables():
    """Developer helper to (re)create missing tables in dev. Enabled only when DEBUG is true."""
    try:
        if not DEBUG:
            return jsonify({'error': 'Not allowed'}), 403
        db.create_all()
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': f'Failed to create tables: {e}'}), 500

# Alias with /api prefix for dev helpers (frontend proxy friendly)
@app.post('/api/admin/dev/create-tables')
def admin_create_tables_api_alias():
    return admin_create_tables()

def _sqlite_has_column(table_name: str, column_name: str) -> bool:
    try:
        res = db.session.execute(f'PRAGMA table_info("{table_name}")').fetchall()
        return any((row[1] == column_name) for row in res)
    except Exception:
        return False

@app.post('/admin/dev/migrate')
def admin_migrate():
    """Lightweight in-place migration for SQLite: adds missing columns and creates new tables.
    Only enabled in DEBUG to avoid unsafe prod migrations.
    """
    try:
        if not DEBUG:
            return jsonify({'error': 'Not allowed'}), 403
        # Create any missing tables first
        db.create_all()
        # Add missing columns on existing tables (SQLite only supports ADD COLUMN)
        engine_name = db.engine.name
        changes = []
        if engine_name == 'sqlite':
            if _sqlite_has_column('order', 'parent_order_id') is False:
                try:
                    db.session.execute(text('ALTER TABLE "order" ADD COLUMN parent_order_id INTEGER'))
                    changes.append('order.parent_order_id')
                except Exception as ex:
                    if 'duplicate column name' not in str(ex).lower():
                        raise
            if _sqlite_has_column('order', 'receipt_url') is False:
                try:
                    db.session.execute(text('ALTER TABLE "order" ADD COLUMN receipt_url VARCHAR(300)'))
                    changes.append('order.receipt_url')
                except Exception as ex:
                    if 'duplicate column name' not in str(ex).lower():
                        raise
            # Create helpful indexes to speed up queries
            try:
                db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_product_category ON product (category)'))
                changes.append('idx_product_category')
            except Exception:
                pass
            try:
                db.session.execute(text('CREATE INDEX IF NOT EXISTS idx_product_created_at ON product (created_at)'))
                changes.append('idx_product_created_at')
            except Exception:
                pass
        db.session.commit()
        return jsonify({'ok': True, 'changes': changes})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Migration failed: {e}'}), 500

@app.post('/api/admin/dev/migrate')
def admin_migrate_api_alias():
    return admin_migrate()

@app.get('/api/admin/dev/diagnostics')
def admin_diagnostics():
    """Dev helper: returns current DATABASE_URL, sqlite file path (if any), and table columns for a given table.
    Usage: GET /api/admin/dev/diagnostics?table=order
    """
    try:
        if not DEBUG:
            return jsonify({'error': 'Not allowed'}), 403
        table = (request.args.get('table') or 'order')
        engine_url = str(db.engine.url)
        db_path = None
        if db.engine.name == 'sqlite':
            # sqlite:///app.db → file is relative to CWD; make absolute
            try:
                db_path = db.engine.url.database
                if db_path:
                    db_path = os.path.abspath(db_path)
            except Exception:
                db_path = None
        cols = []
        try:
            res = db.session.execute(f'PRAGMA table_info("{table}")').fetchall()
            for row in res:
                cols.append({'cid': row[0], 'name': row[1], 'type': row[2]})
        except Exception as e:
            cols = [{'error': f'Failed to load columns: {e}'}]
        return jsonify({'engine': db.engine.name, 'engine_url': engine_url, 'db_path': db_path, 'table': table, 'columns': cols})
    except Exception as e:
        return jsonify({'error': f'Diagnostics failed: {e}'}), 500

@app.get('/vendors/<int:vendor_id>/wallet/ledger')
def get_vendor_ledger(vendor_id: int):
    try:
        entries = WalletLedger.query.filter_by(vendor_id=vendor_id).order_by(WalletLedger.created_at.desc()).limit(100).all()
        out = []
        for e in entries:
            out.append({
                'id': e.id,
                'type': e.type,
                'amount': e.amount,
                'order_id': e.order_id,
                'parent_order_id': e.parent_order_id,
                'description': e.description,
                'commission_rate': e.commission_rate,
                'created_at': e.created_at.isoformat() if e.created_at else None
            })
        return jsonify(out)
    except Exception as e:
        return jsonify({'error': f'Failed to load ledger: {e}'}), 500

@app.post('/vendors/wallet/withdrawals')
def request_withdrawal():
    """Vendor requests a withdrawal from their wallet balance."""
    try:
        data = request.get_json() or {}
        vendor_id = int(data.get('vendor_id') or 0)
        amount = float(data.get('amount') or 0)
        method = (data.get('method') or 'bank')
        account_ref = (data.get('account_ref') or '')
        if vendor_id <= 0 or amount <= 0:
            return jsonify({'error': 'vendor_id and positive amount required'}), 400
        wallet = _ensure_wallet(vendor_id)
        if amount > (wallet.balance or 0.0):
            return jsonify({'error': 'Insufficient balance'}), 400
        # Lock funds
        wallet.balance -= amount
        db.session.add(WalletLedger(
            vendor_id=vendor_id,
            type='debit',
            amount=amount,
            description='Withdrawal request hold'
        ))
        req = WithdrawalRequest(vendor_id=vendor_id, amount=amount, method=method, account_ref=account_ref, status='pending')
        db.session.add(req)
        db.session.commit()
        return jsonify({'id': req.id, 'status': req.status})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to request withdrawal: {e}'}), 500

@app.post('/admin/wallet/withdrawals/<int:req_id>/process')
def process_withdrawal(req_id):
    """Admin processes a withdrawal (marks paid or rejected)."""
    try:
        data = request.get_json() or {}
        action = (data.get('action') or 'paid').lower()  # 'paid' or 'rejected'
        req = WithdrawalRequest.query.get(req_id)
        if not req:
            return jsonify({'error': 'Withdrawal not found'}), 404
        wallet = _ensure_wallet(req.vendor_id)
        if action == 'paid':
            req.status = 'paid'
            db.session.add(WalletLedger(
                vendor_id=req.vendor_id,
                type='payout',
                amount=req.amount,
                description='Withdrawal payout processed'
            ))
        elif action == 'rejected':
            # Return funds to balance
            wallet.balance = (wallet.balance or 0.0) + req.amount
            req.status = 'rejected'
            db.session.add(WalletLedger(
                vendor_id=req.vendor_id,
                type='credit',
                amount=req.amount,
                description='Withdrawal rejected, funds returned'
            ))
        else:
            return jsonify({'error': 'Invalid action'}), 400
        req.updated_at = datetime.utcnow()
        wallet.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'id': req.id, 'status': req.status})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to process withdrawal: {e}'}), 500

@app.get('/api/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'API is running'})

@app.post('/auth/login')
def login():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'error': 'email and password required'}), 400

    user = User.query.filter_by(email=email).first()

    # Admin check
    if email == ADMIN_EMAIL.lower():
        if password != ADMIN_PASSWORD:
            return jsonify({'error': 'invalid credentials'}), 401
        if not user:
            user = User(
                first_name='Admin',
                last_name='User',
                name='Admin',
                email=ADMIN_EMAIL,
                role='admin',
                password_hash=generate_password_hash(ADMIN_PASSWORD)
            )
            db.session.add(user)
            db.session.commit()
        else:
            user.role = 'admin'
            user.password_hash = generate_password_hash(ADMIN_PASSWORD)
            db.session.commit()

        return jsonify({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': user.role
        })

    # Normal user
    if not user or not user.password_hash or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'invalid credentials'}), 401

    return jsonify({
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'role': user.role,
        'email_verified': user.email_verified,
        'account_status': user.account_status
    })

@app.post('/auth/register')
def register():
    data = request.get_json() or {}
    first_name = (data.get('first_name') or '').strip()
    last_name = (data.get('last_name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    role = data.get('role', 'user')
    is_vendor = data.get('is_vendor', False)
    
    # Set role based on is_vendor flag if role is not explicitly set
    if is_vendor and role == 'user':
        role = 'vendor'
    
    print(f"[DEBUG] Registration: role={role}, is_vendor={is_vendor}, email={email}")

    if not all([first_name, last_name, email, password]):
        return jsonify({'error': 'All fields are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    # No email verification required - users can register and use immediately
    account_status = 'active'
    email_verified = True

    # Create user
    user = User(
        first_name=first_name,
        last_name=last_name,
        name=f"{first_name} {last_name}",
        email=email,
        role=role,
        password_hash=generate_password_hash(password),
        email_verified=email_verified,
        account_status=account_status
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'role': user.role,
        'email_verified': user.email_verified,
        'account_status': user.account_status
    })

# Carousel Management Endpoints
@app.get('/carousel/slides')
def get_carousel_slides():
    """Get all active carousel slides"""
    slides = CarouselSlide.query.filter_by(is_active=True).order_by(CarouselSlide.sort_order.asc()).all()
    
    return jsonify([{
        'id': slide.id,
        'title': slide.title,
        'description': slide.description,
        'image_url': slide.image_url,
        'cta_text': slide.cta_text,
        'cta_url': slide.cta_url,
        'sort_order': slide.sort_order,
        'created_at': slide.created_at.isoformat() if slide.created_at else None,
        'updated_at': slide.updated_at.isoformat() if slide.updated_at else None
    } for slide in slides])

@app.get('/admin/carousel/slides')
def admin_get_carousel_slides():
    """Get all carousel slides for admin management"""
    slides = CarouselSlide.query.order_by(CarouselSlide.sort_order.asc()).all()
    
    return jsonify([{
        'id': slide.id,
        'title': slide.title,
        'description': slide.description,
        'image_url': slide.image_url,
        'cta_text': slide.cta_text,
        'cta_url': slide.cta_url,
        'is_active': slide.is_active,
        'sort_order': slide.sort_order,
        'created_at': slide.created_at.isoformat() if slide.created_at else None,
        'updated_at': slide.updated_at.isoformat() if slide.updated_at else None
    } for slide in slides])

@app.post('/admin/carousel/slides')
def admin_create_carousel_slide():
    """Create a new carousel slide (admin only)"""
    data = request.get_json() or {}
    
    # Required fields
    title = data.get('title', '').strip()
    image_url = data.get('image_url', '').strip()
    
    if not title or not image_url:
        return jsonify({'error': 'Title and image URL are required'}), 400
    
    # Optional fields
    description = data.get('description', '').strip()
    cta_text = data.get('cta_text', '').strip()
    cta_url = data.get('cta_url', '').strip()
    is_active = data.get('is_active', True)
    sort_order = data.get('sort_order', 0)
    
    try:
        slide = CarouselSlide(
            title=title,
            description=description,
            image_url=image_url,
            cta_text=cta_text,
            cta_url=cta_url,
            is_active=is_active,
            sort_order=sort_order
        )
        
        db.session.add(slide)
        db.session.commit()
        
        return jsonify({
            'id': slide.id,
            'title': slide.title,
            'description': slide.description,
            'image_url': slide.image_url,
            'cta_text': slide.cta_text,
            'cta_url': slide.cta_url,
            'is_active': slide.is_active,
            'sort_order': slide.sort_order,
            'created_at': slide.created_at.isoformat() if slide.created_at else None,
            'updated_at': slide.updated_at.isoformat() if slide.updated_at else None
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create carousel slide'}), 500

@app.put('/admin/carousel/slides/<int:slide_id>')
def admin_update_carousel_slide(slide_id):
    """Update a carousel slide (admin only)"""
    slide = CarouselSlide.query.get(slide_id)
    
    if not slide:
        return jsonify({'error': 'Carousel slide not found'}), 404
    
    data = request.get_json() or {}
    
    # Update fields
    if 'title' in data:
        slide.title = data['title'].strip()
    if 'description' in data:
        slide.description = data['description'].strip()
    if 'image_url' in data:
        slide.image_url = data['image_url'].strip()
    if 'cta_text' in data:
        slide.cta_text = data['cta_text'].strip()
    if 'cta_url' in data:
        slide.cta_url = data['cta_url'].strip()
    if 'is_active' in data:
        slide.is_active = data['is_active']
    if 'sort_order' in data:
        slide.sort_order = data['sort_order']
    
    try:
        db.session.commit()
        
        return jsonify({
            'id': slide.id,
            'title': slide.title,
            'description': slide.description,
            'image_url': slide.image_url,
            'cta_text': slide.cta_text,
            'cta_url': slide.cta_url,
            'is_active': slide.is_active,
            'sort_order': slide.sort_order,
            'created_at': slide.created_at.isoformat() if slide.created_at else None,
            'updated_at': slide.updated_at.isoformat() if slide.updated_at else None
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update carousel slide'}), 500

@app.delete('/admin/carousel/slides/<int:slide_id>')
def admin_delete_carousel_slide(slide_id):
    """Delete a carousel slide (admin only)"""
    slide = CarouselSlide.query.get(slide_id)
    
    if not slide:
        return jsonify({'error': 'Carousel slide not found'}), 404
    
    try:
        db.session.delete(slide)
        db.session.commit()
        
        return jsonify({'message': 'Carousel slide deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete carousel slide'}), 500

@app.post('/admin/carousel/upload')
def admin_upload_carousel_image():
    """Upload carousel image file (admin only)"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}), 400
    
    try:
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(filename)
        
        # Save file
        file_path = os.path.join(app.config['CAROUSEL_UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Return the URL path for the uploaded file
        image_url = f'/uploads/carousel/{unique_filename}'
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': unique_filename,
            'image_url': image_url
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to upload file'}), 500

@app.route('/uploads/carousel/<filename>')
def serve_carousel_image(filename):
    """Serve uploaded carousel images"""
    return send_from_directory(app.config['CAROUSEL_UPLOAD_FOLDER'], filename)

@app.post('/vendors/apply')
def vendor_apply():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    license_url = data.get('license_url')
    id_card_url = data.get('id_card_url')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    # Check if user exists and is a vendor
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.role != 'vendor':
        return jsonify({'error': 'Only vendors can apply'}), 400
    
    # Enforce admin settings for required documents and email verification
    try:
        from pathlib import Path
        instance_dir = Path(app.instance_path)
        settings_path = instance_dir / 'admin_settings.json'
        settings = {}
        if settings_path.exists():
            with settings_path.open('r', encoding='utf-8') as f:
                settings = json.load(f)
        require_email = bool(((settings.get('vendor') or {}).get('requireEmailVerification')))
        require_license = bool(((settings.get('vendor') or {}).get('requireLicense')))
        require_id = bool(((settings.get('vendor') or {}).get('requireId')))
    except Exception:
        # If settings are unavailable, default to optional docs and no email requirement
        require_email = False
        require_license = False
        require_id = False

    if require_email and not user.email_verified:
        return jsonify({'error': 'Email verification required before applying'}), 400

    # Validate required documents based on settings
    missing = []
    if require_license and not license_url:
        missing.append('license_url')
    if require_id and not id_card_url:
        missing.append('id_card_url')
    if missing:
        return jsonify({'error': f"Missing required fields: {', '.join(missing)}"}), 400

    # Check if application already exists
    existing_app = VendorApplication.query.filter_by(user_id=user_id).first()
    if existing_app:
        return jsonify({'error': 'Application already submitted'}), 400
    
    # Create vendor application
    application = VendorApplication(
        user_id=user_id,
        license_url=license_url,
        id_card_url=id_card_url,
        status='pending'
    )
    
    db.session.add(application)
    db.session.commit()
    
    print(f"[DEBUG] Created vendor application for user {user_id}")
    
    return jsonify({
        'id': application.id,
        'user_id': application.user_id,
        'status': application.status,
        'submitted_at': application.submitted_at.isoformat()
    })

@app.get('/products')
def get_products():
    # Get query parameters for pagination and filtering
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category', '')
    vendor_id = request.args.get('vendor_id', type=int)
    limit = request.args.get('limit', type=int)
    
    # Build query
    query = Product.query
    
    # Filter by category if provided
    if category:
        query = query.filter(Product.category.ilike(f'%{category}%'))
    
    # Filter by vendor_id if provided (for vendor dashboard)
    if vendor_id:
        query = query.filter(Product.vendor_id == vendor_id)
    
    # Order by newest first
    query = query.order_by(Product.created_at.desc())
    
    # Apply pagination or limit
    if limit:
        products = query.limit(limit).all()
    else:
        products = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        ).items
    
    # Optimize response - only include essential fields for list view
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description[:100] + '...' if p.description and len(p.description) > 100 else p.description,
        'price': p.price,
        'category': p.category,
        'vendor_id': p.vendor_id,
        'image_url': p.image_url,
        'stock_quantity': p.stock_quantity,
        'created_at': p.created_at.isoformat() if p.created_at else None
    } for p in products])

@app.get('/products/featured')
def get_featured_products():
    """Get featured products (newest 8 products)"""
    products = Product.query.order_by(Product.created_at.desc()).limit(8).all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description[:100] + '...' if p.description and len(p.description) > 100 else p.description,
        'price': p.price,
        'category': p.category,
        'vendor_id': p.vendor_id,
        'image_url': p.image_url,
        'stock_quantity': p.stock_quantity,
        'created_at': p.created_at.isoformat() if p.created_at else None
    } for p in products])

@app.get('/products/<int:product_id>')
def get_product(product_id):
    """Get a single product by ID"""
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Get vendor information
    vendor = User.query.get(product.vendor_id)
    vendor_name = f"{vendor.first_name} {vendor.last_name}" if vendor else "Unknown Vendor"
    
    # Parse colors and sizes from JSON strings
    colors = []
    sizes = []
    try:
        if product.colors:
            colors = json.loads(product.colors) if isinstance(product.colors, str) else product.colors
    except:
        colors = []
    
    try:
        if product.sizes:
            sizes = json.loads(product.sizes) if isinstance(product.sizes, str) else product.sizes
    except:
        sizes = []
    
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'original_price': getattr(product, 'original_price', None),
        'category': product.category,
        'vendor_id': product.vendor_id,
        'vendor_name': vendor_name,
        'image_url': product.image_url,
        'images': getattr(product, 'images', []) or [],
        'stock_quantity': product.stock_quantity,
        'colors': colors,
        'sizes': sizes,
        'brand': getattr(product, 'brand', None),
        'made': getattr(product, 'made', None),
        'rating': getattr(product, 'rating', 0) or 0,
        'is_featured': getattr(product, 'is_featured', False) or False,
        'created_at': product.created_at.isoformat() if product.created_at else None,
        'updated_at': product.updated_at.isoformat() if product.updated_at else None
    })

@app.post('/products')
def create_product():
    """Create a new product (vendor only)"""
    data = request.get_json() or {}
    print(f"[DEBUG] Product creation request data: {data}")
    
    # Required fields
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    price = data.get('price')
    category = data.get('category', '').strip()
    vendor_id = data.get('vendor_id')
    stock_quantity = data.get('stock_quantity', 0)
    
    print(f"[DEBUG] Parsed fields - name: '{name}', description: '{description}', price: {price}, category: '{category}', vendor_id: {vendor_id}, stock_quantity: {stock_quantity}")
    
    # Optional fields
    image_url = data.get('image_url', '').strip()
    colors = data.get('colors', [])
    sizes = data.get('sizes', [])
    
    # Validation
    required_fields = [name, description, price, category, vendor_id]
    print(f"[DEBUG] Required fields check: {required_fields}")
    if not all(required_fields):
        missing_fields = []
        if not name: missing_fields.append('name')
        if not description: missing_fields.append('description')
        if not price: missing_fields.append('price')
        if not category: missing_fields.append('category')
        if not vendor_id: missing_fields.append('vendor_id')
        error_msg = f'Missing required fields: {", ".join(missing_fields)}'
        print(f"[DEBUG] Validation error: {error_msg}")
        return jsonify({'error': error_msg}), 400
    
    if not isinstance(price, (int, float)) or price <= 0:
        error_msg = f'Price must be a positive number, got: {price} (type: {type(price)})'
        print(f"[DEBUG] Validation error: {error_msg}")
        return jsonify({'error': error_msg}), 400
    
    if not isinstance(stock_quantity, int) or stock_quantity < 0:
        error_msg = f'Stock quantity must be a non-negative integer, got: {stock_quantity} (type: {type(stock_quantity)})'
        print(f"[DEBUG] Validation error: {error_msg}")
        return jsonify({'error': error_msg}), 400
    
    # Check if vendor exists
    vendor = User.query.get(vendor_id)
    if not vendor or vendor.role != 'vendor':
        return jsonify({'error': 'Invalid vendor'}), 400
    
    # Create product
    product = Product(
        name=name,
        description=description,
        price=float(price),
        category=category,
        vendor_id=vendor_id,
        image_url=image_url,
        stock_quantity=stock_quantity,
        colors=json.dumps(colors) if colors else None,
        sizes=json.dumps(sizes) if sizes else None
    )
    
    db.session.add(product)
    db.session.commit()
    
    print(f"[DEBUG] Created product '{name}' for vendor {vendor_id}")
    
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'category': product.category,
        'vendor_id': product.vendor_id,
        'image_url': product.image_url,
        'stock_quantity': product.stock_quantity,
        'colors': colors,
        'sizes': sizes,
        'created_at': product.created_at.isoformat() if product.created_at else None
    }), 201

@app.delete('/products/<int:product_id>')
def delete_product(product_id):
    """Delete a product (vendor can delete their own, admin can delete any)"""
    data = request.get_json() or {}
    vendor_id = data.get('vendor_id')
    force = data.get('force', False)
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Check permissions
    # If force=True, allow admin to delete any product
    # Otherwise, only allow vendor to delete their own products
    if not force and vendor_id and product.vendor_id != vendor_id:
        return jsonify({'error': 'You can only delete your own products'}), 403
    
    # Check if product has any orders (optional safety check)
    order_items = OrderItem.query.filter_by(product_id=product_id).first()
    if order_items and not force:
        return jsonify({'error': 'Cannot delete product with existing orders. Use force=true to override.'}), 400
    
    # Delete the product
    db.session.delete(product)
    db.session.commit()
    
    print(f"[DEBUG] Deleted product {product_id} (vendor_id: {product.vendor_id})")
    
    return jsonify({'message': 'Product deleted successfully'})

@app.put('/products/<int:product_id>')
def update_product(product_id):
    """Update a product (vendor can update their own)"""
    data = request.get_json() or {}
    vendor_id = data.get('vendor_id')
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Check permissions - only allow vendor to update their own products
    if vendor_id and product.vendor_id != vendor_id:
        return jsonify({'error': 'You can only update your own products'}), 403
    
    # Update fields if provided
    if 'name' in data:
        product.name = data['name'].strip()
    if 'description' in data:
        product.description = data['description'].strip()
    if 'price' in data:
        price = data['price']
        if not isinstance(price, (int, float)) or price <= 0:
            return jsonify({'error': 'Price must be a positive number'}), 400
        product.price = float(price)
    if 'category' in data:
        product.category = data['category'].strip()
    if 'image_url' in data:
        product.image_url = data['image_url'].strip()
    if 'stock_quantity' in data:
        stock_quantity = data['stock_quantity']
        if not isinstance(stock_quantity, int) or stock_quantity < 0:
            return jsonify({'error': 'Stock quantity must be a non-negative integer'}), 400
        product.stock_quantity = stock_quantity
    if 'colors' in data:
        product.colors = json.dumps(data['colors']) if data['colors'] else None
    if 'sizes' in data:
        product.sizes = json.dumps(data['sizes']) if data['sizes'] else None
    
    product.updated_at = datetime.utcnow()
    db.session.commit()
    
    print(f"[DEBUG] Updated product {product_id} (vendor_id: {product.vendor_id})")
    
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'category': product.category,
        'vendor_id': product.vendor_id,
        'image_url': product.image_url,
        'stock_quantity': product.stock_quantity,
        'colors': json.loads(product.colors) if product.colors else [],
        'sizes': json.loads(product.sizes) if product.sizes else [],
        'updated_at': product.updated_at.isoformat() if product.updated_at else None
    })

@app.get('/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    response_data = {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'role': user.role,
        'email_verified': user.email_verified,
        'account_status': user.account_status
    }
    
    # Add vendor application if user is a vendor
    if user.role == 'vendor':
        print(f"[DEBUG] User {user_id} is a vendor, checking application...")
        # Query VendorApplication directly instead of using relationship
        vendor_app = VendorApplication.query.filter_by(user_id=user_id).first()
        if vendor_app:
            print(f"[DEBUG] Found vendor application with status: {vendor_app.status}")
            response_data['vendor_application'] = {
                'id': vendor_app.id,
                'status': vendor_app.status,
                'submitted_at': vendor_app.submitted_at.isoformat() if vendor_app.submitted_at else None,
                'reviewed_at': vendor_app.reviewed_at.isoformat() if vendor_app.reviewed_at else None
            }
        else:
            print(f"[DEBUG] No vendor application found for user {user_id}")
    
    print(f"[DEBUG] Returning user data: {response_data}")
    return jsonify(response_data)

@app.get('/vendors/applications')
def get_vendor_applications():
    """Get all vendor applications (admin only)"""
    applications = VendorApplication.query.all()
    print(f"[DEBUG] Found {len(applications)} vendor applications")
    return jsonify([{
                    'id': app.id,
                    'user_id': app.user_id,
                    'license_url': app.license_url,
                    'id_card_url': app.id_card_url,
                    'status': app.status,
        'admin_notes': app.admin_notes,
        'submitted_at': app.submitted_at.isoformat(),
        'reviewed_at': app.reviewed_at.isoformat() if app.reviewed_at else None,
                    'user': {
            'id': app.user.id,
            'name': app.user.name,
            'email': app.user.email
        }
    } for app in applications])

@app.get('/vendors/<int:vendor_id>/orders')
def get_vendor_orders(vendor_id):
    """Get all orders for a specific vendor"""
    # Get all order items for products belonging to this vendor
    order_items = db.session.query(OrderItem, Order, Product).join(
        Order, OrderItem.order_id == Order.id
    ).join(
        Product, OrderItem.product_id == Product.id
    ).filter(
        Product.vendor_id == vendor_id
    ).all()
    
    # Group order items by order
    orders_dict = {}
    for order_item, order, product in order_items:
        if order.id not in orders_dict:
            orders_dict[order.id] = {
                'id': order.id,
                'user_id': order.user_id,
                'total_amount': order.total_amount,
                'status': order.status,
                'payment_status': order.payment_status,
                'payment_method': order.payment_method,
                'payment_reference': order.payment_reference,
                'shipping_address': order.shipping_address,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'updated_at': order.updated_at.isoformat() if order.updated_at else None,
                'items': []
            }
        
        orders_dict[order.id]['items'].append({
            'id': order_item.id,
            'product_id': order_item.product_id,
            'product_name': product.name,
            'quantity': order_item.quantity,
            'price': order_item.price,
            'color': order_item.color,
            'size': order_item.size
        })
    
    orders = list(orders_dict.values())
    print(f"[DEBUG] Found {len(orders)} orders for vendor {vendor_id}")
    
    return jsonify(orders)

@app.post('/vendors/applications/<int:app_id>/status')
def update_vendor_application_status(app_id):
    """Update vendor application status (admin only)"""
    data = request.get_json() or {}
    status = data.get('status')
    admin_notes = data.get('admin_notes', '')
    
    if status not in ['approved', 'rejected']:
        return jsonify({'error': 'Invalid status'}), 400

    application = VendorApplication.query.get(app_id)
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    application.status = status
    application.admin_notes = admin_notes
    application.reviewed_at = datetime.utcnow()
    
    db.session.commit()
    
    print(f"[DEBUG] Updated vendor application {app_id} status to: {status}")
    
    return jsonify({
        'id': application.id,
        'status': application.status,
        'admin_notes': application.admin_notes,
        'reviewed_at': application.reviewed_at.isoformat()
    })

@app.post('/refunds')
def create_refund():
    """Create a new refund request"""
    data = request.get_json() or {}
    order_id = data.get('order_id')
    user_id = data.get('user_id')
    reason = data.get('reason')
    description = data.get('description', '')

    if not all([order_id, user_id, reason]):
        return jsonify({'error': 'order_id, user_id, and reason are required'}), 400

    # Verify order exists and belongs to user
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({'error': 'Order not found or does not belong to user'}), 404

    # Check if refund already exists
    existing_refund = Refund.query.filter_by(order_id=order_id).first()
    if existing_refund:
        return jsonify({'error': 'Refund request already exists for this order'}), 400

    # Enforce refund window from admin settings
    try:
        settings = _load_admin_settings()
        window_days = int(((settings.get('orders') or {}).get('refundWindowDays')) or 0)
    except Exception:
        window_days = 0
    if window_days > 0:
        try:
            created = order.created_at or datetime.utcnow()
            if (datetime.utcnow() - created).days > window_days:
                return jsonify({'error': f'Refund window of {window_days} days has expired'}), 400
        except Exception:
            pass

    # Find vendor from order items
    order_item = OrderItem.query.filter_by(order_id=order_id).first()
    if not order_item:
        return jsonify({'error': 'No items found in order'}), 400
    
    product = Product.query.get(order_item.product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    vendor_id = product.vendor_id

    # Create refund
    refund = Refund(
        order_id=order_id,
            user_id=user_id,
        vendor_id=vendor_id,
        amount=order.total_amount,
        reason=reason,
        description=description
    )
    
    db.session.add(refund)
    db.session.commit()

    return jsonify({
        'id': refund.id,
        'order_id': refund.order_id,
        'amount': refund.amount,
        'reason': refund.reason,
        'status': refund.status,
        'requested_at': refund.requested_at.isoformat()
    })

@app.get('/refunds')
def list_refunds():
    """List all refunds (admin only)"""
    refunds = db.session.query(
        Refund,
        User.first_name.label('user_name'),
        User.last_name.label('user_last_name'),
        User.email.label('user_email'),
        User.first_name.label('vendor_name'),
        User.last_name.label('vendor_last_name')
    ).join(
        User, Refund.user_id == User.id
    ).join(
        User, Refund.vendor_id == User.id, aliased=True
    ).all()

    return jsonify([{
        'id': refund.id,
        'order_id': refund.order_id,
        'user_name': f"{user_name} {user_last_name}",
        'vendor_name': f"{vendor_name} {vendor_last_name}",
        'amount': refund.amount,
        'reason': refund.reason,
        'status': refund.status,
        'requested_at': refund.requested_at.isoformat()
    } for refund, user_name, user_last_name, user_email, vendor_name, vendor_last_name in refunds])

@app.get('/users/<int:user_id>/refunds')
def list_user_refunds(user_id):
    """List refunds for a specific user"""
    refunds = Refund.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': refund.id,
        'order_id': refund.order_id,
        'amount': refund.amount,
        'reason': refund.reason,
        'status': refund.status,
        'requested_at': refund.requested_at.isoformat()
    } for refund in refunds])

@app.put('/refunds/<int:refund_id>/status')
def update_refund_status(refund_id):
    """Update refund status (admin only)"""
    data = request.get_json() or {}
    status = data.get('status')
    admin_notes = data.get('admin_notes', '')

    if not status:
        return jsonify({'error': 'status is required'}), 400

    refund = Refund.query.get(refund_id)
    if not refund:
        return jsonify({'error': 'Refund not found'}), 404

    refund.status = status
    refund.admin_notes = admin_notes
    if status == 'processed':
        refund.processed_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'id': refund.id,
        'status': refund.status,
        'admin_notes': refund.admin_notes
    })

@app.post('/refunds/<int:refund_id>/process')
def process_refund(refund_id):
    """Process refund payment (admin only)"""
    data = request.get_json() or {}
    payment_method = data.get('payment_method')
    payment_reference = data.get('payment_reference')

    if not all([payment_method, payment_reference]):
        return jsonify({'error': 'payment_method and payment_reference are required'}), 400

    refund = Refund.query.get(refund_id)
    if not refund:
        return jsonify({'error': 'Refund not found'}), 404

    refund.payment_method = payment_method
    refund.payment_reference = payment_reference
    refund.status = 'processed'
    refund.processed_at = datetime.utcnow()
    
    db.session.commit()

    return jsonify({
        'id': refund.id,
        'status': refund.status,
        'payment_method': refund.payment_method,
        'payment_reference': refund.payment_reference
    })

@app.post('/payments/checkout')
def checkout():
    """Initialize payment checkout with vendor split support.

    Modes:
    - split_mode = 'single' (default): Create ParentOrder and child Orders per vendor; one tx_ref and one checkout.
    - split_mode = 'per_vendor': Create child Orders per vendor; each has its own tx_ref and checkout.
    """
    try:
        data = request.get_json() or {}
        print(f"[DEBUG] Checkout request data: {data}")
        
        user_id = data.get('user_id')
        items = data.get('items', [])
        shipping = data.get('shipping', {})
        split_mode = (data.get('split_mode') or 'single').lower()
        raw_email = (data.get('email') or '').strip().lower()
        raw_first = (data.get('first_name') or '').strip()
        raw_last = (data.get('last_name') or '').strip()
        raw_phone = (data.get('phone') or '').strip()
        
        if not user_id or not items:
            error_msg = f'user_id and items are required, got user_id: {user_id}, items: {items}'
            return jsonify({'error': error_msg}), 400
        
        # Group items by vendor
        def _get_pid(it):
            try:
                return (
                    it.get('product_id') or it.get('productId') or it.get('id') or
                    ((it.get('product') or {}).get('id'))
                )
            except Exception:
                return None

        vendor_to_lines = {}
        total_amount = 0.0
        for item in items:
            pid = _get_pid(item)
            qty = int(item.get('quantity') or 0)
            if not pid or qty <= 0:
                if DEBUG:
                    print(f"[CHECKOUT] Skipping invalid item: {item}")
                continue
            product = Product.query.get(pid)
            if not product:
                if DEBUG:
                    print(f"[CHECKOUT] Product not found: {pid}")
                continue
            line_total = product.price * qty
            total_amount += line_total
            vid = product.vendor_id or 0
            vendor_to_lines.setdefault(vid, []).append((product, qty))

        if not vendor_to_lines:
            return jsonify({'error': 'No valid products found for checkout'}), 400
        if total_amount <= 0:
            return jsonify({'error': 'Total amount must be greater than zero'}), 400

        # Initialize user details for gateway
        currency = (data.get('currency') or 'ETB').upper()
        if currency not in ['ETB', 'USD']:
            currency = 'ETB'
        user = User.query.get(user_id)
        fallback_email = (user.email.strip().lower() if user and isinstance(user.email, str) else '')
        email = raw_email if _is_valid_email(raw_email) else (fallback_email if _is_valid_email(fallback_email) else 'customer@example.com')
        first_name = raw_first or (user.first_name if user and user.first_name else '') or 'Customer'
        last_name = raw_last or (user.last_name if user and user.last_name else '')
        phone = raw_phone
        customer = { 'first_name': first_name, 'last_name': last_name, 'name': f"{first_name} {last_name}".strip(), 'email': email, 'phone': phone }

        if split_mode == 'per_vendor':
            sessions = []
            created_orders = []
            for vid, lines in vendor_to_lines.items():
                order_total = sum(p.price * qty for p, qty in lines)
                order = Order(user_id=user_id, total_amount=order_total, status='pending', payment_status='pending', shipping_address=json.dumps(shipping))
                db.session.add(order)
                db.session.flush()
                for p, qty in lines:
                    db.session.add(OrderItem(order_id=order.id, product_id=p.id, quantity=qty, price=p.price))
                tx_ref = f"order_{order.id}_{uuid.uuid4().hex[:8]}"
                order.payment_method = 'chapa'
                order.payment_reference = tx_ref
                created_orders.append(order)
                # Create a chapa session per order
                resp = initiate_chapa_payment(order_total, currency, customer, tx_ref)
                if (resp.get('status') != 'success'):
                    db.session.rollback()
                    return jsonify({'error': 'Failed to initialize vendor payment', 'details': resp}), 502
                sessions.append({
                    'order_id': order.id,
                    'tx_ref': tx_ref,
                    'checkout_url': ((resp.get('data') or {}).get('checkout_url')) or ''
                })
            db.session.commit()
            return jsonify({ 'mode': 'per_vendor', 'sessions': sessions, 'currency': currency })
        else:
            # Single payment for all vendors: attempt ParentOrder linkage; if DB lacks column, fall back automatically
            use_parent = False
            try:
                use_parent = (_sqlite_has_column('order', 'parent_order_id') if db.engine.name == 'sqlite' else True)
            except Exception:
                use_parent = False

            def create_orders(with_parent: bool):
                parent_local = None
                child_local = []
                if with_parent:
                    parent_local = ParentOrder(user_id=user_id, total_amount=total_amount, status='pending')
                    db.session.add(parent_local)
                    db.session.flush()
                for vid, lines in vendor_to_lines.items():
                    order_total = sum(p.price * qty for p, qty in lines)
                    kwargs = {
                        'user_id': user_id,
                        'total_amount': order_total,
                        'status': 'pending',
                        'payment_status': 'pending',
                        'shipping_address': json.dumps(shipping)
                    }
                    if with_parent and parent_local is not None:
                        kwargs['parent_order_id'] = parent_local.id
                    order = Order(**kwargs)
                    db.session.add(order)
                    db.session.flush()
                    for p, qty in lines:
                        db.session.add(OrderItem(order_id=order.id, product_id=p.id, quantity=qty, price=p.price))
                    child_local.append(order)
                return parent_local, child_local

            parent = None
            child_orders = []
            try:
                if use_parent:
                    parent = ParentOrder(user_id=user_id, total_amount=total_amount, status='pending')
                    db.session.add(parent)
                    db.session.flush()
                # Insert child orders with compatibility helper
                for vid, lines in vendor_to_lines.items():
                    order_total = sum(p.price * qty for p, qty in lines)
                    order = _insert_order_compat(
                        user_id=user_id,
                        total_amount=order_total,
                        status='pending',
                        payment_status='pending',
                        shipping_address_json=json.dumps(shipping),
                        parent_order_id=(parent.id if parent is not None else None)
                    )
                    for p, qty in lines:
                        db.session.add(OrderItem(order_id=order.id, product_id=p.id, quantity=qty, price=p.price))
                    child_orders.append(order)
            except Exception as e:
                # Retry fully without parent
                db.session.rollback()
                parent = None
                child_orders = []
                for vid, lines in vendor_to_lines.items():
                    order_total = sum(p.price * qty for p, qty in lines)
                    order = _insert_order_compat(
                        user_id=user_id,
                        total_amount=order_total,
                        status='pending',
                        payment_status='pending',
                        shipping_address_json=json.dumps(shipping),
                        parent_order_id=None
                    )
                    for p, qty in lines:
                        db.session.add(OrderItem(order_id=order.id, product_id=p.id, quantity=qty, price=p.price))
                    child_orders.append(order)

            tx_prefix = f"parent_{parent.id}" if parent is not None else f"batch_{uuid.uuid4().hex[:4]}"
            tx_ref = f"{tx_prefix}_{uuid.uuid4().hex[:8]}"
            if parent is not None:
                parent.tx_ref = tx_ref
            for o in child_orders:
                o.payment_method = 'chapa'
                o.payment_reference = tx_ref
            db.session.commit()

            resp = initiate_chapa_payment(total_amount, currency, customer, tx_ref)
            if (resp.get('status') != 'success'):
                return jsonify({'error': 'Failed to initialize payment', 'details': resp}), 502
            checkout_url = ((resp.get('data') or {}).get('checkout_url')) or ''
            if not checkout_url:
                return jsonify({'error': 'Checkout URL not returned by gateway'}), 502
            return jsonify({ 'mode': 'single', 'parent_order_id': (parent.id if parent is not None else None), 'order_ids': [o.id for o in child_orders], 'tx_ref': tx_ref, 'checkout_url': checkout_url, 'total_amount': total_amount, 'currency': currency })
    except Exception as e:
        db.session.rollback()
        err = f"{e}"
        try:
            traceback.print_exc()
        except Exception:
            pass
        return jsonify({'error': 'Checkout failed. Please try again.' if not DEBUG else f'Checkout failed: {err}'}), 500

# Alias to support frontend calling /api/payments/checkout
@app.post('/api/payments/checkout')
def checkout_api_alias():
    return checkout()

# ----------------------
# Place Order (Pending) - no payment required (testing mode)
# ----------------------

@app.post('/orders/place')
def place_order_pending():
    """Create order(s) in pending state without initiating payment.
    Request JSON: { user_id, items:[{product_id,quantity}], shipping:{} }
    Groups items by vendor and creates one order per vendor.
    """
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        items = data.get('items') or []
        shipping = data.get('shipping') or {}
        if not user_id or not items:
            return jsonify({'error': 'user_id and items are required'}), 400

        # Group items by vendor
        def _get_pid(it):
            try:
                return it.get('product_id') or it.get('productId') or it.get('id') or ((it.get('product') or {}).get('id'))
            except Exception:
                return None
        vendor_to_lines = {}
        for it in items:
            pid = _get_pid(it)
            qty = int(it.get('quantity') or 0)
            if not pid or qty <= 0:
                continue
            p = Product.query.get(pid)
            if not p:
                continue
            vendor_to_lines.setdefault(p.vendor_id or 0, []).append((p, qty))

        if not vendor_to_lines:
            return jsonify({'error': 'No valid products'}), 400

        created = []
        for vid, lines in vendor_to_lines.items():
            total = sum(p.price * qty for p, qty in lines)
            # Use compatibility insert to avoid missing parent_order_id column in older SQLite DBs
            order = _insert_order_compat(
                user_id=user_id,
                total_amount=total,
                status='pending',
                payment_status='pending',
                shipping_address_json=json.dumps(shipping or {}),
                parent_order_id=None
            )
            for p, qty in lines:
                db.session.add(OrderItem(order_id=order.id, product_id=p.id, quantity=qty, price=p.price))
            created.append(order)
        db.session.commit()

        # Notify vendors and admin (best-effort)
        try:
            for o in created:
                first_item = OrderItem.query.filter_by(order_id=o.id).first()
                if first_item:
                    product = Product.query.get(first_item.product_id)
                    vendor = User.query.get(product.vendor_id) if product else None
                    if vendor and vendor.email:
                        msg = Message(
                            subject='New Order Placed',
                            sender=app.config['MAIL_USERNAME'] or 'no-reply@example.com',
                            recipients=[vendor.email],
                            body=f'Order #{o.id} has been placed and is pending payment. Please prepare for fulfillment.'
                        )
                        send_mail_background(msg)
            if ADMIN_EMAIL:
                msg = Message(
                    subject='New Pending Order(s)',
                    sender=app.config['MAIL_USERNAME'] or 'no-reply@example.com',
                    recipients=[ADMIN_EMAIL],
                    body=f'{len(created)} pending order(s) created.'
                )
                send_mail_background(msg)
        except Exception:
            pass

        return jsonify({
            'ok': True,
            'order_ids': [o.id for o in created],
            'total_orders': len(created)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to place order: {e}'}), 500

@app.post('/orders/<int:order_id>/complete')
def complete_order(order_id):
    """Complete order after successful payment (or delivery confirmation)."""
    try:
        data = request.get_json() or {}
        payment_method = data.get('payment_method')
        payment_reference = data.get('payment_reference')
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Update order status
        order.status = 'completed'
        order.payment_status = order.payment_status or 'paid'
        order.payment_method = payment_method
        order.payment_reference = payment_reference
        order.updated_at = datetime.utcnow()
        try:
            _release_commission_on_complete(order)
        except Exception:
            pass
        db.session.commit()
        
        return jsonify({
            'id': order.id,
            'status': order.status,
            'payment_status': order.payment_status,
            'payment_method': order.payment_method,
            'payment_reference': order.payment_reference
        })
        
    except Exception as e:
        print(f"Complete order error: {e}")
        return jsonify({'error': 'Failed to complete order'}), 500

@app.post('/orders/<int:order_id>/confirm-delivery')
def confirm_delivery(order_id):
    """Buyer confirms delivery: transition confirmed/shipped → completed."""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        order.status = 'completed'
        order.updated_at = datetime.utcnow()
        try:
            _release_commission_on_complete(order)
        except Exception:
            pass
        db.session.commit()
        return jsonify({'id': order.id, 'status': order.status})
    except Exception as e:
        return jsonify({'error': f'Failed to confirm delivery: {e}'}), 500

@app.post('/orders/auto-complete')
def auto_complete_orders():
    """Admin/cron: auto-complete orders older than X days (no disputes)."""
    try:
        days = int((request.args.get('days') or 7))
        cutoff = datetime.utcnow() - timedelta(days=days)
        q = Order.query.filter(Order.status.in_(['confirmed','shipped','delivered']), Order.updated_at <= cutoff)
        count = 0
        for o in q.all():
            o.status = 'completed'
            o.updated_at = datetime.utcnow()
            try:
                _release_commission_on_complete(o)
            except Exception:
                pass
            count += 1
        db.session.commit()
        return jsonify({'ok': True, 'auto_completed': count})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to auto-complete: {e}'}), 500

@app.post('/orders/<int:order_id>/payment-method')
def set_order_payment_method(order_id):
    """Set or change payment method and address after checkout (transfer/COD/chapa)."""
    try:
        data = request.get_json() or {}
        payment_method = (data.get('payment_method') or '').strip().lower()
        address = data.get('address') or {}

        if payment_method not in ['transfer', 'cod', 'chapa']:
            return jsonify({'error': 'Invalid payment_method'}), 400

        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        # Update address
        try:
            order.shipping_address = json.dumps(address or {})
        except Exception:
            order.shipping_address = json.dumps({})

        # Update payment method
        order.payment_method = payment_method
        if payment_method in ['transfer', 'cod']:
            # Mark as pending payment/processing until backoffice confirms
            order.payment_status = 'pending'
            order.status = 'pending'
        order.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'id': order.id,
            'status': order.status,
            'payment_status': order.payment_status,
            'payment_method': order.payment_method,
            'shipping_address': json.loads(order.shipping_address or '{}')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to set payment method: {e}'}), 500

@app.post('/payments/chapa/callback')
def chapa_callback():
    """Chapa server-to-server callback to confirm payment and update order."""
    try:
        # Basic signature verification if a webhook secret is configured.
        # Many gateways send a signature in header like 'X-Chapa-Signature'.
        # We compute HMAC-SHA256 over raw body with CHAPA_WEBHOOK_SECRET.
        raw_body = request.get_data() or b''
        sig_header = request.headers.get('X-Chapa-Signature') or request.headers.get('x-chapa-signature')
        if CHAPA_WEBHOOK_SECRET:
            try:
                digest = hmac.new(CHAPA_WEBHOOK_SECRET.encode('utf-8'), raw_body, hashlib.sha256).hexdigest()
                if not sig_header or not hmac.compare_digest(digest, sig_header.strip()):
                    return jsonify({'error': 'Invalid webhook signature'}), 401
            except Exception:
                return jsonify({'error': 'Signature verification failed'}), 401

        data = request.get_json(silent=True) or request.form.to_dict() or {}
        tx_ref = data.get('tx_ref') or data.get('reference') or ''
        status = data.get('status') or ''
        if not tx_ref:
            return jsonify({'error': 'tx_ref is required'}), 400

        order = Order.query.filter_by(payment_reference=tx_ref).first()
        parent = ParentOrder.query.filter_by(tx_ref=tx_ref).first()
        if not order and not parent:
            return jsonify({'error': 'Order not found for tx_ref'}), 404

        # Idempotency: if already paid, exit early
        if order and order.payment_status == 'paid':
            return jsonify({'ok': True, 'message': 'Already processed', 'tx_ref': tx_ref})
        if parent and parent.status == 'paid':
            return jsonify({'ok': True, 'message': 'Already processed', 'tx_ref': tx_ref})

        verify_resp = verify_chapa_transaction(tx_ref)
        if verify_resp.get('error'):
            return jsonify({'error': verify_resp['error']}), 502

        # Expected verify success shape: { status: 'success', data: { status: 'success', ... } }
        v_status = verify_resp.get('status')
        v_data = verify_resp.get('data') or {}
        paid_ok = (v_status == 'success') and ((v_data.get('status') or '').lower() == 'success')
        if not paid_ok:
            if order:
                order.payment_status = 'failed'
                order.status = 'pending'
                order.updated_at = datetime.utcnow()
            if parent:
                parent.status = 'pending'
                parent.updated_at = datetime.utcnow()
            db.session.commit()
            return jsonify({'message': 'Payment not successful', 'details': verify_resp}), 400

        # Success path: mark paid
        if parent:
            parent.status = 'paid'
            parent.updated_at = datetime.utcnow()
            # mark all child orders paid/confirmed
            children = Order.query.filter_by(parent_order_id=parent.id).all()
            for ch in children:
                ch.status = 'completed'
                ch.payment_status = 'paid'
                ch.updated_at = datetime.utcnow()
                try:
                    ch.receipt_url = f"/orders/{ch.id}/invoice"
                except Exception:
                    pass
        if order:
            order.status = 'completed'
            order.payment_status = 'paid'
            order.updated_at = datetime.utcnow()
            try:
                order.receipt_url = f"/orders/{order.id}/invoice"
            except Exception:
                pass
        db.session.commit()

        # TODO: Notify vendors (email/SMS/dashboard). Stub for now.
        try:
            if parent:
                children = Order.query.filter_by(parent_order_id=parent.id).all()
                for ch in children:
                    first_item = OrderItem.query.filter_by(order_id=ch.id).first()
                    if not first_item:
                        continue
                    product = Product.query.get(first_item.product_id)
                    vendor = User.query.get(product.vendor_id) if product else None
                    if vendor and vendor.email:
                        msg = Message(
                            subject='New Order Paid',
                            sender=app.config['MAIL_USERNAME'] or 'no-reply@example.com',
                            recipients=[vendor.email],
                            body=f'Order #{ch.id} has been paid. Please fulfill.'
                        )
                        send_mail_background(msg)
                        try:
                            msg2 = Message(
                                subject=f'Invoice for Order #{ch.id}',
                                sender=app.config['MAIL_USERNAME'] or 'no-reply@example.com',
                                recipients=[vendor.email],
                                body=f'Your order has been paid. Download the invoice: {request.host_url.rstrip("/")}/orders/{ch.id}/invoice'
                            )
                            send_mail_background(msg2)
                        except Exception:
                            pass
                try:
                    if ADMIN_EMAIL:
                        msga = Message(
                            subject='New Paid Order (Invoice)',
                            sender=app.config['MAIL_USERNAME'] or 'no-reply@example.com',
                            recipients=[ADMIN_EMAIL],
                            body=f'Paid order(s) under tx_ref {tx_ref}. Example invoice: {request.host_url.rstrip("/")}/orders/{(children[0].id if children else order.id)}/invoice'
                        )
                        send_mail_background(msga)
                except Exception:
                    pass
            elif order:
                first_item = OrderItem.query.filter_by(order_id=order.id).first()
                if first_item:
                    product = Product.query.get(first_item.product_id)
                    vendor = User.query.get(product.vendor_id) if product else None
                    if vendor and vendor.email:
                        msg = Message(
                            subject='New Order Paid',
                            sender=app.config['MAIL_USERNAME'] or 'no-reply@example.com',
                            recipients=[vendor.email],
                            body=f'Order #{order.id} has been paid. Please fulfill.'
                        )
                        send_mail_background(msg)
                        try:
                            msg2 = Message(
                                subject=f'Invoice for Order #{order.id}',
                                sender=app.config['MAIL_USERNAME'] or 'no-reply@example.com',
                                recipients=[vendor.email],
                                body=f'Your order has been paid. Download the invoice: {request.host_url.rstrip("/")}/orders/{order.id}/invoice'
                            )
                            send_mail_background(msg2)
                        except Exception:
                            pass
                try:
                    if ADMIN_EMAIL:
                        msga = Message(
                            subject='New Paid Order (Invoice)',
                            sender=app.config['MAIL_USERNAME'] or 'no-reply@example.com',
                            recipients=[ADMIN_EMAIL],
                            body=f'Paid order #{order.id}. Invoice: {request.host_url.rstrip("/")}/orders/{order.id}/invoice'
                        )
                        send_mail_background(msga)
                except Exception:
                    pass
        except Exception:
            pass

        return jsonify({'ok': True, 'order_id': order.id if order else None, 'parent_order_id': parent.id if parent else None, 'tx_ref': tx_ref})
    except Exception as e:
        return jsonify({'error': f'Callback handling failed: {e}'}), 500

@app.get('/api/payments/verify')
def api_verify_payment():
    """Verify a payment by tx_ref and update the related order. Returns a compact shape expected by the frontend.

    Response example on success:
    { ok: True, tx_ref, order_id, amount, currency, status: 'success' }
    """
    try:
        tx_ref = (request.args.get('tx_ref') or '').strip()
        if not tx_ref:
            return jsonify({'error': 'tx_ref is required'}), 400

        order = Order.query.filter_by(payment_reference=tx_ref).first()
        parent = ParentOrder.query.filter_by(tx_ref=tx_ref).first()
        if not order and not parent:
            return jsonify({'error': 'Order not found for tx_ref'}), 404

        verify_resp = verify_chapa_transaction(tx_ref)
        if verify_resp.get('error'):
            return jsonify({'error': verify_resp['error']}), 502

        v_status = (verify_resp.get('status') or '').lower()
        v_data = verify_resp.get('data') or {}
        paid_ok = (v_status == 'success') and ((v_data.get('status') or '').lower() == 'success')

        if paid_ok:
            if parent:
                parent.status = 'paid'
                parent.updated_at = datetime.utcnow()
                children = Order.query.filter_by(parent_order_id=parent.id).all()
                for ch in children:
                    ch.status = 'completed'
                    ch.payment_status = 'paid'
                    ch.updated_at = datetime.utcnow()
            if order:
                order.status = 'completed'
                order.payment_status = 'paid'
                order.updated_at = datetime.utcnow()
            db.session.commit()
        else:
            if parent:
                parent.status = 'pending'
                parent.updated_at = datetime.utcnow()
                db.session.commit()
            if order:
                order.payment_status = 'failed'
                order.status = 'pending'
                order.updated_at = datetime.utcnow()
                db.session.commit()

        amount = None
        currency = None
        try:
            amount = float(v_data.get('amount')) if v_data.get('amount') is not None else None
        except Exception:
            amount = None
        currency = v_data.get('currency') or None

        return jsonify({
            'ok': paid_ok,
            'tx_ref': tx_ref,
            'order_id': order.id if order else None,
            'parent_order_id': parent.id if parent else None,
            'amount': amount,
            'currency': currency,
            'status': (v_data.get('status') or '').lower() or v_status
        })
    except Exception as e:
        return jsonify({'error': f'Verify failed: {e}'}), 500

@app.get('/api/payments/status')
def api_payment_status():
    """Return a lightweight payment audit/status trail for a tx_ref.

    This is a best-effort helper for the UI; for now it synthesizes a small trail
    from the order's current state and a fresh verify call.
    """
    try:
        tx_ref = (request.args.get('tx_ref') or '').strip()
        if not tx_ref:
            return jsonify({'error': 'tx_ref is required'}), 400

        order = Order.query.filter_by(payment_reference=tx_ref).first()
        parent = ParentOrder.query.filter_by(tx_ref=tx_ref).first()
        if not order and not parent:
            return jsonify({'error': 'Order not found for tx_ref'}), 404

        trail = []
        if parent:
            trail.append({
                'id': f'parent-{parent.id}',
                'event': 'parent_created',
                'status': parent.status,
                'created_at': (parent.created_at or datetime.utcnow()).isoformat()
            })
            # include one child snapshot
            ch = Order.query.filter_by(parent_order_id=parent.id).first()
            if ch:
                order = ch
        if order:
            trail.append({
                'id': f'created-{order.id}',
                'event': 'order_created',
                'status': order.status,
                'created_at': (order.created_at or datetime.utcnow()).isoformat()
            })

        # Try a fresh verify to enrich the trail
        v_resp = verify_chapa_transaction(tx_ref)
        v_status = (v_resp.get('status') or '').lower()
        v_data = v_resp.get('data') or {}
        trail.append({
            'id': f'gateway-{order.id}',
            'event': 'gateway_verify',
            'status': (v_data.get('status') or v_status),
            'created_at': datetime.utcnow().isoformat()
        })

        if order:
            trail.append({
                'id': f'order-{order.id}',
                'event': 'order_update',
                'status': f"{order.status}:{order.payment_status}",
                'created_at': (order.updated_at or order.created_at or datetime.utcnow()).isoformat()
            })

        return jsonify(trail)
    except Exception as e:
        return jsonify({'error': f'Status failed: {e}'}), 500

# ----------------------
# Admin: Reconcile pending Chapa payments (manual/cron)
# ----------------------

@app.post('/admin/payments/reconcile')
def admin_reconcile_payments():
    """Verify recent pending Chapa orders and update their status.

    Query params:
      hours: how far back to look (default 24)
      limit: max orders to process (default 50)
    """
    try:
        hours = int(request.args.get('hours') or 24)
        limit = min(int(request.args.get('limit') or 50), 500)
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        candidates = Order.query.filter(
            Order.payment_method == 'chapa',
            Order.payment_status.in_(['pending', None]),
            Order.created_at >= cutoff,
            Order.payment_reference.isnot(None)
        ).order_by(Order.created_at.desc()).limit(limit).all()

        reconciled = []
        for o in candidates:
            tx_ref = (o.payment_reference or '').strip()
            if not tx_ref:
                continue
            v = verify_chapa_transaction(tx_ref)
            v_status = (v.get('status') or '').lower()
            v_data = v.get('data') or {}
            paid_ok = (v_status == 'success') and ((v_data.get('status') or '').lower() == 'success')
            if paid_ok:
                o.status = 'completed'
                o.payment_status = 'paid'
                o.updated_at = datetime.utcnow()
                reconciled.append(o.id)
        if reconciled:
            db.session.commit()
        return jsonify({'ok': True, 'checked': len(candidates), 'updated': len(reconciled), 'orders': reconciled})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Reconcile failed: {e}'}), 500

@app.get('/admin/settings')
def get_admin_settings():
    try:
        return jsonify(_load_admin_settings())
    except Exception as e:
        return jsonify({'error': f'Failed to load settings: {e}'}), 500

@app.put('/admin/settings')
def put_admin_settings():
    try:
        data = request.get_json() or {}
        instance_dir = Path(app.instance_path)
        instance_dir.mkdir(parents=True, exist_ok=True)
        settings_path = instance_dir / 'admin_settings.json'
        with settings_path.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': f'Failed to save settings: {e}'}), 500

@app.get('/admin/categories')
def get_admin_categories():
    try:
        instance_dir = Path(app.instance_path)
        instance_dir.mkdir(parents=True, exist_ok=True)
        path = instance_dir / 'admin_categories.json'
        if path.exists():
            with path.open('r', encoding='utf-8') as f:
                return jsonify(json.load(f) or [])
        return jsonify([])
    except Exception as e:
        return jsonify({'error': f'Failed to load categories: {e}'}), 500

# ----------------------
# Admin Metrics Endpoints
# ----------------------

def _dt_floor_day(dt: datetime) -> datetime:
    return datetime(dt.year, dt.month, dt.day)

@app.get('/admin/metrics/sales')
def metrics_sales():
    try:
        rng = (request.args.get('range') or '30d').lower()
        days = 30
        if rng.endswith('d'):
            try: days = int(rng[:-1])
            except: days = 30
        start = datetime.utcnow() - timedelta(days=days)

        orders = Order.query.filter(Order.payment_status=='paid', Order.updated_at >= start).all()
        buckets = {}
        for o in orders:
            d = _dt_floor_day(o.updated_at or o.created_at or datetime.utcnow())
            key = d.strftime('%Y-%m-%d')
            buckets[key] = buckets.get(key, 0.0) + float(o.total_amount or 0.0)
        series = sorted(([k, buckets[k]] for k in buckets.keys()), key=lambda x: x[0])
        return jsonify({'series': series})
    except Exception as e:
        return jsonify({'error': f'Failed to load sales metrics: {e}'}), 500

@app.get('/admin/metrics/orders/status')
def metrics_orders_status():
    try:
        rng = (request.args.get('range') or '30d').lower()
        days = 30
        if rng.endswith('d'):
            try: days = int(rng[:-1])
            except: days = 30
        start = datetime.utcnow() - timedelta(days=days)
        q = Order.query.filter(Order.created_at >= start)
        counts = {}
        for o in q.all():
            s = (o.status or 'pending').lower()
            counts[s] = counts.get(s, 0) + 1
        return jsonify(counts)
    except Exception as e:
        return jsonify({'error': f'Failed to load order status metrics: {e}'}), 500

@app.get('/admin/metrics/vendors/top')
def metrics_top_vendors():
    try:
        rng = (request.args.get('range') or '30d').lower()
        limit = int(request.args.get('limit') or 10)
        days = 30
        if rng.endswith('d'):
            try: days = int(rng[:-1])
            except: days = 30
        start = datetime.utcnow() - timedelta(days=days)
        # Sum revenue by vendor for paid orders
        rows = db.session.query(OrderItem, Order, Product).join(Order, OrderItem.order_id==Order.id).join(Product, OrderItem.product_id==Product.id).filter(Order.payment_status=='paid', Order.updated_at >= start).all()
        rev = {}
        for oi, o, p in rows:
            amount = float(oi.price or 0.0) * float(oi.quantity or 0)
            vid = p.vendor_id or 0
            rev[vid] = rev.get(vid, 0.0) + amount
        # Map vendor name
        out = []
        for vid, amt in rev.items():
            vendor = User.query.get(vid)
            name = vendor.name if vendor and getattr(vendor, 'name', None) else (vendor.email if vendor else f'Vendor {vid}')
            out.append({'vendor_id': vid, 'vendor_name': name, 'revenue': round(amt, 2)})
        out.sort(key=lambda x: x['revenue'], reverse=True)
        return jsonify(out[:limit])
    except Exception as e:
        return jsonify({'error': f'Failed to load top vendors: {e}'}), 500

# ----------------------
# Simple Invoice Endpoint (HTML)
# ----------------------

@app.get('/orders/<int:order_id>/invoice')
def get_order_invoice(order_id: int):
    """Return a simple HTML invoice for the order (for download/print)."""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        user = User.query.get(order.user_id)
        items = db.session.query(OrderItem, Product).join(Product, OrderItem.product_id==Product.id).filter(OrderItem.order_id==order.id).all()
        try:
            shipping = json.loads(order.shipping_address or '{}')
        except Exception:
            shipping = {}

        rows_html = []
        subtotal = 0.0
        for oi, p in items:
            line_total = float(oi.price or 0.0) * float(oi.quantity or 0)
            subtotal += line_total
            rows_html.append(f"<tr><td>{(p.name or 'Product')}</td><td style='text-align:center'>{oi.quantity}</td><td style='text-align:right'>{oi.price:.2f}</td><td style='text-align:right'>{line_total:.2f}</td></tr>")

        html = f"""
<!doctype html>
<html>
<head>
  <meta charset='utf-8'/>
  <title>Invoice #{order.id}</title>
  <style>
    body {{ font-family: Arial, sans-serif; color:#111827; padding: 20px; }}
    .header {{ display:flex; justify-content:space-between; align-items:flex-start; }}
    .title {{ font-size: 20px; font-weight: 700; }}
    .badge {{ display:inline-block; padding:4px 8px; border-radius:999px; border:1px solid #e5e7eb; font-size:12px; font-weight:700; }}
    .paid {{ background:#ecfdf5; color:#065f46; border-color:#10b981 }}
    .pending {{ background:#eff6ff; color:#1e3a8a; border-color:#3b82f6 }}
    .failed {{ background:#fef2f2; color:#7f1d1d; border-color:#ef4444 }}
    table {{ width:100%; border-collapse: collapse; margin-top: 16px; }}
    th, td {{ border-bottom:1px solid #e5e7eb; padding: 8px; font-size: 14px; }}
    th {{ text-align: left; background:#f9fafb; }}
    .totals {{ text-align:right; margin-top: 12px; }}
    .muted {{ color:#6b7280; }}
  </style>
  <script>function doPrint(){{ setTimeout(()=>window.print(), 200) }}</script>
</head>
<body onload='doPrint()'>
  <div class='header'>
    <div>
      <div class='title'>Invoice #{order.id}</div>
      <div class='muted'>Date: {(order.created_at or datetime.utcnow()).strftime('%Y-%m-%d %H:%M')}</div>
      <div class='muted'>Customer: {user.name if user else order.user_id}</div>
      <div class='muted'>Payment: <span class='badge {order.payment_status or ''}'>{(order.payment_status or '').upper()}</span> · Method: {order.payment_method or '-'}</div>
      <div class='muted'>Reference: {order.payment_reference or '-'}</div>
    </div>
    <div>
      <div><strong>Ship To</strong></div>
      <div class='muted'>{shipping.get('name','')}</div>
      <div class='muted'>{shipping.get('phone','')}</div>
      <div class='muted'>{', '.join([x for x in [shipping.get('address1',''), shipping.get('address2','')] if x])}</div>
      <div class='muted'>{', '.join([x for x in [shipping.get('city',''), shipping.get('region',''), shipping.get('postal','')] if x])}</div>
    </div>
  </div>

  <table>
    <thead><tr><th>Item</th><th style='text-align:center'>Qty</th><th style='text-align:right'>Price</th><th style='text-align:right'>Total</th></tr></thead>
    <tbody>
      {''.join(rows_html)}
    </tbody>
  </table>
  <div class='totals'>
    <div>Subtotal: {subtotal:.2f} ETB</div>
    <div><strong>Grand Total: {float(order.total_amount or subtotal):.2f} ETB</strong></div>
  </div>
</body>
</html>
"""
        resp = make_response(html)
        resp.headers['Content-Type'] = 'text/html; charset=utf-8'
        return resp
    except Exception as e:
        return jsonify({'error': f'Failed to generate invoice: {e}'}), 500

# ----------------------
# Admin Orders Listing
# ----------------------

@app.get('/admin/orders')
def admin_list_orders():
    """List recent orders with payment details and items for the admin dashboard.
    Query params: range=30d, status=(optional)
    """
    try:
        rng = (request.args.get('range') or '30d').lower()
        status_filter = (request.args.get('status') or '').strip().lower()
        days = 30
        if rng.endswith('d'):
            try: days = int(rng[:-1])
            except: days = 30
        start = datetime.utcnow() - timedelta(days=days)

        q = Order.query.filter(Order.created_at >= start)
        if status_filter:
            q = q.filter((Order.status == status_filter) | (Order.payment_status == status_filter))
        q = q.order_by(Order.created_at.desc())

        orders = []
        for o in q.limit(200).all():
            items = []
            for oi in OrderItem.query.filter_by(order_id=o.id).all():
                product = Product.query.get(oi.product_id)
                items.append({
                    'id': oi.id,
                    'product_id': oi.product_id,
                    'product_name': product.name if product else 'Unknown',
                    'vendor_id': product.vendor_id if product else None,
                    'quantity': oi.quantity,
                    'price': oi.price,
                    'line_total': float(oi.price or 0.0) * float(oi.quantity or 0),
                })
            orders.append({
                'id': o.id,
                'user_id': o.user_id,
                'total_amount': o.total_amount,
                'status': o.status,
                'payment_status': o.payment_status,
                'payment_method': o.payment_method,
                'payment_reference': o.payment_reference,
                'created_at': o.created_at.isoformat() if o.created_at else None,
                'updated_at': o.updated_at.isoformat() if o.updated_at else None,
                'items': items,
            })
        return jsonify(orders)
    except Exception as e:
        return jsonify({'error': f'Failed to load orders: {e}'}), 500

@app.put('/admin/categories')
def put_admin_categories():
    try:
        data = request.get_json() or []
        if not isinstance(data, list):
            return jsonify({'error': 'Categories must be a list'}), 400
        instance_dir = Path(app.instance_path)
        instance_dir.mkdir(parents=True, exist_ok=True)
        path = instance_dir / 'admin_categories.json'
        with path.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': f'Failed to save categories: {e}'}), 500

@app.post('/auth/send-test-email')
def send_test_email():
    try:
        payload = request.get_json() or {}
        email_settings = payload.get('settings') or {}

        # Temporarily reconfigure mail with provided settings
        app.config['MAIL_SERVER'] = email_settings.get('host') or app.config['MAIL_SERVER']
        app.config['MAIL_PORT'] = int(email_settings.get('port') or app.config['MAIL_PORT'])
        app.config['MAIL_USE_TLS'] = bool(email_settings.get('useTLS'))
        app.config['MAIL_USE_SSL'] = bool(email_settings.get('useSSL'))
        app.config['MAIL_USERNAME'] = email_settings.get('username') or app.config['MAIL_USERNAME']
        # Note: MAIL_PASSWORD should be set in env for security

        recipient = email_settings.get('from') or ADMIN_EMAIL
        msg = Message(
            subject='Admin Settings Test Email',
            sender=email_settings.get('from') or app.config['MAIL_USERNAME'] or 'no-reply@example.com',
            recipients=[recipient],
            body='This is a test email from your AfraShop admin settings.'
        )
        send_mail_background(msg)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': f'Failed to send test email: {e}'}), 500

# User Profile Management Endpoints
@app.put('/users/<int:user_id>')
def update_user_profile(user_id):
    """Update user profile information"""
    try:
        data = request.get_json() or {}
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update fields if provided
        if 'first_name' in data:
            user.first_name = data['first_name'].strip()
        if 'last_name' in data:
            user.last_name = data['last_name'].strip()
        if 'email' in data:
            email = data['email'].strip().lower()
            # Check if email is already taken by another user
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'error': 'Email already in use'}), 400
            user.email = email
        
        user.name = f"{user.first_name} {user.last_name}"
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'name': user.name,
            'email': user.email,
            'role': user.role
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update profile: {e}'}), 500

@app.put('/users/<int:user_id>/password')
def update_user_password(user_id):
    """Update user password"""
    try:
        data = request.get_json() or {}
        current_password = data.get('current')
        new_password = data.get('new')
        
        if not all([current_password, new_password]):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify current password
        if not check_password_hash(user.password_hash, current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Update password
        user.password_hash = generate_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Password updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update password: {e}'}), 500

@app.put('/users/<int:user_id>/notifications')
def update_user_notifications(user_id):
    """Update user notification preferences"""
    try:
        data = request.get_json() or {}
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Store notification preferences in user data or separate table
        # For now, we'll store as JSON in a field (you might want to create a separate table)
        user.notification_preferences = json.dumps(data)
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Notification preferences updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update notifications: {e}'}), 500

@app.put('/users/<int:user_id>/privacy')
def update_user_privacy(user_id):
    """Update user privacy settings"""
    try:
        data = request.get_json() or {}
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Store privacy preferences
        user.privacy_preferences = json.dumps(data)
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Privacy settings updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update privacy settings: {e}'}), 500

@app.delete('/users/<int:user_id>')
def delete_user_account(user_id):
    """Delete user account"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Delete related data (orders, addresses, etc.)
        # Note: You might want to soft delete instead of hard delete
        Order.query.filter_by(user_id=user_id).delete()
        Refund.query.filter_by(user_id=user_id).delete()
        
        # Delete user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'Account deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete account: {e}'}), 500

# Address Management Endpoints
@app.get('/users/<int:user_id>/addresses')
def get_user_addresses(user_id):
    """Get user addresses"""
    try:
        # For now, return empty array - you can implement address storage
        # This would typically involve a separate Address model
        return jsonify([])
    except Exception as e:
        return jsonify({'error': f'Failed to get addresses: {e}'}), 500

@app.post('/users/<int:user_id>/addresses')
def create_user_address(user_id):
    """Create new address for user"""
    try:
        data = request.get_json() or {}
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # For now, return the data as if it was saved
        # In a real implementation, you'd create an Address model
        address = {
            'id': len(data) + 1,  # Simple ID generation
            'user_id': user_id,
            'name': data.get('name', ''),
            'street': data.get('street', ''),
            'city': data.get('city', ''),
            'state': data.get('state', ''),
            'postal_code': data.get('postal_code', ''),
            'country': data.get('country', ''),
            'phone': data.get('phone', ''),
            'is_default': False
        }
        
        return jsonify(address), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to create address: {e}'}), 500

@app.put('/users/<int:user_id>/addresses/<int:address_id>')
def update_user_address(user_id, address_id):
    """Update user address"""
    try:
        data = request.get_json() or {}
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # For now, return the updated data
        # In a real implementation, you'd update the Address model
        address = {
            'id': address_id,
            'user_id': user_id,
            'name': data.get('name', ''),
            'street': data.get('street', ''),
            'city': data.get('city', ''),
            'state': data.get('state', ''),
            'postal_code': data.get('postal_code', ''),
            'country': data.get('country', ''),
            'phone': data.get('phone', ''),
            'is_default': False
        }
        
        return jsonify(address)
        
    except Exception as e:
        return jsonify({'error': f'Failed to update address: {e}'}), 500

@app.delete('/users/<int:user_id>/addresses/<int:address_id>')
def delete_user_address(user_id, address_id):
    """Delete user address"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # In a real implementation, you'd delete from Address model
        return jsonify({'message': 'Address deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': f'Failed to delete address: {e}'}), 500

@app.put('/users/<int:user_id>/addresses/<int:address_id>/default')
def set_default_address(user_id, address_id):
    """Set address as default"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # In a real implementation, you'd update the Address model
        return jsonify({'message': 'Default address updated successfully'})
        
    except Exception as e:
        return jsonify({'error': f'Failed to set default address: {e}'}), 500

# ----------------------
# Analytics & Admin Orders
# ----------------------

@app.get('/api/analytics/orders_summary')
def analytics_orders_summary():
    """Return order counters: total, pending, completed, cancelled, paid, failed."""
    try:
        total = db.session.query(db.func.count(Order.id)).scalar() or 0
        pending = db.session.query(db.func.count(Order.id)).filter(Order.status == 'pending').scalar() or 0
        # Treat confirmed (paid) as completed for dashboard purposes
        completed = db.session.query(db.func.count(Order.id)).filter(
            db.or_(Order.status.in_(['confirmed','completed']), Order.payment_status == 'paid')
        ).scalar() or 0
        cancelled = db.session.query(db.func.count(Order.id)).filter(Order.status == 'cancelled').scalar() or 0
        paid = db.session.query(db.func.count(Order.id)).filter(Order.payment_status == 'paid').scalar() or 0
        failed = db.session.query(db.func.count(Order.id)).filter(Order.payment_status == 'failed').scalar() or 0
        return jsonify({
            'total': total,
            'pending': pending,
            'completed': completed,
            'cancelled': cancelled,
            'paid': paid,
            'failed': failed,
        })
    except Exception as e:
        return jsonify({'error': f'Failed to load summary: {e}'}), 500

@app.get('/api/analytics/sales_over_time')
def analytics_sales_over_time():
    """Return daily totals for last N days. Query: days=30, metric=amount|count"""
    try:
        days = int(request.args.get('days') or 30)
        metric = (request.args.get('metric') or 'amount').lower()
        cutoff = datetime.utcnow() - timedelta(days=days)
        rows = db.session.query(
            db.func.date(Order.created_at).label('day'),
            db.func.sum(Order.total_amount).label('amount'),
            db.func.count(Order.id).label('count')
        ).filter(Order.created_at >= cutoff).group_by(db.func.date(Order.created_at)).order_by(db.func.date(Order.created_at)).all()
        labels = []
        values = []
        for day, amount, count in rows:
            labels.append(str(day))
            values.append(float(amount or 0) if metric == 'amount' else int(count or 0))
        return jsonify({'labels': labels, 'values': values, 'metric': metric})
    except Exception as e:
        return jsonify({'error': f'Failed to load sales: {e}'}), 500

@app.get('/api/analytics/top_categories')
def analytics_top_categories():
    """Top categories by order count."""
    try:
        q = db.session.query(
            Product.category.label('category'),
            db.func.count(OrderItem.id).label('orders')
        ).join(Product, OrderItem.product_id == Product.id).join(Order, OrderItem.order_id == Order.id).group_by(Product.category).order_by(db.func.count(OrderItem.id).desc()).limit(10)
        rows = q.all()
        return jsonify([{'category': c or 'Uncategorized', 'orders': int(n or 0)} for c, n in rows])
    except Exception as e:
        return jsonify({'error': f'Failed to load categories: {e}'}), 500

@app.get('/admin/orders')
def admin_orders_list():
    """List recent orders for admin. Query: range=30d|7d|1d, limit=50"""
    try:
        rng = (request.args.get('range') or '30d').lower()
        limit = min(int(request.args.get('limit') or 50), 200)
        days = 30
        if rng.endswith('d'):
            try: days = int(rng[:-1])
            except Exception: days = 30
        cutoff = datetime.utcnow() - timedelta(days=days)
        orders = Order.query.filter(Order.created_at >= cutoff).order_by(Order.created_at.desc()).limit(limit).all()
        out = []
        for o in orders:
            out.append({
                'id': o.id,
                'user_id': o.user_id,
                'total_amount': o.total_amount,
                'status': o.status,
                'payment_status': o.payment_status,
                'payment_method': o.payment_method,
                'payment_reference': o.payment_reference,
                'receipt_url': o.receipt_url,
                'created_at': o.created_at.isoformat() if o.created_at else None
            })
        return jsonify(out)
    except Exception as e:
        return jsonify({'error': f'Failed to load orders: {e}'}), 500

@app.get('/vendors/<int:vendor_id>/orders')
def vendor_orders(vendor_id: int):
    """List orders scoped to a specific vendor by joining order_items and products."""
    try:
        q = db.session.query(
            OrderItem, Order, Product
        ).join(Order, OrderItem.order_id == Order.id).join(Product, OrderItem.product_id == Product.id).filter(Product.vendor_id == vendor_id).order_by(Order.created_at.desc()).limit(200)
        rows = q.all()
        out = []
        for oi, o, p in rows:
            out.append({
                'order_id': o.id,
                'product_id': oi.product_id,
                'product_name': p.name,
                'quantity': oi.quantity,
                'price': oi.price,
                'status': o.status,
                'payment_status': o.payment_status,
                'created_at': o.created_at.isoformat() if o.created_at else None
            })
        return jsonify(out)
    except Exception as e:
        return jsonify({'error': f'Failed to load vendor orders: {e}'}), 500

if __name__ == '__main__':
    with app.app_context():
        # Just create tables without dropping
        db.create_all()
        print("Database tables created successfully!")
    app.run(host=HOST, port=PORT, debug=DEBUG)
