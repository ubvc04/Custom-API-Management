from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import User, ApiKey, ApiUsage, LoginHistory, db
from utils.decorators import require_admin
from datetime import datetime, timedelta

admin = Blueprint('admin', __name__)

@admin.route('/')
@login_required
@require_admin
def index():
    """Admin dashboard"""
    return render_template('admin/index.html')

@admin.route('/users')
@login_required
@require_admin
def users():
    """User management page"""
    return render_template('admin/users.html')

@admin.route('/keys')
@login_required
@require_admin
def keys():
    """All API keys management page"""
    return render_template('admin/keys.html')

@admin.route('/analytics')
@login_required
@require_admin
def analytics():
    """Analytics and usage page"""
    return render_template('admin/analytics.html')

@admin.route('/api/stats')
@login_required
@require_admin
def get_admin_stats():
    """Get admin dashboard statistics"""
    # User stats
    total_users = User.query.count()
    verified_users = User.query.filter_by(otp_verified=True).count()
    admin_users = User.query.filter_by(is_admin=True).count()
    
    # API key stats
    total_keys = ApiKey.query.count()
    active_keys = ApiKey.query.filter_by(status='active').count()
    inactive_keys = ApiKey.query.filter_by(status='inactive').count()
    revoked_keys = ApiKey.query.filter_by(status='revoked').count()
    
    # Usage stats
    total_usage = db.session.query(db.func.sum(ApiKey.usage_count)).scalar() or 0
    
    # Recent activity (last 24 hours)
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    recent_usage = ApiUsage.query.filter(ApiUsage.timestamp >= twenty_four_hours_ago).count()
    recent_logins = LoginHistory.query.filter(
        LoginHistory.timestamp >= twenty_four_hours_ago,
        LoginHistory.success == True
    ).count()
    recent_registrations = User.query.filter(User.created_at >= twenty_four_hours_ago).count()
    
    return jsonify({
        'users': {
            'total': total_users,
            'verified': verified_users,
            'admin': admin_users,
            'recent_registrations': recent_registrations
        },
        'api_keys': {
            'total': total_keys,
            'active': active_keys,
            'inactive': inactive_keys,
            'revoked': revoked_keys
        },
        'usage': {
            'total': total_usage,
            'recent': recent_usage,
            'recent_logins': recent_logins
        }
    }), 200

@admin.route('/api/users')
@login_required
@require_admin
def get_all_users():
    """Get all users with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    search = request.args.get('search', '').strip()
    
    query = User.query
    
    if search:
        query = query.filter(
            (User.username.contains(search)) | 
            (User.email.contains(search))
        )
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    users_data = []
    for user in users.items:
        user_data = user.to_dict()
        user_data['api_key_count'] = ApiKey.query.filter_by(user_id=user.id).count()
        user_data['total_usage'] = db.session.query(
            db.func.sum(ApiKey.usage_count)
        ).filter_by(user_id=user.id).scalar() or 0
        users_data.append(user_data)
    
    return jsonify({
        'users': users_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': users.total,
            'pages': users.pages,
            'has_next': users.has_next,
            'has_prev': users.has_prev
        }
    }), 200

@admin.route('/api/users/<int:user_id>')
@login_required
@require_admin
def get_user_details(user_id):
    """Get detailed user information"""
    user = User.query.get_or_404(user_id)
    
    # Get user's API keys
    api_keys = ApiKey.query.filter_by(user_id=user_id).order_by(ApiKey.created_at.desc()).all()
    
    # Get user's login history (last 10)
    login_history = LoginHistory.query.filter_by(user_id=user_id).order_by(
        LoginHistory.timestamp.desc()
    ).limit(10).all()
    
    # Get usage stats
    total_usage = db.session.query(db.func.sum(ApiKey.usage_count)).filter_by(
        user_id=user_id
    ).scalar() or 0
    
    # Recent usage (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_usage = ApiUsage.query.join(ApiKey).filter(
        ApiKey.user_id == user_id,
        ApiUsage.timestamp >= thirty_days_ago
    ).count()
    
    return jsonify({
        'user': user.to_dict(),
        'api_keys': [key.to_dict() for key in api_keys],
        'login_history': [log.to_dict() for log in login_history],
        'stats': {
            'total_usage': total_usage,
            'recent_usage': recent_usage,
            'api_key_count': len(api_keys)
        }
    }), 200

@admin.route('/api/users/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
@require_admin
def toggle_user_admin(user_id):
    """Toggle user admin status"""
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot modify your own admin status'}), 400
    
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    
    return jsonify({
        'message': f'User admin status {"enabled" if user.is_admin else "disabled"}',
        'user': user.to_dict()
    }), 200

@admin.route('/api/users/<int:user_id>/toggle_verification', methods=['POST'])
@login_required
@require_admin
def toggle_user_verification(user_id):
    """Toggle user verification status"""
    user = User.query.get_or_404(user_id)
    user.otp_verified = not user.otp_verified
    db.session.commit()
    
    return jsonify({
        'message': f'User verification {"enabled" if user.otp_verified else "disabled"}',
        'user': user.to_dict()
    }), 200

@admin.route('/api/keys')
@login_required
@require_admin
def get_all_keys():
    """Get all API keys with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    status = request.args.get('status', '').strip()
    user_id = request.args.get('user_id', type=int)
    
    query = ApiKey.query
    
    if status and status in ['active', 'inactive', 'revoked']:
        query = query.filter(ApiKey.status == status)
    
    if user_id:
        query = query.filter(ApiKey.user_id == user_id)
    
    keys = query.order_by(ApiKey.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    keys_data = []
    for key in keys.items:
        key_data = key.to_dict()
        key_data['owner_username'] = key.owner.username
        key_data['owner_email'] = key.owner.email
        keys_data.append(key_data)
    
    return jsonify({
        'keys': keys_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': keys.total,
            'pages': keys.pages,
            'has_next': keys.has_next,
            'has_prev': keys.has_prev
        }
    }), 200

@admin.route('/api/keys/<int:key_id>/status', methods=['POST'])
@login_required
@require_admin
def admin_update_key_status(key_id):
    """Update API key status (admin)"""
    api_key = ApiKey.query.get_or_404(key_id)
    
    data = request.get_json() if request.is_json else request.form
    new_status = data.get('status', '').strip().lower()
    
    if new_status not in ['active', 'inactive', 'revoked']:
        return jsonify({'error': 'Invalid status'}), 400
    
    api_key.status = new_status
    db.session.commit()
    
    return jsonify({
        'message': f'API key status updated to {new_status}',
        'key': api_key.to_dict()
    }), 200

@admin.route('/api/usage_analytics')
@login_required
@require_admin
def get_usage_analytics():
    """Get usage analytics for admin dashboard"""
    days = request.args.get('days', 30, type=int)
    days = min(days, 365)  # Limit to 1 year
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Daily usage counts
    daily_usage = db.session.query(
        db.func.date(ApiUsage.timestamp).label('date'),
        db.func.count(ApiUsage.id).label('count')
    ).filter(
        ApiUsage.timestamp >= start_date
    ).group_by(db.func.date(ApiUsage.timestamp)).order_by(
        db.func.date(ApiUsage.timestamp)
    ).all()
    
    # Top endpoints
    top_endpoints = db.session.query(
        ApiUsage.endpoint,
        db.func.count(ApiUsage.id).label('count')
    ).filter(
        ApiUsage.timestamp >= start_date
    ).group_by(ApiUsage.endpoint).order_by(
        db.func.count(ApiUsage.id).desc()
    ).limit(10).all()
    
    # Top users by usage
    top_users = db.session.query(
        User.username,
        db.func.count(ApiUsage.id).label('usage_count')
    ).join(ApiKey).join(ApiUsage).filter(
        ApiUsage.timestamp >= start_date
    ).group_by(User.id, User.username).order_by(
        db.func.count(ApiUsage.id).desc()
    ).limit(10).all()
    
    # Status distribution
    status_distribution = db.session.query(
        ApiUsage.status,
        db.func.count(ApiUsage.id).label('count')
    ).filter(
        ApiUsage.timestamp >= start_date
    ).group_by(ApiUsage.status).all()
    
    return jsonify({
        'daily_usage': {
            'labels': [usage.date.strftime('%Y-%m-%d') for usage in daily_usage],
            'data': [usage.count for usage in daily_usage]
        },
        'top_endpoints': [
            {'endpoint': endpoint, 'count': count} 
            for endpoint, count in top_endpoints
        ],
        'top_users': [
            {'username': username, 'usage_count': count} 
            for username, count in top_users
        ],
        'status_distribution': [
            {'status': status, 'count': count} 
            for status, count in status_distribution
        ]
    }), 200

@admin.route('/api/recent_activity')
@login_required
@require_admin
def get_admin_recent_activity():
    """Get recent system activity"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 50)
    
    # Get recent usage logs
    recent_logs = ApiUsage.query.order_by(ApiUsage.timestamp.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    activities = []
    for log in recent_logs.items:
        activities.append({
            'id': log.id,
            'endpoint': log.endpoint,
            'timestamp': log.timestamp.isoformat() if log.timestamp else None,
            'status': log.status,
            'key_name': log.api_key.name,
            'key_preview': log.api_key.key_preview,
            'user': log.api_key.owner.username,
            'ip_address': log.ip_address
        })
    
    return jsonify({
        'activities': activities,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': recent_logs.total,
            'pages': recent_logs.pages,
            'has_next': recent_logs.has_next,
            'has_prev': recent_logs.has_prev
        }
    }), 200