import requests
from functools import wraps
from flask import current_app, request, jsonify
from .circuit_breaker import CircuitBreaker, CircuitBreakerError

class AuthServiceClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or current_app.config['AUTH_SERVICE_URL']
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=current_app.config.get('CIRCUIT_BREAKER_FAILURE_THRESHOLD', 5),
            recovery_timeout=current_app.config.get('CIRCUIT_BREAKER_RECOVERY_TIMEOUT', 60)
        )

    def validate_token(self, token):
        """Validate JWT token with auth service."""
        def _validate():
            response = requests.post(
                f"{self.base_url}/api/v1/auth/validate",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code != 200:
                raise CircuitBreakerError(f"Token validation failed: {response.status_code}")
            return response.json()
        return self.circuit_breaker(_validate)()

    def get_user_permissions(self, token):
        """Get user permissions from auth service."""
        def _get_permissions():
            response = requests.get(
                f"{self.base_url}/api/v1/auth/permissions",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code != 200:
                raise CircuitBreakerError(f"Permission fetch failed: {response.status_code}")
            return response.json()
        return self.circuit_breaker(_get_permissions)()

    def validate_initiative_access(self, token, initiative_id):
        """Validate user access to a specific initiative."""
        def _validate_access():
            response = requests.post(
                f"{self.base_url}/api/v1/auth/validate-access",
                headers={"Authorization": f"Bearer {token}"},
                json={"initiative_id": initiative_id}
            )
            if response.status_code != 200:
                raise CircuitBreakerError(f"Initiative access validation failed: {response.status_code}")
            return response.json()
        return self.circuit_breaker(_validate_access)()

def auth_required(permissions=None, validate_initiative=False):
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
                # Optionally validate initiative access
                if validate_initiative and 'initiative_id' in kwargs:
                    access = auth_client.validate_initiative_access(token, kwargs['initiative_id'])
                    if not access.get('has_access'):
                        return jsonify({"error": "No access to initiative"}), 403
                # Add user info to request context
                request.user = user_info
                return f(*args, **kwargs)
            except CircuitBreakerError as e:
                return jsonify({"error": str(e)}), 503
            except requests.exceptions.RequestException:
                return jsonify({"error": "Authentication service unavailable"}), 503
            except Exception:
                return jsonify({"error": "Invalid token"}), 401
        return decorated_function
    return decorator 