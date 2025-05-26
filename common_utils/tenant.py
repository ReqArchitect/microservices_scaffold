"""
Multi-tenant utilities for ReqArchitect services
"""
from flask import request, g, jsonify
from functools import wraps
from werkzeug.local import LocalProxy

# Current tenant accessor
current_tenant = LocalProxy(lambda: getattr(g, 'tenant', None))

def tenant_required(f):
    """
    Decorator to ensure a tenant is specified.
    Must be applied after authentication middleware.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get tenant from JWT if available
        from flask_jwt_extended import get_jwt
        try:
            claims = get_jwt()
            tenant_id = claims.get('tenant_id')
        except:
            tenant_id = None
            
        # If not in JWT, try header
        if not tenant_id:
            tenant_id = request.headers.get('X-Tenant-ID')
            
        if not tenant_id:
            return jsonify({"error": "Tenant ID is required"}), 400
        
        g.tenant = tenant_id
        return f(*args, **kwargs)
    return decorated_function

def tenant_filter(query, model_class):
    """
    Apply tenant filtering to a SQLAlchemy query
    """
    if current_tenant and hasattr(model_class, 'tenant_id'):
        return query.filter(model_class.tenant_id == current_tenant)
    return query

def set_tenant_on_model(model):
    """
    Set tenant ID on a model before saving
    """
    if current_tenant and hasattr(model, 'tenant_id') and model.tenant_id is None:
        model.tenant_id = current_tenant
    return model

class TenantModelMixin:
    """
    Mixin for SQLAlchemy models that are tenant-specific
    """
    @classmethod
    def get_for_tenant(cls, id, tenant_id=None):
        """Get a record for the current tenant or specified tenant"""
        tenant_id = tenant_id or current_tenant
        if tenant_id is None:
            return None
        return cls.query.filter_by(id=id, tenant_id=tenant_id).first()
    
    @classmethod
    def get_all_for_tenant(cls, tenant_id=None):
        """Get all records for the current tenant or specified tenant"""
        tenant_id = tenant_id or current_tenant
        if tenant_id is None:
            return []
        return cls.query.filter_by(tenant_id=tenant_id).all()
