import os
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from config import *


db = SQLAlchemy()


def send_password_reset_email(to_email, reset_url, user_name):
    """Send password reset email to user"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = "Password Reset Request - Afra Shop"
        
        # Email body
        body = f"""
        Hello {user_name},
        
        You have requested to reset your password for your Afra Shop account.
        
        Click the link below to reset your password:
        {reset_url}
        
        This link will expire in 1 hour for security reasons.
        
        If you didn't request this password reset, please ignore this email.
        
        Best regards,
        Afra Shop Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, to_email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_email_verification(to_email, verification_url, user_name):
    """Send email verification email to user"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = "Email Verification Required - Afra Shop"
        
        # Email body
        body = f"""
        Hello {user_name},
        
        Thank you for registering as a vendor on Afra Shop!
        
        To complete your vendor application, please verify your email address by clicking the link below:
        {verification_url}
        
        This link will expire in 24 hours for security reasons.
        
        If you didn't register for a vendor account, please ignore this email.
        
        Best regards,
        Afra Shop Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, to_email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Failed to send verification email: {e}")
        return False


def cleanup_expired_tokens():
    """Clean up expired password reset and email verification tokens"""
    try:
        # Clean up expired password reset tokens
        expired_reset_tokens = PasswordResetToken.query.filter(
            PasswordResetToken.expires_at < datetime.utcnow()
        ).all()
        
        for token in expired_reset_tokens:
            db.session.delete(token)
        
        if expired_reset_tokens:
            print(f"Cleaned up {len(expired_reset_tokens)} expired password reset tokens")
        
        # Clean up expired email verification tokens
        try:
            expired_verification_tokens = EmailVerificationToken.query.filter(
                EmailVerificationToken.expires_at < datetime.utcnow()
            ).all()
            
            for token in expired_verification_tokens:
                db.session.delete(token)
            
            if expired_verification_tokens:
                print(f"Cleaned up {len(expired_verification_tokens)} expired email verification tokens")
                
        except Exception as e:
            # EmailVerificationToken table might not exist yet
            print(f"Email verification token cleanup skipped: {e}")
        
        if expired_reset_tokens or (expired_verification_tokens if 'expired_verification_tokens' in locals() else False):
            db.session.commit()
            
    except Exception as e:
        print(f"Failed to cleanup expired tokens: {e}")
        db.session.rollback()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(
        app,
        resources={r"/*": {"origins": CORS_ORIGINS}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    db.init_app(app)

    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("Database tables created/updated successfully")
            
            # Check if email_verified column exists in VendorApplication table
            try:
                # Try to add the email_verified column if it doesn't exist
                with db.engine.connect() as conn:
                    # Check if column exists
                    result = conn.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'vendor_application' 
                        AND column_name = 'email_verified'
                    """)
                    
                    if not result.fetchone():
                        # Add the column if it doesn't exist
                        conn.execute("ALTER TABLE vendor_application ADD COLUMN email_verified BOOLEAN DEFAULT FALSE")
                        print("Added email_verified column to vendor_application table")
                    else:
                        print("email_verified column already exists")
                        
            except Exception as e:
                print(f"Database schema update warning: {e}")
                # Continue anyway - the column might already exist
                
        except Exception as e:
            print(f"Critical database initialization error: {e}")
            raise e

    register_routes(app)
    return app


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=True)
    last_name = db.Column(db.String(120), nullable=True)
    name = db.Column(db.String(240), nullable=True)  # deprecated, kept for compatibility
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default='user')  # user | vendor | admin
    password_hash = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class VendorApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    license_url = db.Column(db.Text, nullable=False)
    id_card_url = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending | approved | rejected
    email_verified = db.Column(db.Boolean, default=False)  # New field for email verification
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # price at purchase time


class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class EmailVerificationToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def register_routes(app: Flask):
    @app.errorhandler(500)
    def handle_500(e):
        return jsonify({'error': 'internal_server_error'}), 500
    @app.get('/health')
    def health():
        try:
            # Test database connection
            db.session.execute('SELECT 1')
            db_status = 'connected'
        except Exception as e:
            print(f"Database health check failed: {e}")
            db_status = 'error'
            return jsonify({'ok': False, 'database': db_status, 'error': str(e)}), 500
        
        try:
            # Clean up expired tokens on health check
            cleanup_expired_tokens()
            cleanup_status = 'success'
        except Exception as e:
            print(f"Token cleanup failed: {e}")
            cleanup_status = 'error'
        
        return jsonify({
            'ok': True, 
            'database': db_status,
            'token_cleanup': cleanup_status,
            'timestamp': datetime.utcnow().isoformat()
        })

    # Auth (very basic demo)
    @app.post('/auth/register')
    def register_user():
        try:
            data = request.get_json() or {}
            print(f"Registration data received: {data}")  # Debug log
            
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            password = data.get('password')
            
            # Validate required fields
            missing_fields = []
            if not first_name or not first_name.strip():
                missing_fields.append('first_name')
            if not last_name or not last_name.strip():
                missing_fields.append('last_name')
            if not email or not email.strip():
                missing_fields.append('email')
            if not password:
                missing_fields.append('password')
            
            if missing_fields:
                return jsonify({
                    'error': f'Missing required fields: {", ".join(missing_fields)}',
                    'received_data': data
                }), 400
            
            # Check if email already exists
            if User.query.filter_by(email=email.strip()).first():
                return jsonify({'error': 'email already exists'}), 400
            
            # Create user
            user = User(
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                name=f"{first_name.strip()} {last_name.strip()}",
                email=email.strip(),
                role='user',
                password_hash=generate_password_hash(password)
            )
            db.session.add(user)
            db.session.commit()
            
            print(f"User created successfully: {user.id}")  # Debug log
            return jsonify({
                'id': user.id, 
                'first_name': user.first_name, 
                'last_name': user.last_name, 
                'email': user.email, 
                'role': user.role
            })
            
        except Exception as ex:
            db.session.rollback()
            print(f"Registration error: {ex}")  # Debug log
            return jsonify({'error': 'registration_failed', 'detail': str(ex)}), 500

    @app.post('/auth/login')
    def login():
        data = request.get_json() or {}
        email = (data.get('email') or '').strip()
        password = data.get('password') or ''
        if not email or not password:
            return jsonify({'error': 'email and password required'}), 400
        user = User.query.filter_by(email=email).first()
        # Bootstrap or reconcile admin if matching configured credentials
        if email.lower() == ADMIN_EMAIL.lower() and password == ADMIN_PASSWORD:
            if not user:
                user = User(first_name='Admin', last_name='User', name='Admin', email=ADMIN_EMAIL, role='admin', password_hash=generate_password_hash(ADMIN_PASSWORD))
                db.session.add(user)
                db.session.commit()
            else:
                # Ensure admin role and reset password to configured admin password
                user.role = 'admin'
                user.password_hash = generate_password_hash(ADMIN_PASSWORD)
                db.session.commit()
            return jsonify({'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'role': user.role})
        # Normal users
        if not user or not user.password_hash or not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'invalid credentials'}), 401
        return jsonify({'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'role': user.role})

    @app.post('/auth/forgot-password')
    def forgot_password():
        data = request.get_json() or {}
        email = (data.get('email') or '').strip()
        if not email:
            return jsonify({'error': 'email required'}), 400
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            # Don't reveal if email exists or not for security
            return jsonify({'message': 'If an account with that email exists, a password reset link has been sent'}), 200
        
        # Check if there's already a recent token (within last 5 minutes)
        recent_token = PasswordResetToken.query.filter_by(user_id=user.id).first()
        if recent_token and recent_token.created_at > datetime.utcnow() - timedelta(minutes=5):
            return jsonify({'error': 'Please wait a few minutes before requesting another reset link'}), 429
        
        # Clean up expired tokens before creating new ones
        cleanup_expired_tokens()
        
        # Generate unique token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Remove any existing tokens for this user
        PasswordResetToken.query.filter_by(user_id=user.id).delete()
        
        # Create new token
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        db.session.add(reset_token)
        db.session.commit()
        
        # Send email with reset link
        # Use a proper URL format that will work in emails
        base_url = request.headers.get('Origin', 'http://localhost:3000')
        reset_url = f"{base_url}/#/reset-password?token={token}"
        user_name = f"{user.first_name} {user.last_name}"
        
        email_sent = send_password_reset_email(user.email, reset_url, user_name)
        
        if email_sent:
            return jsonify({
                'message': 'Password reset link has been sent to your email',
                'reset_url': reset_url,
                'expires_at': expires_at.isoformat()
            })
        else:
            # If email fails, return error with the reset link for manual use
            print(f"Failed to send email to {user.email}")
            return jsonify({
                'message': 'Password reset link generated but email delivery failed. You can use the link below manually.',
                'reset_url': reset_url,
                'expires_at': expires_at.isoformat(),
                'email_failed': True
            })

    @app.post('/auth/reset-password')
    def reset_password():
        data = request.get_json() or {}
        token = data.get('token')
        new_password = data.get('new_password')
        
        if not token or not new_password:
            return jsonify({'error': 'token and new_password required'}), 400
        
        # Validate password strength
        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Find valid token
        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        if not reset_token:
            return jsonify({'error': 'invalid or expired token'}), 400
        
        if reset_token.expires_at < datetime.utcnow():
            # Clean up expired token
            db.session.delete(reset_token)
            db.session.commit()
            return jsonify({'error': 'token expired'}), 400
        
        # Update user password
        user = User.query.get(reset_token.user_id)
        if not user:
            return jsonify({'error': 'user not found'}), 400
        
        # Check if new password is different from current
        if check_password_hash(user.password_hash, new_password):
            return jsonify({'error': 'New password must be different from current password'}), 400
        
        user.password_hash = generate_password_hash(new_password)
        
        # Remove the used token
        db.session.delete(reset_token)
        db.session.commit()
        
        return jsonify({'message': 'Password updated successfully'})

    @app.post('/auth/verify-email')
    def verify_email():
        data = request.get_json() or {}
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'token required'}), 400
        
        # Find valid token
        verification_token = EmailVerificationToken.query.filter_by(token=token).first()
        if not verification_token:
            return jsonify({'error': 'invalid or expired token'}), 400
        
        if verification_token.expires_at < datetime.utcnow():
            # Clean up expired token
            db.session.delete(verification_token)
            db.session.commit()
            return jsonify({'error': 'token expired'}), 400
        
        # Mark vendor application as email verified
        vendor_app = VendorApplication.query.filter_by(user_id=verification_token.user_id).first()
        if not vendor_app:
            return jsonify({'error': 'vendor application not found'}), 404
        
        # Try to set email_verified, but handle case where column might not exist
        try:
            vendor_app.email_verified = True
        except AttributeError:
            # Column doesn't exist yet, skip this field
            pass
        
        # Remove the used token
        db.session.delete(verification_token)
        db.session.commit()
        
        return jsonify({
            'message': 'Email verified successfully! Your vendor application is now under review.',
            'vendor_application_id': vendor_app.id
        })

    @app.post('/auth/admin')
    def sign_in_admin():
        # Dev convenience: create or fetch a single admin
        email = ADMIN_EMAIL
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(first_name='Admin', last_name='User', name='Admin', email=email, role='admin', password_hash=generate_password_hash(ADMIN_PASSWORD))
            db.session.add(user)
            db.session.commit()
        return jsonify({'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'role': user.role})

    # Vendor applications
    @app.post('/vendors/apply')
    def apply_vendor():
        try:
            data = request.get_json() or {}
            print(f"Vendor application data received: {data}")  # Debug log
            
            user_id = data.get('user_id')
            license_url = data.get('license_url')
            id_card_url = data.get('id_card_url')
            
            # Validate required fields
            missing_fields = []
            if not user_id:
                missing_fields.append('user_id')
            if not license_url:
                missing_fields.append('license_url')
            if not id_card_url:
                missing_fields.append('id_card_url')
            
            if missing_fields:
                return jsonify({
                    'error': f'Missing required fields: {", ".join(missing_fields)}',
                    'received_data': data
                }), 400
            
            # Get user details
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'user not found'}), 404
        
            app_row = VendorApplication.query.filter_by(user_id=user_id).first()
            if app_row:
                app_row.license_url = license_url
                app_row.id_card_url = id_card_url
                app_row.status = 'pending'
                # Try to set email_verified, but handle case where column might not exist
                try:
                    app_row.email_verified = False
                except AttributeError:
                    # Column doesn't exist yet, skip this field
                    pass
            else:
                try:
                    app_row = VendorApplication(
                        user_id=user_id, 
                        license_url=license_url, 
                        id_card_url=id_card_url, 
                        status='pending',
                        email_verified=False
                    )
                except TypeError:
                    # Fallback if email_verified column doesn't exist
                    app_row = VendorApplication(
                        user_id=user_id, 
                        license_url=license_url, 
                        id_card_url=id_card_url, 
                        status='pending'
                    )
                db.session.add(app_row)
            
            db.session.commit()
            
            # Generate verification token
            token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            # Remove any existing verification tokens for this user
            EmailVerificationToken.query.filter_by(user_id=user_id).delete()
            
            # Create new verification token
            verification_token = EmailVerificationToken(
                user_id=user_id,
                token=token,
                expires_at=expires_at
            )
            db.session.add(verification_token)
            db.session.commit()
            
            # Send verification email
            base_url = request.headers.get('Origin', 'http://localhost:3000')
            verification_url = f"{base_url}/#/verify-email?token={token}"
            user_name = f"{user.first_name} {user.last_name}"
            
            email_sent = send_email_verification(user.email, verification_url, user_name)
            
            if email_sent:
                print(f"Vendor application submitted successfully: {app_row.id}")  # Debug log
                return jsonify({
                    'id': app_row.id, 
                    'status': app_row.status,
                    'message': 'Vendor application submitted! Please check your email to verify your address.',
                    'verification_required': True
                })
            else:
                print(f"Vendor application submitted but email failed: {app_row.id}")  # Debug log
                return jsonify({
                    'id': app_row.id, 
                    'status': app_row.status,
                    'message': 'Vendor application submitted but verification email failed to send.',
                    'verification_required': True,
                    'email_failed': True
                })
        except Exception as e:
            db.session.rollback()
            print(f"Vendor application error: {e}")  # Debug log
            return jsonify({'error': 'vendor_application_failed', 'detail': str(e)}), 500

    @app.get('/vendors/applications')
    def list_vendor_apps():
        apps = VendorApplication.query.order_by(VendorApplication.created_at.desc()).all()
        return jsonify([
            {
                'id': a.id,
                'user_id': a.user_id,
                'license_url': a.license_url,
                'id_card_url': a.id_card_url,
                'status': a.status,
                'email_verified': getattr(a, 'email_verified', False),  # Safe access with fallback
                'created_at': a.created_at.isoformat()
            } for a in apps
        ])

    @app.post('/vendors/applications/<int:application_id>/status')
    def set_vendor_status(application_id: int):
        data = request.get_json() or {}
        status = data.get('status')
        if status not in ['pending', 'approved', 'rejected']:
            return jsonify({'error': 'invalid status'}), 400
        
        app_row = VendorApplication.query.get_or_404(application_id)
        
        # Check if email is verified before allowing approval (if column exists)
        try:
            if status == 'approved' and not app_row.email_verified:
                return jsonify({'error': 'Cannot approve vendor application: email not verified'}), 400
        except AttributeError:
            # email_verified column doesn't exist yet, allow approval
            pass
        
        app_row.status = status
        if status == 'approved':
            user = User.query.get(app_row.user_id)
            if user:
                user.role = 'vendor'
        
        db.session.commit()
        return jsonify({'id': app_row.id, 'status': app_row.status})

    # Products
    @app.post('/products')
    def create_product():
        data = request.get_json() or {}
        vendor_user_id = data.get('vendor_user_id')
        name = data.get('name')
        description = data.get('description')
        price = float(data.get('price') or 0)
        image_url = data.get('image_url')
        if not (vendor_user_id and name and description and image_url):
            return jsonify({'error': 'missing fields'}), 400
        p = Product(vendor_user_id=vendor_user_id, name=name, description=description, price=price, image_url=image_url)
        db.session.add(p)
        db.session.commit()
        return jsonify({'id': p.id}), 201

    @app.get('/products')
    def list_products():
        items = Product.query.order_by(Product.created_at.desc()).all()
        return jsonify([
            {
                'id': p.id,
                'vendor_user_id': p.vendor_user_id,
                'name': p.name,
                'description': p.description,
                'price': p.price,
                'image_url': p.image_url,
            } for p in items
        ])

    @app.put('/products/<int:product_id>')
    def update_product(product_id: int):
        data = request.get_json() or {}
        product = Product.query.get_or_404(product_id)
        vendor_user_id = data.get('vendor_user_id')
        if not vendor_user_id or int(vendor_user_id) != int(product.vendor_user_id):
            return jsonify({'error': 'forbidden'}), 403
        name = data.get('name')
        description = data.get('description')
        price = data.get('price')
        image_url = data.get('image_url')
        if name is not None:
            product.name = name
        if description is not None:
            product.description = description
        if price is not None:
            try:
                product.price = float(price)
            except Exception:
                return jsonify({'error': 'invalid price'}), 400
        if image_url is not None and image_url != '':
            product.image_url = image_url
        db.session.commit()
        return jsonify({'id': product.id})

    @app.delete('/products/<int:product_id>')
    def delete_product(product_id: int):
        data = request.get_json(silent=True) or {}
        product = Product.query.get_or_404(product_id)
        # Allow either matching vendor id or explicit admin override via 'force'
        vendor_user_id = data.get('vendor_user_id')
        force = bool(data.get('force'))
        if not force:
            try:
                if not vendor_user_id or int(vendor_user_id) != int(product.vendor_user_id):
                    return jsonify({'error': 'forbidden'}), 403
            except Exception:
                return jsonify({'error': 'invalid vendor_user_id'}), 400
        # Remove dependent order items first to avoid FK violations
        try:
            db.session.query(OrderItem).filter_by(product_id=product.id).delete(synchronize_session=False)
            db.session.delete(product)
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            return jsonify({'error': 'delete_failed', 'detail': str(ex)}), 500
        return jsonify({'deleted': True})

    # Orders (basic)
    @app.post('/orders')
    def create_order():
        data = request.get_json() or {}
        user_id = data.get('user_id')
        items = data.get('items') or []  # [{product_id, quantity}]
        if not user_id or not items:
            return jsonify({'error': 'user_id and items required'}), 400
        order = Order(user_id=user_id, total=0)
        db.session.add(order)
        total = 0
        for i in items:
            product = Product.query.get(i.get('product_id'))
            qty = int(i.get('quantity') or 1)
            if not product:
                continue
            line_total = product.price * qty
            total += line_total
            db.session.add(OrderItem(order_id=order.id, product_id=product.id, quantity=qty, price=product.price))
        order.total = total
        db.session.commit()
        return jsonify({'id': order.id, 'total': order.total}), 201

    @app.get('/orders')
    def list_orders():
        orders = Order.query.order_by(Order.created_at.desc()).all()
        return jsonify([
            {
                'id': o.id,
                'user_id': o.user_id,
                'total': o.total,
                'created_at': o.created_at.isoformat()
            } for o in orders
        ])

    @app.get('/vendors/<int:vendor_id>/orders')
    def get_vendor_orders(vendor_id: int):
        """Get all orders that contain products from a specific vendor"""
        try:
            # Get all products from this vendor
            vendor_products = Product.query.filter_by(vendor_user_id=vendor_id).all()
            product_ids = [p.id for p in vendor_products]
            
            if not product_ids:
                return jsonify([])
            
            # Get order items for these products
            order_items = OrderItem.query.filter(OrderItem.product_id.in_(product_ids)).all()
            
            # Group by order and get order details
            orders_data = {}
            for item in order_items:
                order = Order.query.get(item.order_id)
                if order:
                    if order.id not in orders_data:
                        orders_data[order.id] = {
                            'id': order.id,
                            'user_id': order.user_id,
                            'total': 0,
                            'created_at': order.created_at.isoformat(),
                            'items': []
                        }
                    
                    # Get product details
                    product = Product.query.get(item.product_id)
                    if product:
                        orders_data[order.id]['items'].append({
                            'product_id': item.product_id,
                            'product_name': product.name,
                            'quantity': item.quantity,
                            'price': item.price,
                            'line_total': item.quantity * item.price
                        })
                        orders_data[order.id]['total'] += item.quantity * item.price
            
            return jsonify(list(orders_data.values()))
            
        except Exception as e:
            return jsonify({'error': 'failed_to_fetch_orders', 'detail': str(e)}), 500

    # Users
    @app.get('/users/<int:user_id>')
    def get_user(user_id: int):
        try:
            user = User.query.get_or_404(user_id)
            app_row = VendorApplication.query.filter_by(user_id=user.id).first()
            is_vendor = (user.role == 'vendor') or (app_row and app_row.status == 'approved')
            is_admin = user.role == 'admin'
            
            vendor_app_data = None
            if app_row:
                try:
                    vendor_app_data = {
                        'id': app_row.id,
                        'status': app_row.status,
                        'license_url': app_row.license_url,
                        'id_card_url': app_row.id_card_url,
                        'email_verified': getattr(app_row, 'email_verified', False),  # Safe access with fallback
                        'created_at': app_row.created_at.isoformat(),
                    }
                except Exception as e:
                    print(f"Error processing vendor application data: {e}")
                    # Fallback to basic data
                    vendor_app_data = {
                        'id': app_row.id,
                        'status': app_row.status,
                        'license_url': app_row.license_url,
                        'id_card_url': app_row.id_card_url,
                        'email_verified': False,  # Default fallback
                        'created_at': app_row.created_at.isoformat(),
                    }
            
            return jsonify({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'role': user.role,
                'is_vendor': bool(is_vendor),
                'is_admin': bool(is_admin),
                'vendor_application': vendor_app_data
            })
        except Exception as e:
            print(f"Error in get_user route: {e}")
            return jsonify({'error': 'Failed to fetch user data', 'detail': str(e)}), 500


app = create_app()

# Simple root route for connectivity checks
@app.get('/')
def root_index():
    return jsonify({'ok': True, 'service': 'backend'})

if __name__ == '__main__':
    # Use configuration values
    app.run(host=HOST, port=PORT, debug=DEBUG)


