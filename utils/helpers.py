import secrets
import string
import hashlib
import random
from flask import current_app
from flask_mail import Message, Mail
from datetime import datetime, timedelta

def generate_secure_api_key(length=128):
    """Generate a very long, secure API key"""
    # Use a mix of letters, digits, and some safe symbols
    alphabet = string.ascii_letters + string.digits + '-_'
    api_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    return api_key

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def hash_api_key(api_key):
    """Hash an API key using SHA256"""
    return hashlib.sha256(api_key.encode('utf-8')).hexdigest()

def verify_api_key_hash(api_key, key_hash):
    """Verify an API key against its hash"""
    return hash_api_key(api_key) == key_hash

def send_email(mail_instance, to_email, subject, html_content, text_content=None):
    """Send email using Flask-Mail"""
    try:
        msg = Message(
            subject=subject,
            recipients=[to_email],
            html=html_content,
            body=text_content or html_content,
            sender=current_app.config['MAIL_USERNAME']
        )
        mail_instance.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False

def send_otp_email(mail_instance, user_email, otp_code):
    """Send OTP verification email"""
    subject = "API Manager - Email Verification"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
            .content {{ background: #f9f9f9; padding: 30px; }}
            .otp-code {{ background: #fff; border: 2px dashed #667eea; padding: 20px; text-align: center; font-size: 32px; font-weight: bold; color: #667eea; margin: 20px 0; }}
            .footer {{ background: #333; color: white; padding: 20px; text-align: center; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 API Manager</h1>
                <p>Email Verification Required</p>
            </div>
            <div class="content">
                <h2>Welcome to API Manager!</h2>
                <p>Thank you for registering. Please use the following OTP code to verify your email address:</p>
                <div class="otp-code">{otp_code}</div>
                <p><strong>This code will expire in 10 minutes.</strong></p>
                <p>If you didn't request this verification, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>API Manager - Secure API Key Management</p>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(mail_instance, user_email, subject, html_content)

def send_login_alert(mail_instance, user_email, username, ip_address, timestamp):
    """Send login alert email"""
    subject = "API Manager - Login Alert"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 20px; text-align: center; }}
            .content {{ background: #f9f9f9; padding: 30px; }}
            .alert-box {{ background: #fff; border-left: 4px solid #11998e; padding: 20px; margin: 20px 0; }}
            .footer {{ background: #333; color: white; padding: 20px; text-align: center; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 API Manager</h1>
                <p>Login Alert</p>
            </div>
            <div class="content">
                <h2>Successful Login Detected</h2>
                <div class="alert-box">
                    <p><strong>Account:</strong> {username}</p>
                    <p><strong>Time:</strong> {timestamp}</p>
                    <p><strong>IP Address:</strong> {ip_address}</p>
                </div>
                <p>If this wasn't you, please secure your account immediately by changing your password.</p>
            </div>
            <div class="footer">
                <p>API Manager - Secure API Key Management</p>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(mail_instance, user_email, subject, html_content)

def send_api_key_generated_email(mail_instance, user_email, key_name, key_preview):
    """Send email notification when new API key is generated"""
    subject = "API Manager - New API Key Generated"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%); color: #2d3436; padding: 20px; text-align: center; }}
            .content {{ background: #f9f9f9; padding: 30px; }}
            .key-box {{ background: #fff; border: 2px solid #fab1a0; padding: 20px; margin: 20px 0; }}
            .footer {{ background: #333; color: white; padding: 20px; text-align: center; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔑 API Manager</h1>
                <p>New API Key Generated</p>
            </div>
            <div class="content">
                <h2>API Key Created Successfully</h2>
                <div class="key-box">
                    <p><strong>Key Name:</strong> {key_name or 'Unnamed Key'}</p>
                    <p><strong>Key Preview:</strong> {key_preview}</p>
                    <p><strong>Status:</strong> Active</p>
                </div>
                <p>Your new API key has been generated and is ready to use. Please store it securely as you won't be able to see the full key again.</p>
                <p>If you didn't create this key, please contact support immediately.</p>
            </div>
            <div class="footer">
                <p>API Manager - Secure API Key Management</p>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(mail_instance, user_email, subject, html_content)

def get_client_ip(request):
    """Get client IP address from request"""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']

def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    return True, "Password is valid"

def format_datetime(dt):
    """Format datetime for display"""
    if not dt:
        return "Never"
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def time_ago(dt):
    """Return human-readable time ago string"""
    if not dt:
        return "Never"
    
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hours ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minutes ago"
    else:
        return "Just now"