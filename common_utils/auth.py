from flask_jwt_extended import get_jwt_identity, get_jwt, JWTManager, verify_jwt_in_request
from authlib.integrations.flask_client import OAuth
from functools import wraps
from flask import jsonify, request, g, abort
import os

oauth = OAuth()

def get_user_and_tenant():
    user_id = int(get_jwt_identity())
    tenant_id = get_jwt().get('tenant_id')
    return user_id, tenant_id

def init_jwt(app):
    jwt = JWTManager(app)
    return jwt

def init_oauth(app):
    oauth.init_app(app)
    app.config['OAUTH2_CLIENT_ID'] = os.environ.get('OAUTH2_CLIENT_ID')
    app.config['OAUTH2_CLIENT_SECRET'] = os.environ.get('OAUTH2_CLIENT_SECRET')
    app.config['OAUTH2_SERVER_METADATA_URL'] = os.environ.get('OAUTH2_SERVER_METADATA_URL')
    oauth.register(
        name='oidc',
        client_id=app.config['OAUTH2_CLIENT_ID'],
        client_secret=app.config['OAUTH2_CLIENT_SECRET'],
        server_metadata_url=app.config['OAUTH2_SERVER_METADATA_URL'],
        client_kwargs={'scope': 'openid profile email'}
    )
    return oauth

def rbac_required(permissions=None, roles=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()
            if roles and identity.get('role') not in roles:
                return jsonify({'error': 'Forbidden: Insufficient role'}), 403
            if permissions:
                user_perms = identity.get('permissions', [])
                if not all(perm in user_perms for perm in permissions):
                    return jsonify({'error': 'Forbidden: Insufficient permissions'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator 