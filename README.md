# API Manager

A full-stack web application for secure API key management with user authentication, email notifications, and comprehensive analytics.

## Features

- **User Management**
  - Registration with email OTP verification
  - Secure login with password hashing (bcrypt)
  - Password change and email update functionality
  - Login history tracking

- **API Key Management**
  - Generate secure 128+ character API keys
  - Key activation/deactivation/revocation
  - Optional expiration dates
  - Usage tracking and analytics

- **Security**
  - SHA256 API key hashing
  - CSRF protection
  - Rate limiting
  - Input validation and sanitization

- **Email Notifications**
  - OTP verification emails
  - Login alerts
  - API key generation notifications

- **Admin Dashboard**
  - User management
  - System-wide analytics
  - Usage monitoring
  - Key management

- **Modern UI**
  - Responsive design with Tailwind CSS
  - Interactive animations
  - Real-time charts with Chart.js
  - Mobile-friendly interface

## Tech Stack

- **Backend**: Flask + Python 3.11
- **Database**: SQLite (easily upgradable to PostgreSQL)
- **Frontend**: HTML5, CSS3, JavaScript, Tailwind CSS
- **Email**: SMTP (Gmail, Outlook, or custom)
- **Security**: bcrypt, SHA256, CSRF tokens, rate limiting

## Quick Start

### Prerequisites

- Python 3.11+
- pip
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd API
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   Copy `.env` file and update with your settings:
   ```bash
   # Update .env with your SMTP credentials
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   SECRET_KEY=your-secret-key
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open http://localhost:5000 in your browser

### First Setup

1. Register the first account (will be automatically set as admin)
2. Verify email with OTP
3. Login and access the dashboard
4. Generate your first API key

## API Usage

### Authentication

Include your API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:5000/api/test
```

### Available Endpoints

- `GET /api/test` - Test endpoint
- `GET /api/user_info` - Get user information
- `GET /api/data` - Sample data endpoint
- `GET /api/weather` - Sample weather data
- `GET /api/quotes` - Random quotes
- `GET /api/status` - API status

### Response Format

```json
{
  "message": "Success message",
  "data": {
    // Response data
  }
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | Required |
| `DATABASE_URL` | Database connection string | `sqlite:///api_manager.db` |
| `SMTP_SERVER` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USERNAME` | SMTP username | Required |
| `SMTP_PASSWORD` | SMTP password/app password | Required |
| `SMTP_USE_TLS` | Use TLS encryption | `True` |

### SMTP Setup (Gmail)

1. Enable 2-factor authentication on your Google account
2. Generate an App Password:
   - Go to Google Account settings
   - Security > 2-Step Verification > App passwords
   - Generate password for "Mail"
3. Use the generated password in `SMTP_PASSWORD`

## Production Deployment

### Using Docker

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Or build manually**
   ```bash
   docker build -t api-manager .
   docker run -p 8000:8000 --env-file .env api-manager
   ```

### Using Gunicorn

```bash
gunicorn --config gunicorn_config.py app:app
```

### Platform Deployment

#### Render.com
1. Connect your GitHub repository
2. Set environment variables in Render dashboard
3. Deploy with build command: `pip install -r requirements.txt`
4. Start command: `gunicorn --config gunicorn_config.py app:app`

#### Railway.app
1. Connect repository to Railway
2. Add environment variables
3. Deploy automatically

#### Heroku
1. Create Heroku app
2. Set config vars (environment variables)
3. Deploy via Git push

## Security Features

- **Password Security**: bcrypt hashing with configurable rounds
- **API Key Security**: SHA256 hashing, secure generation
- **CSRF Protection**: All forms protected against CSRF attacks
- **Rate Limiting**: Configurable rate limits per endpoint
- **Input Validation**: Server-side validation for all inputs
- **Email Verification**: OTP-based email verification
- **Session Security**: Secure session management

## Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `password_hash`: bcrypt hashed password
- `otp_verified`: Email verification status
- `is_admin`: Admin privileges flag
- `created_at`: Account creation timestamp

### API Keys Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `key_hash`: SHA256 hashed API key
- `key_preview`: First 16 characters for display
- `name`: Optional key name
- `status`: active/inactive/revoked
- `created_at`: Key creation timestamp
- `expires_at`: Optional expiration timestamp
- `usage_count`: Total usage counter

### API Usage Table
- `id`: Primary key
- `key_id`: Foreign key to API keys
- `endpoint`: Accessed endpoint
- `timestamp`: Request timestamp
- `status`: Request status
- `ip_address`: Client IP address

### Login History Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `timestamp`: Login timestamp
- `ip_address`: Login IP address
- `success`: Login success/failure

## Development

### Project Structure
```
API/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
├── models/
│   └── __init__.py       # Database models
├── routes/
│   ├── __init__.py
│   ├── auth.py           # Authentication routes
│   ├── api_keys.py       # API key management
│   ├── api.py            # Public API endpoints
│   ├── dashboard.py      # Dashboard routes
│   └── admin.py          # Admin routes
├── utils/
│   ├── __init__.py
│   ├── helpers.py        # Utility functions
│   └── decorators.py     # Custom decorators
├── templates/            # Jinja2 templates
├── static/
│   ├── css/
│   └── js/
└── requirements.txt
```

### Adding New API Endpoints

1. **Create endpoint in routes/api.py**
   ```python
   @api.route('/new_endpoint')
   @require_api_key
   def new_endpoint():
       return jsonify({'message': 'New endpoint'})
   ```

2. **The `@require_api_key` decorator automatically**:
   - Validates API key
   - Records usage
   - Handles errors
   - Provides `g.current_api_key` object

### Customizing Email Templates

Edit the HTML templates in `utils/helpers.py`:
- `send_otp_email()`
- `send_login_alert()`
- `send_api_key_generated_email()`

## Troubleshooting

### Common Issues

1. **SMTP Authentication Error**
   - Use app-specific passwords for Gmail
   - Check firewall settings
   - Verify SMTP credentials

2. **Database Locked Error**
   - Ensure only one instance is running
   - Check file permissions
   - Consider switching to PostgreSQL for production

3. **Template Not Found**
   - Check template file paths
   - Ensure templates directory structure is correct

4. **CSS/JS Not Loading**
   - Check static file paths
   - Verify Flask static file configuration
   - Clear browser cache

### Logs and Debugging

Enable debug mode in development:
```python
app.run(debug=True)
```

Check application logs for errors and add custom logging:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on GitHub or contact the development team.

## Changelog

### Version 1.0.0
- Initial release
- User authentication system
- API key management
- Email notifications
- Admin dashboard
- Modern responsive UI
- Comprehensive documentation