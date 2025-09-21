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

def send_login_alert_email(mail_instance, user_email, username, login_time, ip_address, user_agent):
    """Send login alert email to user"""
    from datetime import datetime
    
    # Parse user agent for device info
    device_info = "Unknown Device"
    if user_agent:
        if "Windows" in user_agent:
            device_info = "Windows Computer"
        elif "Mac" in user_agent:
            device_info = "Mac Computer"
        elif "iPhone" in user_agent:
            device_info = "iPhone"
        elif "Android" in user_agent:
            device_info = "Android Device"
        elif "iPad" in user_agent:
            device_info = "iPad"
        else:
            device_info = "Unknown Device"
    
    subject = "🔐 New Login to Your API Manager Account"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 20px; text-align: center; }}
            .content {{ background: #f9f9f9; padding: 30px; }}
            .login-details {{ background: #fff; border-left: 4px solid #28a745; padding: 20px; margin: 20px 0; }}
            .security-note {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 20px 0; border-radius: 5px; }}
            .footer {{ background: #333; color: white; padding: 20px; text-align: center; font-size: 12px; }}
            .detail-row {{ margin: 10px 0; }}
            .label {{ font-weight: bold; color: #555; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Login Alert</h1>
                <p>Your API Manager Account Security Notification</p>
            </div>
            <div class="content">
                <h2>Hello {username},</h2>
                <p>We detected a new login to your API Manager account. Here are the details:</p>
                
                <div class="login-details">
                    <h3>📋 Login Details</h3>
                    <div class="detail-row">
                        <span class="label">🕐 Time:</span> {login_time.strftime("%B %d, %Y at %I:%M %p UTC")}
                    </div>
                    <div class="detail-row">
                        <span class="label">🌐 IP Address:</span> {ip_address}
                    </div>
                    <div class="detail-row">
                        <span class="label">💻 Device:</span> {device_info}
                    </div>
                    <div class="detail-row">
                        <span class="label">👤 Account:</span> {username} ({user_email})
                    </div>
                </div>
                
                <div class="security-note">
                    <h3>🛡️ Security Notice</h3>
                    <p><strong>Was this you?</strong> If you recognize this login, no action is needed.</p>
                    <p><strong>Don't recognize this login?</strong> Please:</p>
                    <ul>
                        <li>Change your password immediately</li>
                        <li>Review your API keys and revoke any suspicious ones</li>
                        <li>Check your account activity</li>
                        <li>Contact support if you need assistance</li>
                    </ul>
                </div>
                
                <p>This is an automated security notification to help protect your account.</p>
            </div>
            <div class="footer">
                <p>API Manager - Secure API Key Management</p>
                <p>This email was sent to {user_email}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(mail_instance, user_email, subject, html_content)

def send_api_action_otp_email(mail_instance, user_email, username, otp_code, action_type):
    """Send OTP email for API key actions (create/delete)"""
    
    action_emoji = "🔑" if action_type == "create" else "🗑️"
    action_text = "Create API Key" if action_type == "create" else "Delete API Key"
    
    subject = f"🔐 OTP Required: {action_text}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; padding: 20px; text-align: center; }}
            .content {{ background: #f9f9f9; padding: 30px; }}
            .otp-code {{ background: #fff; border: 2px dashed #ff6b6b; padding: 20px; text-align: center; font-size: 32px; font-weight: bold; color: #ff6b6b; margin: 20px 0; }}
            .action-info {{ background: #fff; border-left: 4px solid #ff6b6b; padding: 20px; margin: 20px 0; }}
            .footer {{ background: #333; color: white; padding: 20px; text-align: center; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{action_emoji} Security Verification</h1>
                <p>OTP Required for API Key Action</p>
            </div>
            <div class="content">
                <h2>Hello {username},</h2>
                <p>You are attempting to <strong>{action_text.lower()}</strong>. For security, please verify this action with the OTP code below:</p>
                
                <div class="otp-code">{otp_code}</div>
                
                <div class="action-info">
                    <h3>🛡️ Security Information</h3>
                    <p><strong>Action:</strong> {action_text}</p>
                    <p><strong>Account:</strong> {username}</p>
                    <p><strong>Time:</strong> Valid for 10 minutes</p>
                </div>
                
                <p><strong>This code will expire in 10 minutes.</strong></p>
                <p>If you didn't request this action, please ignore this email and check your account security.</p>
            </div>
            <div class="footer">
                <p>API Manager - Secure API Key Management</p>
                <p>This email was sent to {user_email}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(mail_instance, user_email, subject, html_content)