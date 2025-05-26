from flask import request
from flask_jwt_extended import get_jwt_identity

def get_tenant_id():
    """Get tenant ID from JWT token or request data"""
    try:
        # First try to get from JWT token
        identity = get_jwt_identity()
        if isinstance(identity, dict) and 'tenant_id' in identity:
            return identity['tenant_id']
        # Then try to get from request data
        data = request.get_json()
        if data and 'tenant_id' in data:
            return data['tenant_id']
        # Finally try to get from query parameters
        tenant_id = request.args.get('tenant_id')
        if tenant_id:
            return int(tenant_id)
        return None
    except Exception:
        return None 