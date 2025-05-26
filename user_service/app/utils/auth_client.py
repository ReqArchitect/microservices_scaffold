import requests
from functools import wraps
from flask import current_app, request, jsonify
from .circuit_breaker import CircuitBreaker

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

def auth_required(permissions=None):
    """Decorator to check if user is authenticated and has required permissions."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({"error": "No authorization header"}), 401

            try:
                token = auth_header.split(' ')[1]
                auth_client = AuthServiceClient()
                
                # Validate token
                user_info = auth_client.validate_token(token)
                
                # Check permissions if required
                if permissions:
                    user_permissions = auth_client.get_user_permissions(token)
                    if not all(perm in user_permissions for perm in permissions):
                        return jsonify({"error": "Insufficient permissions"}), 403
                
                # Add user info to request context
                request.user = user_info
                
                return f(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                return jsonify({"error": "Authentication service unavailable"}), 503
            except Exception as e:
                return jsonify({"error": "Invalid token"}), 401
                
        return decorated_function
    return decorator 