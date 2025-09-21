from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import ApiKey, ApiUsage, LoginHistory, db
from utils.decorators import require_verified_user
from datetime import datetime, timedelta

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
@login_required
@require_verified_user
def index():
    """Main dashboard page"""
    return render_template('dashboard/index.html')

@dashboard.route('/keys')
@login_required
@require_verified_user
def keys():
    """API keys management page"""
    return render_template('dashboard/keys.html')

@dashboard.route('/usage')
@login_required
@require_verified_user
def usage():
    """Usage analytics page"""
    return render_template('dashboard/usage.html')

@dashboard.route('/account')
@login_required
@require_verified_user
def account():
    """Account settings page"""
    return render_template('dashboard/account.html')

@dashboard.route('/api/stats')
@login_required
@require_verified_user
def get_dashboard_stats():
    """Get dashboard statistics"""
    # User's API key stats
    total_keys = ApiKey.query.filter_by(user_id=current_user.id).count()
    active_keys = ApiKey.query.filter_by(user_id=current_user.id, status='active').count()
    
    # Total usage across all user's keys
    total_usage = db.session.query(db.func.sum(ApiKey.usage_count)).filter_by(
        user_id=current_user.id
    ).scalar() or 0
    
    # Recent usage (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_usage = ApiUsage.query.join(ApiKey).filter(
        ApiKey.user_id == current_user.id,
        ApiUsage.timestamp >= seven_days_ago
    ).count()
    
    # Most used endpoint
    most_used_endpoint = db.session.query(
        ApiUsage.endpoint,
        db.func.count(ApiUsage.id).label('count')
    ).join(ApiKey).filter(
        ApiKey.user_id == current_user.id
    ).group_by(ApiUsage.endpoint).order_by(
        db.func.count(ApiUsage.id).desc()
    ).first()
    
    # Recent login count
    recent_logins = LoginHistory.query.filter(
        LoginHistory.user_id == current_user.id,
        LoginHistory.timestamp >= seven_days_ago,
        LoginHistory.success == True
    ).count()
    
    return jsonify({
        'total_keys': total_keys,
        'active_keys': active_keys,
        'total_usage': total_usage,
        'recent_usage': recent_usage,
        'most_used_endpoint': most_used_endpoint[0] if most_used_endpoint else 'None',
        'recent_logins': recent_logins
    }), 200

@dashboard.route('/api/recent_activity')
@login_required
@require_verified_user
def get_recent_activity():
    """Get recent API usage activity"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    
    # Get recent usage logs for user's keys
    recent_logs = db.session.query(ApiUsage).join(ApiKey).filter(
        ApiKey.user_id == current_user.id
    ).order_by(ApiUsage.timestamp.desc()).paginate(
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
            'key_preview': log.api_key.key_preview
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

@dashboard.route('/api/usage_chart')
@login_required
@require_verified_user
def get_usage_chart_data():
    """Get usage data for charts"""
    days = request.args.get('days', 7, type=int)
    days = min(days, 90)  # Limit to 90 days
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get daily usage counts
    daily_usage = db.session.query(
        db.func.date(ApiUsage.timestamp).label('date'),
        db.func.count(ApiUsage.id).label('count')
    ).join(ApiKey).filter(
        ApiKey.user_id == current_user.id,
        ApiUsage.timestamp >= start_date
    ).group_by(db.func.date(ApiUsage.timestamp)).order_by(
        db.func.date(ApiUsage.timestamp)
    ).all()
    
    # Format data for chart
    chart_data = {
        'labels': [],
        'data': []
    }
    
    for usage in daily_usage:
        chart_data['labels'].append(usage.date.strftime('%Y-%m-%d'))
        chart_data['data'].append(usage.count)
    
    return jsonify(chart_data), 200

@dashboard.route('/api/login_history')
@login_required
@require_verified_user
def get_login_history():
    """Get user's login history"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 50)
    
    login_logs = LoginHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(LoginHistory.timestamp.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return jsonify({
        'login_history': [log.to_dict() for log in login_logs.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': login_logs.total,
            'pages': login_logs.pages,
            'has_next': login_logs.has_next,
            'has_prev': login_logs.has_prev
        }
    }), 200