from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import bcrypt
import hashlib

# Create db instance - will be initialized by app
db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    otp_verified = db.Column(db.Boolean, default=False, nullable=False)
    otp_code = db.Column(db.String(6), nullable=True)
    otp_created_at = db.Column(db.DateTime, nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    api_keys = db.relationship('ApiKey', backref='owner', lazy=True, cascade='all, delete-orphan')
    login_history = db.relationship('LoginHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def set_otp(self, otp_code):
        """Set OTP code and timestamp"""
        self.otp_code = otp_code
        self.otp_created_at = datetime.utcnow()
    
    def verify_otp(self, otp_code):
        """Verify OTP code and expiry"""
        if not self.otp_code or not self.otp_created_at:
            return False
        
        # Check if OTP has expired (10 minutes)
        time_diff = datetime.utcnow() - self.otp_created_at
        if time_diff.total_seconds() > 600:  # 10 minutes
            return False
        
        return self.otp_code == otp_code
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'otp_verified': self.otp_verified,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class ApiKey(db.Model):
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    key_hash = db.Column(db.String(256), nullable=False, unique=True)
    key_preview = db.Column(db.String(20), nullable=False)  # First 16 chars for display
    name = db.Column(db.String(100), nullable=True)  # Optional key name
    status = db.Column(db.String(20), default='active', nullable=False)  # active, inactive, revoked
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)
    last_used = db.Column(db.DateTime, nullable=True)
    usage_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Relationships
    usage_logs = db.relationship('ApiUsage', backref='api_key', lazy=True, cascade='all, delete-orphan')
    
    def set_key_hash(self, raw_key):
        """Hash the API key"""
        import hashlib
        self.key_hash = hashlib.sha256(raw_key.encode('utf-8')).hexdigest()
        self.key_preview = raw_key[:16] + '...'
    
    def verify_key(self, raw_key):
        """Verify if provided key matches hash"""
        import hashlib
        return self.key_hash == hashlib.sha256(raw_key.encode('utf-8')).hexdigest()
    
    def is_valid(self):
        """Check if key is valid (active and not expired)"""
        if self.status != 'active':
            return False
        
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        
        return True
    
    def record_usage(self, endpoint, status='success'):
        """Record API key usage"""
        self.last_used = datetime.utcnow()
        self.usage_count += 1
        
        usage_log = ApiUsage(
            key_id=self.id,
            endpoint=endpoint,
            status=status,
            timestamp=datetime.utcnow()
        )
        db.session.add(usage_log)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'key_preview': self.key_preview,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'usage_count': self.usage_count
        }

class ApiUsage(db.Model):
    __tablename__ = 'api_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    key_id = db.Column(db.Integer, db.ForeignKey('api_keys.id'), nullable=False)
    endpoint = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # success, failure, invalid_key, expired
    ip_address = db.Column(db.String(45), nullable=True)  # Support IPv6
    user_agent = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'key_id': self.key_id,
            'endpoint': self.endpoint,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'status': self.status,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }

class LoginHistory(db.Model):
    __tablename__ = 'login_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.Text, nullable=True)
    success = db.Column(db.Boolean, default=True, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'success': self.success
        }