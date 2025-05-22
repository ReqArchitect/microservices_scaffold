from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from flask import abort

# Example decorator for role-based access (expand as needed)
def jwt_required_role(role=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()
            if role and (not identity or identity.get('role') != role):
                abort(403, description='Forbidden: Insufficient role')
            return fn(*args, **kwargs)
        return wrapper
    return decorator
