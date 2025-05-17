from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity,
    create_refresh_token, get_jwt, verify_jwt_in_request
)
from app import db
from app.models import Tenant, User, UserActivity
from werkzeug.security import generate_password_hash, check_password_hash
from flasgger import swag_from
from app.utils import (
    validate_password, validate_email_format, generate_password_reset_token,
    generate_email_verification_token, log_user_activity, get_tenant_id
)
from datetime import datetime, timedelta
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import time
from app import limiter, REQUEST_LATENCY, AUTH_ATTEMPTS, USER_ACTIONS, USER_ACTION_LATENCY, FAILED_LOGINS, TOKEN_REFRESHES, PASSWORD_RESETS, EMAIL_VERIFICATIONS, USER_ROLE_CHANGES
from app.utils.auth_client import auth_required

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprints for different API versions
v1_blueprint = Blueprint('v1', __name__, url_prefix='/api/v1')
user_blueprint = Blueprint('users', __name__, url_prefix='/api/v1/users')
auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')

# Register blueprints
v1_blueprint.register_blueprint(user_blueprint)
v1_blueprint.register_blueprint(auth_blueprint)

def role_required(roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            jwt = get_jwt()
            if jwt.get("role") not in roles:
                return jsonify({"message": "Unauthorized"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

@user_blueprint.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
@swag_from({
    "tags": ["User Management"],
    "summary": "Register new user",
    "description": "Creates a user and assigns them to a tenant",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"},
                    "password": {"type": "string"},
                    "full_name": {"type": "string"},
                    "tenant_name": {"type": "string"},
                    "role": {"type": "string", "enum": ["vendor_admin", "tenant_admin", "user"]}
                },
                "required": ["email", "password", "full_name", "tenant_name"]
            }
        }
    ],
    "responses": {
        201: {"description": "User registered successfully"},
        400: {"description": "Invalid input"},
        429: {"description": "Too many requests"}
    }
})
def register():
    start_time = time.time()
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")
    tenant_name = data.get("tenant_name")
    role = data.get("role", "user")

    if not all([email, password, full_name, tenant_name]):
        return jsonify({"message": "All fields are required"}), 400

    # Validate email format
    is_valid_email, email_message = validate_email_format(email)
    if not is_valid_email:
        return jsonify({"message": email_message}), 400

    # Validate password complexity
    is_valid_password, password_message = validate_password(password)
    if not is_valid_password:
        return jsonify({"message": password_message}), 400

    tenant = Tenant.query.filter_by(name=tenant_name).first()
    if not tenant:
        tenant = Tenant(name=tenant_name)
        db.session.add(tenant)
        db.session.commit()

    user = User.query.filter_by(email=email, tenant_id=tenant.id).first()
    if user:
        return jsonify({"message": "User already exists"}), 400

    # Determine role based on whether this is the first user
    if User.query.count() == 0:
        role = "vendor_admin"  # First user is always vendor admin
    elif role not in ["vendor_admin", "tenant_admin", "user"]:
        role = "user"  # Default to user if invalid role specified

    verification_token = generate_email_verification_token()
    new_user = User(
        email=email,
        full_name=full_name,
        password_hash=generate_password_hash(password),
        role=role,
        tenant_id=tenant.id,
        email_verification_token=verification_token
    )
    db.session.add(new_user)
    db.session.commit()

    # Log activity
    log_user_activity(db, new_user.id, "register", {"tenant_id": tenant.id})

    USER_ACTIONS.labels(
        action_type='register',
        tenant_id=tenant.id,
        role=role
    ).inc()
    
    USER_ACTION_LATENCY.labels(action_type='register').observe(time.time() - start_time)
    return jsonify({"message": "User registered successfully"}), 201

@auth_blueprint.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
@swag_from({
    "tags": ["Authentication"],
    "summary": "Login",
    "description": "Authenticate user and get JWT token",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"},
                    "password": {"type": "string"},
                    "tenant_name": {"type": "string"}
                },
                "required": ["email", "password", "tenant_name"]
            }
        }
    ],
    "responses": {
        200: {"description": "Login successful, JWT returned"},
        401: {"description": "Invalid credentials"},
        400: {"description": "Missing fields"},
        429: {"description": "Too many requests"}
    }
})
def login():
    start_time = time.time()
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    tenant_name = data.get("tenant_name")

    if not all([email, password, tenant_name]):
        return jsonify({"message": "All fields are required"}), 400

    tenant = Tenant.query.filter_by(name=tenant_name).first()
    if not tenant:
        return jsonify({"message": "Invalid tenant"}), 400

    user = User.query.filter_by(email=email, tenant_id=tenant.id).first()
    if not user or not check_password_hash(user.password_hash, password):
        FAILED_LOGINS.labels(reason='invalid_credentials').inc()
        AUTH_ATTEMPTS.labels(type='login', status='failed').inc()
        return jsonify({"message": "Invalid credentials"}), 401

    if not user.is_active:
        FAILED_LOGINS.labels(reason='inactive_account').inc()
        AUTH_ATTEMPTS.labels(type='login', status='failed').inc()
        return jsonify({"message": "Account is inactive"}), 401

    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    # Log activity
    log_user_activity(db, user.id, "login", {"ip": request.remote_addr})

    access_token = create_access_token(identity={
        "id": user.id,
        "tenant_id": tenant.id,
        "role": user.role
    })
    refresh_token = create_refresh_token(identity={
        "id": user.id,
        "tenant_id": tenant.id,
        "role": user.role
    })

    AUTH_ATTEMPTS.labels(type='login', status='success').inc()
    USER_ACTIONS.labels(
        action_type='login',
        tenant_id=tenant.id,
        role=user.role
    ).inc()
    
    USER_ACTION_LATENCY.labels(action_type='login').observe(time.time() - start_time)
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200

@user_blueprint.route("/me", methods=["GET"])
@auth_required()
@swag_from({
    "tags": ["User"],
    "summary": "Get current user info",
    "description": "Returns the authenticated user's profile",
    "security": [{"bearerAuth": []}],
    "responses": {
        200: {"description": "Current user profile"},
        404: {"description": "User not found"}
    }
})
def get_current_user():
    user = User.query.get(request.user['id'])
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "tenant_id": user.tenant_id,
        "is_email_verified": user.is_email_verified,
        "preferences": user.preferences,
        "last_login": user.last_login.isoformat() if user.last_login else None
    })

@user_blueprint.route("/me", methods=["PUT"])
@auth_required()
@swag_from({
    "tags": ["User"],
    "summary": "Update current user",
    "description": "Update the authenticated user's profile",
    "security": [{"bearerAuth": []}],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "full_name": {"type": "string"},
                    "preferences": {"type": "object"}
                }
            }
        }
    ],
    "responses": {
        200: {"description": "User updated successfully"},
        400: {"description": "Invalid input"}
    }
})
def update_current_user():
    user = User.query.get(request.user['id'])
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    if "full_name" in data:
        user.full_name = data["full_name"]
    if "preferences" in data:
        user.preferences = data["preferences"]

    db.session.commit()
    return jsonify({"message": "User updated successfully"})

@user_blueprint.route("/me/activity", methods=["GET"])
@auth_required()
@swag_from({
    "tags": ["User"],
    "summary": "Get user activity",
    "description": "Get the authenticated user's activity log",
    "security": [{"bearerAuth": []}],
    "parameters": [
        {
            "name": "limit",
            "in": "query",
            "type": "integer",
            "default": 10
        },
        {
            "name": "offset",
            "in": "query",
            "type": "integer",
            "default": 0
        }
    ],
    "responses": {
        200: {"description": "User activity log"},
        404: {"description": "User not found"}
    }
})
def get_user_activity():
    user = User.query.get(request.user['id'])
    if not user:
        return jsonify({"message": "User not found"}), 404

    limit = request.args.get("limit", 10, type=int)
    offset = request.args.get("offset", 0, type=int)

    activities = UserActivity.query.filter_by(user_id=user.id)\
        .order_by(UserActivity.created_at.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()

    return jsonify([{
        "action": activity.action,
        "details": activity.details,
        "ip_address": activity.ip_address,
        "created_at": activity.created_at.isoformat()
    } for activity in activities])

@v1_blueprint.route("/health", methods=["GET"])
@swag_from({
    "tags": ["System"],
    "summary": "Health check",
    "description": "Check the health of the service",
    "responses": {
        200: {"description": "Service is healthy"}
    }
})
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "user-service",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    })

@user_blueprint.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@swag_from({
    "tags": ["Auth"],
    "summary": "Refresh access token",
    "description": "Get a new access token using refresh token",
    "security": [{"bearerAuth": []}],
    "responses": {
        200: {"description": "New access token generated"},
        401: {"description": "Invalid refresh token"}
    }
})
def refresh():
    identity = get_jwt_identity()
    user = User.query.get(identity["id"])
    if not user or not user.is_active:
        return jsonify({"message": "Invalid refresh token"}), 401

    access_token = create_access_token(identity={
        "id": user.id,
        "tenant_id": user.tenant_id,
        "role": user.role
    })
    return jsonify(access_token=access_token)

@user_blueprint.route("", methods=["GET"])
@auth_required(permissions=['list_users'])
@swag_from({
    "tags": ["Admin"],
    "summary": "List users",
    "description": "Get a list of users (admin only)",
    "security": [{"bearerAuth": []}],
    "parameters": [
        {
            "name": "tenant_id",
            "in": "query",
            "type": "integer",
            "description": "Filter by tenant ID"
        },
        {
            "name": "role",
            "in": "query",
            "type": "string",
            "description": "Filter by role"
        },
        {
            "name": "limit",
            "in": "query",
            "type": "integer",
            "default": 10
        },
        {
            "name": "offset",
            "in": "query",
            "type": "integer",
            "default": 0
        }
    ],
    "responses": {
        200: {"description": "List of users"},
        403: {"description": "Unauthorized"}
    }
})
def list_users():
    tenant_id = request.args.get("tenant_id", type=int)
    role = request.args.get("role")
    limit = request.args.get("limit", 10, type=int)
    offset = request.args.get("offset", 0, type=int)

    query = User.query

    # Filter by tenant if specified
    if tenant_id:
        query = query.filter_by(tenant_id=tenant_id)

    if role:
        query = query.filter_by(role=role)

    total = query.count()
    users = query.limit(limit).offset(offset).all()

    return jsonify({
        "total": total,
        "users": [{
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "tenant_id": user.tenant_id,
            "is_active": user.is_active,
            "is_email_verified": user.is_email_verified,
            "last_login": user.last_login.isoformat() if user.last_login else None
        } for user in users]
    })

@user_blueprint.route("/<int:user_id>", methods=["PUT"])
@jwt_required()
@role_required(["vendor", "admin"])
@swag_from({
    "tags": ["Admin"],
    "summary": "Update user",
    "description": "Update user details (admin only)",
    "security": [{"bearerAuth": []}],
    "parameters": [
        {
            "name": "user_id",
            "in": "path",
            "type": "integer",
            "required": True
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "is_active": {"type": "boolean"},
                    "role": {"type": "string"}
                }
            }
        }
    ],
    "responses": {
        200: {"description": "User updated successfully"},
        403: {"description": "Unauthorized"},
        404: {"description": "User not found"}
    }
})
def update_user(user_id):
    identity = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Check permissions
    if identity["role"] != "vendor" and user.tenant_id != identity["tenant_id"]:
        return jsonify({"message": "Unauthorized"}), 403

    data = request.get_json()
    if "is_active" in data:
        user.is_active = data["is_active"]
    if "role" in data and identity["role"] == "vendor":
        user.role = data["role"]

    db.session.commit()
    log_user_activity(db, identity["id"], "update_user", {
        "target_user_id": user_id,
        "changes": data
    })
    return jsonify({"message": "User updated successfully"})

@user_blueprint.route("/<int:user_id>/activity", methods=["GET"])
@jwt_required()
@role_required(["vendor", "admin"])
@swag_from({
    "tags": ["Admin"],
    "summary": "Get user activity",
    "description": "Get activity log for a specific user (admin only)",
    "security": [{"bearerAuth": []}],
    "parameters": [
        {
            "name": "user_id",
            "in": "path",
            "type": "integer",
            "required": True
        },
        {
            "name": "limit",
            "in": "query",
            "type": "integer",
            "default": 10
        },
        {
            "name": "offset",
            "in": "query",
            "type": "integer",
            "default": 0
        }
    ],
    "responses": {
        200: {"description": "User activity log"},
        403: {"description": "Unauthorized"},
        404: {"description": "User not found"}
    }
})
def get_user_activity_log(user_id):
    identity = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Check permissions
    if identity["role"] != "vendor" and user.tenant_id != identity["tenant_id"]:
        return jsonify({"message": "Unauthorized"}), 403

    limit = request.args.get("limit", 10, type=int)
    offset = request.args.get("offset", 0, type=int)

    activities = UserActivity.query.filter_by(user_id=user_id)\
        .order_by(UserActivity.created_at.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()

    return jsonify([{
        "action": activity.action,
        "details": activity.details,
        "ip_address": activity.ip_address,
        "created_at": activity.created_at.isoformat()
    } for activity in activities])

@user_blueprint.route("/metrics", methods=["GET"])
@jwt_required()
@role_required(["vendor"])
@swag_from({
    "tags": ["System"],
    "summary": "Get service metrics",
    "description": "Get system metrics (vendor only)",
    "security": [{"bearerAuth": []}],
    "responses": {
        200: {"description": "System metrics"},
        403: {"description": "Unauthorized"}
    }
})
def get_metrics():
    # Get basic metrics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    verified_users = User.query.filter_by(is_email_verified=True).count()
    total_tenants = Tenant.query.count()
    
    # Get recent activity
    recent_activities = UserActivity.query\
        .order_by(UserActivity.created_at.desc())\
        .limit(10)\
        .all()

    return jsonify({
        "users": {
            "total": total_users,
            "active": active_users,
            "verified": verified_users
        },
        "tenants": total_tenants,
        "recent_activities": [{
            "action": activity.action,
            "user_id": activity.user_id,
            "created_at": activity.created_at.isoformat()
        } for activity in recent_activities]
    })
