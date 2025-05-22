from functools import wraps
from flask import jsonify, current_app, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, get_jwt
import logging
from datetime import datetime

# Define roles and their permissions
ROLES = {
    'admin': {
        'initiatives': ['create', 'read', 'update', 'delete'],
        'users': ['create', 'read', 'update', 'delete'],
        'reports': ['create', 'read', 'update', 'delete']
    },
    'manager': {
        'initiatives': ['create', 'read', 'update'],
        'users': ['read'],
        'reports': ['create', 'read']
    },
    'user': {
        'initiatives': ['read'],
        'users': ['read'],
        'reports': ['read']
    }
}

def get_user_permissions(role):
    """Get permissions for a given role."""
    return ROLES.get(role, {})

def validate_token():
    """Validate JWT token and return identity with permissions."""
    try:
        verify_jwt_in_request()
        identity = get_jwt_identity()
        
        if not identity or not isinstance(identity, dict):
            current_app.logger.error("Invalid token: identity is not a dict")
            return None
        
        # Validate required fields
        required_fields = ['id', 'tenant_id', 'role']
        if not all(field in identity for field in required_fields):
            current_app.logger.error(f"Invalid token: missing required fields. Got: {identity}")
            return None
        
        # Get role from token first, then fall back to header
        role = identity.get('role')
        if not role:
            role = request.headers.get('X-User-Role', 'user')
            current_app.logger.warning(f"Role not found in token, using header: {role}")
        
        if role not in ROLES:
            current_app.logger.error(f"Invalid role: {role}")
            return None
            
        # Update identity with validated role
        identity['role'] = role
        
        # Get permissions from role
        permissions = get_user_permissions(role)
        identity['permissions'] = permissions
        
        current_app.logger.debug(f"Token validated successfully for user {identity['id']} with role {role}")
        return identity
    except Exception as e:
        current_app.logger.error(f"Token validation error: {str(e)}")
        return None

def has_permission(identity, resource, action):
    """Check if user has permission to perform action on resource."""
    try:
        if not identity or 'role' not in identity:
            return False
        
        role = identity['role']
        permissions = ROLES.get(role, {})
        
        return action in permissions.get(resource, [])
    except Exception as e:
        current_app.logger.error(f"Permission check error: {str(e)}")
        return False

def permission_required(resource, action):
    """Decorator to check if user has required permission."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                identity = validate_token()
                if not identity:
                    return jsonify({"error": "Invalid token"}), 401
                
                if not has_permission(identity, resource, action):
                    log_auth_event(identity, resource, action, False)
                    return jsonify({"error": "Unauthorized"}), 403
                
                log_auth_event(identity, resource, action, True)
                return fn(*args, **kwargs)
            except Exception as e:
                current_app.logger.error(f"Permission check error: {str(e)}")
                return jsonify({"error": "Unauthorized"}), 401
        return wrapper
    return decorator

def role_required(role):
    """Decorator to check if user has required role."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                identity = validate_token()
                if not identity:
                    return jsonify({"error": "Invalid token"}), 401
                
                if identity['role'] != role:
                    log_auth_event(identity, 'role', role, False)
                    return jsonify({"error": "Unauthorized"}), 403
                
                log_auth_event(identity, 'role', role, True)
                return fn(*args, **kwargs)
            except Exception as e:
                current_app.logger.error(f"Role check error: {str(e)}")
                return jsonify({"error": "Unauthorized"}), 401
        return wrapper
    return decorator

def check_tenant_access(fn):
    """Decorator to check if user has access to tenant."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            identity = validate_token()
            if not identity:
                return jsonify({"error": "Invalid token"}), 401
            
            tenant_id = request.args.get('tenant_id') or request.json.get('tenant_id')
            if tenant_id and str(tenant_id) != str(identity['tenant_id']):
                log_auth_event(identity, 'tenant', tenant_id, False)
                return jsonify({"error": "Unauthorized tenant access"}), 403
            
            log_auth_event(identity, 'tenant', tenant_id, True)
            return fn(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f"Tenant access check error: {str(e)}")
            return jsonify({"error": "Unauthorized"}), 401
    return wrapper

def log_auth_event(identity, resource, action, success):
    """Log authentication and authorization events."""
    try:
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': identity.get('id'),
            'tenant_id': identity.get('tenant_id'),
            'role': identity.get('role'),
            'resource': resource,
            'action': action,
            'success': success
        }
        if success:
            current_app.logger.info(f"Auth event: {event}")
        else:
            current_app.logger.warning(f"Auth failure: {event}")
    except Exception as e:
        current_app.logger.error(f"Error logging auth event: {str(e)}")

def get_user_role(identity):
    """Get user role from identity."""
    return identity.get('role', 'user') if identity else 'user' 