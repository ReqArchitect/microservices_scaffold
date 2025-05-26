from functools import wraps
from flask import jsonify, current_app, request
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    get_jwt_identity, verify_jwt_in_request, get_jwt
)
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

def create_tokens(identity: Dict[str, Any]) -> Dict[str, str]:
    """
    Create access and refresh tokens with consistent identity claims.
    
    Args:
        identity: Dictionary containing user identity information
        
    Returns:
        Dictionary containing access_token and refresh_token
    """
    try:
        # Ensure required fields
        required_fields = ['id', 'tenant_id', 'role']
        if not all(field in identity for field in required_fields):
            raise ValueError(f"Missing required fields in identity. Required: {required_fields}")

        # Create tokens with consistent identity claim
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    except Exception as e:
        logger.error(f"Error creating tokens: {str(e)}")
        raise

def validate_token() -> Optional[Dict[str, Any]]:
    """
    Validate JWT token and return identity with permissions.
    
    Returns:
        Dictionary containing user identity and permissions, or None if invalid
    """
    try:
        verify_jwt_in_request()
        identity = get_jwt_identity()
        
        if not identity or not isinstance(identity, dict):
            logger.error("Invalid token: identity is not a dict")
            return None
        
        # Validate required fields
        required_fields = ['id', 'tenant_id', 'role']
        if not all(field in identity for field in required_fields):
            logger.error(f"Invalid token: missing required fields. Got: {identity}")
            return None
        
        # Get role from token
        role = identity.get('role')
        if not role:
            logger.error("Invalid token: missing role")
            return None
            
        # Get permissions from role
        permissions = get_user_permissions(role)
        identity['permissions'] = permissions
        
        logger.debug(f"Token validated successfully for user {identity['id']} with role {role}")
        return identity
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return None

def get_user_permissions(role: str) -> Dict[str, list]:
    """
    Get permissions for a given role.
    
    Args:
        role: User role
        
    Returns:
        Dictionary of resource permissions
    """
    # Define roles and their permissions
    ROLES = {
        'vendor_admin': {
            'initiatives': ['create', 'read', 'update', 'delete'],
            'users': ['create', 'read', 'update', 'delete'],
            'reports': ['create', 'read', 'update', 'delete']
        },
        'tenant_admin': {
            'initiatives': ['create', 'read', 'update'],
            'users': ['read', 'update'],
            'reports': ['create', 'read']
        },
        'user': {
            'initiatives': ['read'],
            'users': ['read'],
            'reports': ['read']
        }
    }
    
    return ROLES.get(role, {})

def has_permission(identity: Dict[str, Any], resource: str, action: str) -> bool:
    """
    Check if user has permission to perform action on resource.
    
    Args:
        identity: User identity dictionary
        resource: Resource to check permission for
        action: Action to check permission for
        
    Returns:
        Boolean indicating if user has permission
    """
    try:
        if not identity or 'role' not in identity:
            return False
        
        role = identity['role']
        permissions = get_user_permissions(role)
        
        return action in permissions.get(resource, [])
    except Exception as e:
        logger.error(f"Permission check error: {str(e)}")
        return False

def permission_required(resource: str, action: str):
    """
    Decorator to check if user has required permission.
    
    Args:
        resource: Resource to check permission for
        action: Action to check permission for
    """
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
                logger.error(f"Permission check error: {str(e)}")
                return jsonify({"error": "Unauthorized"}), 401
        return wrapper
    return decorator

def role_required(role: str):
    """
    Decorator to check if user has required role.
    
    Args:
        role: Required role
    """
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
                logger.error(f"Role check error: {str(e)}")
                return jsonify({"error": "Unauthorized"}), 401
        return wrapper
    return decorator

def log_auth_event(identity: Dict[str, Any], resource: str, action: str, success: bool):
    """
    Log authentication and authorization events.
    
    Args:
        identity: User identity dictionary
        resource: Resource being accessed
        action: Action being performed
        success: Whether the action was successful
    """
    try:
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': identity.get('id'),
            'tenant_id': identity.get('tenant_id'),
            'role': identity.get('role'),
            'resource': resource,
            'action': action,
            'success': success,
            'ip_address': request.remote_addr
        }
        if success:
            logger.info(f"Auth event: {event}")
        else:
            logger.warning(f"Auth failure: {event}")
    except Exception as e:
        logger.error(f"Error logging auth event: {str(e)}") 