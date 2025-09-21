from functools import wraps
from flask import request, jsonify, current_app, g
from flask_login import current_user
from models import ApiKey, ApiUsage, db
from utils.helpers import get_client_ip
import hashlib

def require_api_key(f):
    """Decorator to require valid API key for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get API key from header
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                'error': 'API key required',
                'message': 'Please provide API key in X-API-Key header'
            }), 401
        
        # Hash the provided key
        key_hash = hashlib.sha256(api_key.encode('utf-8')).hexdigest()
        
        # Find the API key in database
        api_key_obj = ApiKey.query.filter_by(key_hash=key_hash).first()
        
        if not api_key_obj:
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is not valid'
            }), 401
        
        # Check if key is valid (active and not expired)
        if not api_key_obj.is_valid():
            # Log failed usage
            usage_log = ApiUsage(
                key_id=api_key_obj.id,
                endpoint=request.endpoint or request.path,
                status='invalid_key',
                ip_address=get_client_ip(request),
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(usage_log)
            db.session.commit()
            
            return jsonify({
                'error': 'Invalid API key',
                'message': f'API key is {api_key_obj.status}'
            }), 401
        
        # Record successful usage
        api_key_obj.record_usage(
            endpoint=request.endpoint or request.path,
            status='success'
        )
        
        # Add IP and user agent to usage log
        usage_log = ApiUsage.query.filter_by(
            key_id=api_key_obj.id
        ).order_by(ApiUsage.id.desc()).first()
        
        if usage_log:
            usage_log.ip_address = get_client_ip(request)
            usage_log.user_agent = request.headers.get('User-Agent')
        
        db.session.commit()
        
        # Store API key object in g for use in the view function
        g.current_api_key = api_key_obj
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_admin(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        if not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_verified_user(f):
    """Decorator to require verified user"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        if not current_user.otp_verified:
            return jsonify({'error': 'Email verification required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function