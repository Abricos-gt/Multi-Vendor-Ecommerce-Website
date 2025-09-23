import os
import secrets
import json
import requests
import uuid
from flask_mail import Mail, Message
import threading
import requests as _requests
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, redirect, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import psycopg2
from config import DATABASE_URL, ADMIN_EMAIL, ADMIN_PASSWORD, CORS_ORIGINS, DEBUG, HOST, PORT

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Routes
@app.get('/')
def root_index():
    return jsonify({'ok': True, 'service': 'backend'})

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

    if not all([first_name, last_name, email, password]):
        return jsonify({'error': 'All fields are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    # All users need email verification
    account_status = 'pending_verification'
    email_verified = False

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

    # Generate verification token and send email
    verification_token = secrets.token_urlsafe(32)
    verification_expires = datetime.utcnow() + timedelta(hours=24)
    
    user.verification_token = verification_token
    user.verification_expires = verification_expires
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host=HOST, port=PORT, debug=DEBUG)
