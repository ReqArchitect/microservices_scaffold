from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from datetime import timedelta
from .models import User, Tenant, UserActivity
from . import db
from .utils.circuit_breaker import CircuitBreaker
from .utils.versioning import api_version
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('auth', __name__)

# Circuit breaker for external service calls
auth_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60
)

@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200

@bp.route('/v1/auth/register', methods=['POST'])
@api_version('1.0')
def register():
    """Register a new user."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'full_name', 'tenant_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if user already exists
        if User.query.filter_by(email=data['email'], tenant_id=data['tenant_id']).first():
            return jsonify({'error': 'User already exists'}), 409

        # Create new user
        user = User(
            email=data['email'],
            full_name=data['full_name'],
            tenant_id=data['tenant_id'],
            role=data.get('role', 'user')
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        # Log activity
        activity = UserActivity(
            user_id=user.id,
            action='register',
            details={'method': 'email'},
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/v1/auth/login', methods=['POST'])
@api_version('1.0')
def login():
    """Authenticate user and return tokens."""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Missing email or password'}), 400

        user = User.query.filter_by(
            email=data['email'],
            tenant_id=data.get('tenant_id')
        ).first()

        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401

        if not user.is_active:
            return jsonify({'error': 'Account is disabled'}), 403

        # Create tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'email': user.email,
                'role': user.role,
                'tenant_id': user.tenant_id
            }
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            additional_claims={
                'email': user.email,
                'role': user.role,
                'tenant_id': user.tenant_id
            }
        )

        # Update last login
        user.last_login = datetime.utcnow()
        
        # Log activity
        activity = UserActivity(
            user_id=user.id,
            action='login',
            details={'method': 'email'},
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/v1/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
@api_version('1.0')
def refresh():
    """Refresh access token."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_active:
            return jsonify({'error': 'Invalid or inactive user'}), 401

        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'email': user.email,
                'role': user.role,
                'tenant_id': user.tenant_id
            }
        )

        # Log activity
        activity = UserActivity(
            user_id=user.id,
            action='token_refresh',
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({'access_token': access_token}), 200

    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/v1/auth/logout', methods=['POST'])
@jwt_required()
@api_version('1.0')
def logout():
    """Logout user."""
    try:
        current_user_id = get_jwt_identity()
        
        # Log activity
        activity = UserActivity(
            user_id=current_user_id,
            action='logout',
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({'message': 'Successfully logged out'}), 200

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/v1/auth/verify-email/<token>', methods=['GET'])
@api_version('1.0')
def verify_email(token):
    """Verify user email."""
    try:
        user = User.query.filter_by(email_verification_token=token).first()
        
        if not user:
            return jsonify({'error': 'Invalid verification token'}), 400

        user.is_email_verified = True
        user.email_verification_token = None

        # Log activity
        activity = UserActivity(
            user_id=user.id,
            action='email_verification',
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({'message': 'Email verified successfully'}), 200

    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/v1/auth/reset-password', methods=['POST'])
@api_version('1.0')
def request_password_reset():
    """Request password reset."""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400

        user = User.query.filter_by(email=data['email']).first()
        
        if user:
            # Generate reset token and send email (implementation needed)
            # For now, just log the request
            activity = UserActivity(
                user_id=user.id,
                action='password_reset_request',
                ip_address=request.remote_addr
            )
            db.session.add(activity)
            db.session.commit()

        # Always return success to prevent email enumeration
        return jsonify({'message': 'If the email exists, a password reset link has been sent'}), 200

    except Exception as e:
        logger.error(f"Password reset request error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/v1/auth/reset-password/<token>', methods=['POST'])
@api_version('1.0')
def reset_password(token):
    """Reset password using token."""
    try:
        data = request.get_json()
        
        if not data or 'password' not in data:
            return jsonify({'error': 'New password is required'}), 400

        user = User.query.filter_by(password_reset_token=token).first()
        
        if not user:
            return jsonify({'error': 'Invalid reset token'}), 400

        user.set_password(data['password'])
        user.password_reset_token = None

        # Log activity
        activity = UserActivity(
            user_id=user.id,
            action='password_reset',
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({'message': 'Password reset successfully'}), 200

    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/v1/auth/me', methods=['GET'])
@jwt_required()
@api_version('1.0')
def get_current_user():
    """Get current user information."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify(user.to_dict()), 200

    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/v1/auth/me', methods=['PUT'])
@jwt_required()
@api_version('1.0')
def update_current_user():
    """Update current user information."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()
        
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'preferences' in data:
            user.preferences = data['preferences']

        # Log activity
        activity = UserActivity(
            user_id=user.id,
            action='profile_update',
            details={'updated_fields': list(data.keys())},
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify(user.to_dict()), 200

    except Exception as e:
        logger.error(f"Update current user error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500 