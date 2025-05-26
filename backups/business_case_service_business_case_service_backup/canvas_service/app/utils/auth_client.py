import requests
from functools import wraps
from flask import current_app, request, jsonify
from .circuit_breaker import CircuitBreaker, CircuitBreakerError

class AuthServiceClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or current_app.config['AUTH_SERVICE_URL']
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=current_app.config['CIRCUIT_BREAKER_FAILURE_THRESHOLD'],
            recovery_timeout=current_app.config['CIRCUIT_BREAKER_RECOVERY_TIMEOUT']
        )

    def validate_token(self, token):
        """Validate JWT token with auth service."""
        def _validate():
            response = requests.post(
                f"{self.base_url}/api/v1/auth/validate",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return response.json()
        
        return self.circuit_breaker.execute(_validate)

    def get_user_permissions(self, token):
        """Get user permissions from auth service."""
        def _get_permissions():
            response = requests.get(
                f"{self.base_url}/api/v1/auth/permissions",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return response.json()
        
        return self.circuit_breaker.execute(_get_permissions)

    def validate_initiative_access(self, token, initiative_id):
        """Validate user's access to a specific initiative."""
        def _validate_access():
            response = requests.post(
                f"{self.base_url}/api/v1/auth/validate-access",
                headers={"Authorization": f"Bearer {token}"},
                json={"resource_type": "initiative", "resource_id": initiative_id}
            )
            response.raise_for_status()
            return response.json()
        
        return self.circuit_breaker.execute(_validate_access)

def auth_required(permissions=None, validate_initiative=False, allowed_roles=None, enforce_tenant=False):
    """
    Decorator to check if user is authenticated and has required permissions.
    
    Args:
        permissions (list): List of required permissions
        validate_initiative (bool): Whether to validate initiative access
        allowed_roles (list): List of allowed roles
        enforce_tenant (bool): Whether to enforce tenant check
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({"error": "No authorization header"}), 401
            try:
                token = auth_header.split(' ')[1]
                auth_client = AuthServiceClient()
                user_info = auth_client.validate_token(token)
                print(f"[DEBUG] user_info: {user_info}")
                # Role check
                if not user_info.get('role'):
                    print("[DEBUG] No role in user_info, returning 401")
                    return jsonify({"error": "Invalid token"}), 401
                if allowed_roles is not None and user_info.get('role') not in allowed_roles:
                    from flask import current_app
                    action = request.method.lower()
                    current_app.logger.warning(f"Unauthorized action: user_id={user_info.get('id')} role={user_info.get('role')} attempted {action} disallowed role access to {request.path}")
                    return jsonify({"error": "Invalid role"}), 403
                # Tenant isolation check BEFORE permission checks
                if validate_initiative and 'initiative_id' in kwargs:
                    from app.models import Initiative
                    initiative = Initiative.query.get(kwargs['initiative_id'])
                    if not initiative or initiative.tenant_id != user_info['tenant_id']:
                        print(f"[DEBUG] Initiative not found or tenant mismatch: initiative={initiative}, user_tenant={user_info['tenant_id']}")
                        return jsonify({"error": "Not found"}), 404
                if enforce_tenant:
                    data = request.get_json(silent=True) or {}
                    if data.get('tenant_id') and data['tenant_id'] != user_info['tenant_id']:
                        print(f"[DEBUG] Tenant mismatch: data_tenant={data.get('tenant_id')}, user_tenant={user_info['tenant_id']}")
                        return jsonify({"error": "Unauthorized tenant access"}), 403
                # Permission check
                if permissions:
                    user_permissions = auth_client.get_user_permissions(token)
                    if isinstance(user_permissions, dict):
                        user_permissions = user_permissions.get('permissions', [])
                    elif isinstance(user_permissions, str):
                        import json
                        user_permissions = json.loads(user_permissions)
                    if not isinstance(user_permissions, list):
                        user_permissions = []
                    print(f"[DEBUG] user_permissions: {user_permissions}, required: {permissions}")
                    if not all(perm in user_permissions for perm in permissions):
                        from flask import current_app
                        current_app.logger.warning(f"Unauthorized action: user_id={user_info.get('id')} role={user_info.get('role')} attempted {permissions} on {request.path}")
                        print("[DEBUG] Insufficient permissions, returning 403")
                        return jsonify({"error": "Insufficient permissions"}), 403
                # Validate initiative access if required (after tenant check)
                if validate_initiative and 'initiative_id' in kwargs:
                    access_info = auth_client.validate_initiative_access(token, kwargs['initiative_id'])
                    print(f"[DEBUG] access_info: {access_info}")
                    if not access_info.get('has_access'):
                        print("[DEBUG] Access denied to initiative, returning 403")
                        return jsonify({"error": "Access denied to initiative"}), 403
                request.user = user_info
                print(f"[DEBUG] Passing to endpoint {f.__name__}")
                return f(*args, **kwargs)
            except requests.exceptions.RequestException:
                return jsonify({"error": "Invalid token"}), 401
            except Exception:
                return jsonify({"error": "Invalid token"}), 401
        return decorated_function
    return decorator 