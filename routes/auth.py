from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User, LoginHistory, db
from utils.helpers import generate_otp, send_otp_email, send_login_alert, get_client_ip, validate_password_strength
from utils.decorators import require_verified_user
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    
    data = request.get_json() if request.is_json else request.form
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    # Validation
    if not username or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400
    
    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters long'}), 400
    
    # Validate email format
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Validate password strength
    is_valid, message = validate_password_strength(password)
    if not is_valid:
        return jsonify({'error': message}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    user = User(username=username, email=email)
    user.set_password(password)
    
    # Generate OTP
    otp_code = generate_otp()
    user.set_otp(otp_code)
    
    # Check if this is the first user (make admin)
    if User.query.count() == 0:
        user.is_admin = True
        user.otp_verified = True  # Auto-verify first admin user
    
    db.session.add(user)
    db.session.commit()
    
    # Send OTP email (skip for admin)
    if not user.is_admin:
        from app import mail
        if not send_otp_email(mail, email, otp_code):
            return jsonify({'error': 'Failed to send verification email'}), 500
    
    return jsonify({
        'message': 'Registration successful! Please check your email for verification code.' if not user.is_admin else 'Admin account created successfully!',
        'user_id': user.id,
        'requires_otp': not user.is_admin
    }), 201

@auth.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json() if request.is_json else request.form
    user_id = data.get('user_id')
    otp_code = data.get('otp_code', '').strip()
    
    if not user_id or not otp_code:
        return jsonify({'error': 'User ID and OTP code are required'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Invalid user'}), 400
    
    if user.otp_verified:
        return jsonify({'error': 'Email already verified'}), 400
    
    if user.verify_otp(otp_code):
        user.otp_verified = True
        user.otp_code = None  # Clear OTP after verification
        user.otp_created_at = None
        db.session.commit()
        
        return jsonify({'message': 'Email verified successfully!'}), 200
    else:
        return jsonify({'error': 'Invalid or expired OTP code'}), 400

@auth.route('/resend_otp', methods=['POST'])
def resend_otp():
    data = request.get_json() if request.is_json else request.form
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Invalid user'}), 400
    
    if user.otp_verified:
        return jsonify({'error': 'Email already verified'}), 400
    
    # Generate new OTP
    otp_code = generate_otp()
    user.set_otp(otp_code)
    db.session.commit()
    
    # Send OTP email
    from app import mail
    if send_otp_email(mail, user.email, otp_code):
        return jsonify({'message': 'New OTP sent to your email'}), 200
    else:
        return jsonify({'error': 'Failed to send verification email'}), 500

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    data = request.get_json() if request.is_json else request.form
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Find user by username or email
    user = User.query.filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    # Record login attempt
    ip_address = get_client_ip(request)
    user_agent = request.headers.get('User-Agent')
    
    if user and user.check_password(password):
        if not user.otp_verified:
            return jsonify({'error': 'Please verify your email first'}), 403
        
        # Record successful login
        login_history = LoginHistory(
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True
        )
        db.session.add(login_history)
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Log user in
        login_user(user)
        
        # Send login alert email
        from app import mail
        send_login_alert(mail, user.email, user.username, ip_address, datetime.utcnow())
        
        return jsonify({
            'message': 'Login successful!',
            'user': user.to_dict(),
            'redirect': url_for('dashboard.index')
        }), 200
    else:
        # Record failed login attempt
        if user:
            login_history = LoginHistory(
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False
            )
            db.session.add(login_history)
            db.session.commit()
        
        return jsonify({'error': 'Invalid username or password'}), 401

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/change_password', methods=['POST'])
@login_required
@require_verified_user
def change_password():
    data = request.get_json() if request.is_json else request.form
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')
    
    if not current_password or not new_password or not confirm_password:
        return jsonify({'error': 'All fields are required'}), 400
    
    if new_password != confirm_password:
        return jsonify({'error': 'New passwords do not match'}), 400
    
    if not current_user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 400
    
    # Validate new password strength
    is_valid, message = validate_password_strength(new_password)
    if not is_valid:
        return jsonify({'error': message}), 400
    
    # Update password
    current_user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully!'}), 200

@auth.route('/update_email', methods=['POST'])
@login_required
@require_verified_user
def update_email():
    data = request.get_json() if request.is_json else request.form
    new_email = data.get('new_email', '').strip().lower()
    password = data.get('password', '')
    
    if not new_email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Validate email format
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, new_email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    if not current_user.check_password(password):
        return jsonify({'error': 'Password is incorrect'}), 400
    
    # Check if email is already taken
    if User.query.filter_by(email=new_email).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Generate OTP for new email
    otp_code = generate_otp()
    current_user.set_otp(otp_code)
    current_user.otp_verified = False  # Require re-verification
    
    # Temporarily store new email (you might want to create a separate field for this)
    current_user.email = new_email
    db.session.commit()
    
    # Send OTP to new email
    from app import mail
    if send_otp_email(mail, new_email, otp_code):
        return jsonify({
            'message': 'OTP sent to new email. Please verify to complete the change.',
            'user_id': current_user.id
        }), 200
    else:
        return jsonify({'error': 'Failed to send verification email'}), 500

@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('auth/forgot_password.html')
    
    data = request.get_json() if request.is_json else request.form
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        # Don't reveal if email exists or not
        return jsonify({'message': 'If the email exists, a reset code has been sent'}), 200
    
    # Generate OTP for password reset
    otp_code = generate_otp()
    user.set_otp(otp_code)
    db.session.commit()
    
    # Send reset email
    from app import mail
    send_otp_email(mail, email, otp_code)
    
    return jsonify({
        'message': 'If the email exists, a reset code has been sent',
        'user_id': user.id
    }), 200

@auth.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json() if request.is_json else request.form
    user_id = data.get('user_id')
    otp_code = data.get('otp_code', '').strip()
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')
    
    if not user_id or not otp_code or not new_password or not confirm_password:
        return jsonify({'error': 'All fields are required'}), 400
    
    if new_password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Invalid user'}), 400
    
    if not user.verify_otp(otp_code):
        return jsonify({'error': 'Invalid or expired OTP code'}), 400
    
    # Validate new password strength
    is_valid, message = validate_password_strength(new_password)
    if not is_valid:
        return jsonify({'error': message}), 400
    
    # Update password
    user.set_password(new_password)
    user.otp_code = None
    user.otp_created_at = None
    db.session.commit()
    
    return jsonify({'message': 'Password reset successful!'}), 200