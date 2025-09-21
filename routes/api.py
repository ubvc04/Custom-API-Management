from flask import Blueprint, request, jsonify
from utils.decorators import require_api_key
from flask import g

api = Blueprint('api', __name__)

@api.route('/test')
@require_api_key
def test_endpoint():
    """Test endpoint to verify API key validation"""
    return jsonify({
        'message': 'API key validation successful!',
        'api_key_info': {
            'key_id': g.current_api_key.id,
            'key_name': g.current_api_key.name,
            'key_preview': g.current_api_key.key_preview,
            'owner': g.current_api_key.owner.username
        },
        'data': {
            'timestamp': '2025-09-21T00:00:00Z',
            'status': 'success'
        }
    }), 200

@api.route('/user_info')
@require_api_key
def user_info():
    """Get user information associated with the API key"""
    user = g.current_api_key.owner
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.isoformat() if user.created_at else None
        },
        'api_key_info': {
            'key_id': g.current_api_key.id,
            'key_name': g.current_api_key.name,
            'usage_count': g.current_api_key.usage_count,
            'last_used': g.current_api_key.last_used.isoformat() if g.current_api_key.last_used else None
        }
    }), 200

@api.route('/data')
@require_api_key
def get_data():
    """Sample data endpoint"""
    sample_data = {
        'products': [
            {'id': 1, 'name': 'Product A', 'price': 99.99},
            {'id': 2, 'name': 'Product B', 'price': 149.99},
            {'id': 3, 'name': 'Product C', 'price': 199.99}
        ],
        'total_count': 3,
        'timestamp': '2025-09-21T00:00:00Z'
    }
    
    return jsonify({
        'message': 'Data retrieved successfully',
        'data': sample_data
    }), 200

@api.route('/weather')
@require_api_key
def get_weather():
    """Sample weather endpoint"""
    weather_data = {
        'location': 'New York',
        'temperature': 22,
        'humidity': 65,
        'condition': 'Partly Cloudy',
        'wind_speed': 15,
        'timestamp': '2025-09-21T00:00:00Z'
    }
    
    return jsonify({
        'message': 'Weather data retrieved successfully',
        'weather': weather_data
    }), 200

@api.route('/quotes')
@require_api_key
def get_quotes():
    """Sample quotes endpoint"""
    quotes = [
        {
            'id': 1,
            'text': 'The only way to do great work is to love what you do.',
            'author': 'Steve Jobs'
        },
        {
            'id': 2,
            'text': 'Innovation distinguishes between a leader and a follower.',
            'author': 'Steve Jobs'
        },
        {
            'id': 3,
            'text': 'Your limitation—it\'s only your imagination.',
            'author': 'Unknown'
        }
    ]
    
    import random
    random_quote = random.choice(quotes)
    
    return jsonify({
        'message': 'Quote retrieved successfully',
        'quote': random_quote,
        'total_quotes': len(quotes)
    }), 200

@api.route('/status')
@require_api_key
def api_status():
    """API status endpoint"""
    from datetime import datetime
    
    return jsonify({
        'status': 'operational',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'endpoints': {
            'test': '/api/test',
            'user_info': '/api/user_info',
            'data': '/api/data',
            'weather': '/api/weather',
            'quotes': '/api/quotes',
            'status': '/api/status'
        },
        'api_key_info': {
            'key_id': g.current_api_key.id,
            'key_name': g.current_api_key.name,
            'status': g.current_api_key.status
        }
    }), 200