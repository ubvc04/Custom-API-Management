from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from models import ApiKey, ApiUsage, db
from utils.helpers import generate_secure_api_key, send_api_key_generated_email
from utils.decorators import require_verified_user
from datetime import datetime, timedelta

api_keys = Blueprint('api_keys', __name__)

@api_keys.route('/generate', methods=['GET', 'POST'])
@login_required
@require_verified_user
def generate_key():
    if request.method == 'GET':
        return render_template('keys/generate.html')
    
    data = request.get_json() if request.is_json else request.form
    key_name = data.get('name', '').strip()
    expires_in_days = data.get('expires_in_days', '').strip()
    
    # Validate expiration
    expires_at = None
    if expires_in_days:
        try:
            days = int(expires_in_days)
            if days <= 0:
                return jsonify({'error': 'Expiration days must be positive'}), 400
            if days > 365:
                return jsonify({'error': 'Maximum expiration is 365 days'}), 400
            expires_at = datetime.utcnow() + timedelta(days=days)
        except ValueError:
            return jsonify({'error': 'Invalid expiration days'}), 400
    
    # Check if user has reached key limit (optional)
    user_key_count = ApiKey.query.filter_by(user_id=current_user.id).count()
    if user_key_count >= 10:  # Limit to 10 keys per user
        return jsonify({'error': 'Maximum number of API keys reached (10)'}), 400
    
    # Generate secure API key
    raw_key = generate_secure_api_key(128)
    
    # Create API key record
    api_key = ApiKey(
        user_id=current_user.id,
        name=key_name or f"API Key {user_key_count + 1}",
        expires_at=expires_at
    )
    api_key.set_key_hash(raw_key)
    
    db.session.add(api_key)
    db.session.commit()
    
    # Send notification email
    from app import mail
    send_api_key_generated_email(mail, current_user.email, api_key.name, api_key.key_preview)
    
    return jsonify({
        'message': 'API key generated successfully!',
        'api_key': raw_key,  # Return raw key only once
        'key_info': api_key.to_dict(),
        'warning': 'Please save this key securely. You will not be able to see it again.'
    }), 201

@api_keys.route('/list')
@login_required
@require_verified_user
def list_keys():
    keys = ApiKey.query.filter_by(user_id=current_user.id).order_by(ApiKey.created_at.desc()).all()
    return jsonify({
        'keys': [key.to_dict() for key in keys]
    }), 200

@api_keys.route('/<int:key_id>')
@login_required
@require_verified_user
def get_key(key_id):
    api_key = ApiKey.query.filter_by(id=key_id, user_id=current_user.id).first()
    if not api_key:
        return jsonify({'error': 'API key not found'}), 404
    
    return jsonify(api_key.to_dict()), 200

@api_keys.route('/<int:key_id>/status', methods=['POST'])
@login_required
@require_verified_user
def update_key_status(key_id):
    api_key = ApiKey.query.filter_by(id=key_id, user_id=current_user.id).first()
    if not api_key:
        return jsonify({'error': 'API key not found'}), 404
    
    data = request.get_json() if request.is_json else request.form
    new_status = data.get('status', '').strip().lower()
    
    if new_status not in ['active', 'inactive', 'revoked']:
        return jsonify({'error': 'Invalid status. Must be active, inactive, or revoked'}), 400
    
    api_key.status = new_status
    db.session.commit()
    
    return jsonify({
        'message': f'API key status updated to {new_status}',
        'key_info': api_key.to_dict()
    }), 200

@api_keys.route('/<int:key_id>/delete', methods=['DELETE', 'POST'])
@login_required
@require_verified_user
def delete_key(key_id):
    api_key = ApiKey.query.filter_by(id=key_id, user_id=current_user.id).first()
    if not api_key:
        return jsonify({'error': 'API key not found'}), 404
    
    # Soft delete by setting status to revoked
    api_key.status = 'revoked'
    db.session.commit()
    
    return jsonify({'message': 'API key deleted successfully'}), 200

@api_keys.route('/<int:key_id>/usage')
@login_required
@require_verified_user
def get_key_usage(key_id):
    api_key = ApiKey.query.filter_by(id=key_id, user_id=current_user.id).first()
    if not api_key:
        return jsonify({'error': 'API key not found'}), 404
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    per_page = min(per_page, 100)  # Limit to 100 records per page
    
    # Get usage logs
    usage_logs = ApiUsage.query.filter_by(key_id=key_id).order_by(
        ApiUsage.timestamp.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return jsonify({
        'usage_logs': [log.to_dict() for log in usage_logs.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': usage_logs.total,
            'pages': usage_logs.pages,
            'has_next': usage_logs.has_next,
            'has_prev': usage_logs.has_prev
        },
        'key_info': api_key.to_dict()
    }), 200

@api_keys.route('/<int:key_id>/regenerate', methods=['POST'])
@login_required
@require_verified_user
def regenerate_key(key_id):
    api_key = ApiKey.query.filter_by(id=key_id, user_id=current_user.id).first()
    if not api_key:
        return jsonify({'error': 'API key not found'}), 404
    
    if api_key.status == 'revoked':
        return jsonify({'error': 'Cannot regenerate revoked key'}), 400
    
    # Generate new secure API key
    raw_key = generate_secure_api_key(128)
    api_key.set_key_hash(raw_key)
    api_key.status = 'active'  # Ensure key is active after regeneration
    api_key.usage_count = 0  # Reset usage count
    api_key.last_used = None  # Reset last used
    
    db.session.commit()
    
    # Send notification email
    from app import mail
    send_api_key_generated_email(mail, current_user.email, api_key.name, api_key.key_preview)
    
    return jsonify({
        'message': 'API key regenerated successfully!',
        'api_key': raw_key,  # Return raw key only once
        'key_info': api_key.to_dict(),
        'warning': 'Please save this key securely. You will not be able to see it again.'
    }), 200

@api_keys.route('/<int:key_id>/update', methods=['POST'])
@login_required
@require_verified_user
def update_key(key_id):
    api_key = ApiKey.query.filter_by(id=key_id, user_id=current_user.id).first()
    if not api_key:
        return jsonify({'error': 'API key not found'}), 404
    
    data = request.get_json() if request.is_json else request.form
    new_name = data.get('name', '').strip()
    expires_in_days = data.get('expires_in_days', '').strip()
    
    # Update name if provided
    if new_name:
        api_key.name = new_name
    
    # Update expiration if provided
    if expires_in_days:
        try:
            days = int(expires_in_days)
            if days <= 0:
                return jsonify({'error': 'Expiration days must be positive'}), 400
            if days > 365:
                return jsonify({'error': 'Maximum expiration is 365 days'}), 400
            api_key.expires_at = datetime.utcnow() + timedelta(days=days)
        except ValueError:
            return jsonify({'error': 'Invalid expiration days'}), 400
    elif expires_in_days == '':  # Remove expiration
        api_key.expires_at = None
    
    db.session.commit()
    
    return jsonify({
        'message': 'API key updated successfully!',
        'key_info': api_key.to_dict()
    }), 200

@api_keys.route('/stats')
@login_required
@require_verified_user
def get_user_stats():
    """Get user's API key statistics"""
    total_keys = ApiKey.query.filter_by(user_id=current_user.id).count()
    active_keys = ApiKey.query.filter_by(user_id=current_user.id, status='active').count()
    inactive_keys = ApiKey.query.filter_by(user_id=current_user.id, status='inactive').count()
    revoked_keys = ApiKey.query.filter_by(user_id=current_user.id, status='revoked').count()
    
    # Get total usage across all user's keys
    total_usage = db.session.query(db.func.sum(ApiKey.usage_count)).filter_by(
        user_id=current_user.id
    ).scalar() or 0
    
    # Get recent usage (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_usage = ApiUsage.query.join(ApiKey).filter(
        ApiKey.user_id == current_user.id,
        ApiUsage.timestamp >= thirty_days_ago
    ).count()
    
    return jsonify({
        'stats': {
            'total_keys': total_keys,
            'active_keys': active_keys,
            'inactive_keys': inactive_keys,
            'revoked_keys': revoked_keys,
            'total_usage': total_usage,
            'recent_usage': recent_usage
        }
    }), 200