from flask import Blueprint, request, jsonify
from .models import User, Tenant, UserActivity
from . import db
from .utils.versioning import api_version
from .utils.identity import get_identity
import logging
from flask_jwt_extended import jwt_required

logger = logging.getLogger(__name__)
bp = Blueprint('admin', __name__, url_prefix='/v1/admin')

def admin_required(fn):
    """Decorator to require admin role."""
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id, tenant_id, role = get_identity()
        user = User.query.get(user_id)
        all_users = User.query.all()
        logger.debug(f"admin_required: all_users={[{'id': u.id, 'email': u.email, 'role': u.role, 'tenant_id': u.tenant_id} for u in all_users]}")
        logger.debug(f"admin_required: user_id={user_id}, tenant_id={tenant_id}, role={role}, user={user}")
        if not user or user.role not in ['vendor_admin', 'tenant_admin']:
            logger.debug(f"admin_required: access denied for user_id={user_id}, user.role={getattr(user, 'role', None)}")
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

@bp.route('/users', methods=['GET'])
@admin_required
@api_version('1.0')
def list_users():
    """List users (filtered by tenant for tenant admins)."""
    try:
        user_id, tenant_id = get_identity()
        current_user = User.query.get(user_id)
        
        # Build query based on admin role
        query = User.query
        if current_user.role == 'tenant_admin':
            query = query.filter_by(tenant_id=tenant_id)
            
        # Apply filters
        if request.args.get('role'):
            query = query.filter_by(role=request.args.get('role'))
        if request.args.get('is_active') is not None:
            query = query.filter_by(is_active=request.args.get('is_active') == 'true')
            
        # Pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        users = query.paginate(page=page, per_page=per_page)
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': users.page
        }), 200
        
    except Exception as e:
        logger.error(f"List users error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
@api_version('1.0')
def get_user(user_id):
    """Get user details."""
    try:
        user_id, tenant_id = get_identity()
        current_user = User.query.get(user_id)
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Check tenant access
        if current_user.role == 'tenant_admin' and user.tenant_id != tenant_id:
            return jsonify({'error': 'Access denied'}), 403
            
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
@api_version('1.0')
def update_user(user_id):
    """Update user details."""
    try:
        user_id, tenant_id = get_identity()
        current_user = User.query.get(user_id)
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Check tenant access
        if current_user.role == 'tenant_admin' and user.tenant_id != tenant_id:
            return jsonify({'error': 'Access denied'}), 403
            
        data = request.get_json()
        
        # Update fields
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'role' in data and current_user.role == 'vendor_admin':
            user.role = data['role']
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'preferences' in data:
            user.preferences = data['preferences']
            
        # Log activity
        activity = UserActivity(
            user_id=user_id,
            action='admin_update_user',
            details={
                'target_user_id': user_id,
                'updated_fields': list(data.keys())
            },
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Update user error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
@api_version('1.0')
def delete_user(user_id):
    """Delete user."""
    try:
        user_id, tenant_id = get_identity()
        current_user = User.query.get(user_id)
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Check tenant access
        if current_user.role == 'tenant_admin' and user.tenant_id != tenant_id:
            return jsonify({'error': 'Access denied'}), 403
            
        # Log activity before deletion
        activity = UserActivity(
            user_id=user_id,
            action='admin_delete_user',
            details={'target_user_id': user_id},
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Delete user error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/tenants', methods=['GET'])
@admin_required
@api_version('1.0')
def list_tenants():
    """List tenants (vendor admin only)."""
    try:
        user_id, tenant_id = get_identity()
        current_user = User.query.get(user_id)
        
        if current_user.role != 'vendor_admin':
            return jsonify({'error': 'Vendor admin access required'}), 403
            
        # Apply filters
        query = Tenant.query
        if request.args.get('is_active') is not None:
            query = query.filter_by(is_active=request.args.get('is_active') == 'true')
            
        # Pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        tenants = query.paginate(page=page, per_page=per_page)
        
        return jsonify({
            'tenants': [tenant.to_dict() for tenant in tenants.items],
            'total': tenants.total,
            'pages': tenants.pages,
            'current_page': tenants.page
        }), 200
        
    except Exception as e:
        logger.error(f"List tenants error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/tenants', methods=['POST'])
@admin_required
@api_version('1.0')
def create_tenant():
    """Create new tenant (vendor admin only)."""
    try:
        user_id, tenant_id = get_identity()
        current_user = User.query.get(user_id)
        
        if current_user.role != 'vendor_admin':
            return jsonify({'error': 'Vendor admin access required'}), 403
            
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Tenant name is required'}), 400
            
        # Check if tenant exists
        if Tenant.query.filter_by(name=data['name']).first():
            return jsonify({'error': 'Tenant already exists'}), 409
            
        # Create tenant
        tenant = Tenant(
            name=data['name'],
            is_active=data.get('is_active', True),
            settings=data.get('settings', {})
        )
        
        db.session.add(tenant)
        
        # Log activity
        activity = UserActivity(
            user_id=user_id,
            action='create_tenant',
            details={'tenant_name': tenant.name},
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify(tenant.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Create tenant error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/tenants/<int:tenant_id>', methods=['GET'])
@admin_required
@api_version('1.0')
def get_tenant(tenant_id):
    """Get tenant details."""
    try:
        user_id, tenant_id = get_identity()
        current_user = User.query.get(user_id)
        
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
            
        # Check tenant access
        if current_user.role == 'tenant_admin' and tenant.id != tenant_id:
            return jsonify({'error': 'Access denied'}), 403
            
        return jsonify(tenant.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Get tenant error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/tenants/<int:tenant_id>', methods=['PUT'])
@admin_required
@api_version('1.0')
def update_tenant(tenant_id):
    """Update tenant details."""
    try:
        user_id, tenant_id = get_identity()
        current_user = User.query.get(user_id)
        
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
            
        # Check tenant access
        if current_user.role == 'tenant_admin' and tenant.id != tenant_id:
            return jsonify({'error': 'Access denied'}), 403
            
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            tenant.name = data['name']
        if 'is_active' in data and current_user.role == 'vendor_admin':
            tenant.is_active = data['is_active']
        if 'settings' in data:
            tenant.settings = data['settings']
            
        # Log activity
        activity = UserActivity(
            user_id=user_id,
            action='update_tenant',
            details={
                'tenant_id': tenant_id,
                'updated_fields': list(data.keys())
            },
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify(tenant.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Update tenant error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/tenants/<int:tenant_id>', methods=['DELETE'])
@admin_required
@api_version('1.0')
def delete_tenant(tenant_id):
    """Delete tenant (vendor admin only)."""
    try:
        user_id, tenant_id = get_identity()
        current_user = User.query.get(user_id)
        
        if current_user.role != 'vendor_admin':
            return jsonify({'error': 'Vendor admin access required'}), 403
            
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
            
        # Log activity before deletion
        activity = UserActivity(
            user_id=user_id,
            action='delete_tenant',
            details={'tenant_id': tenant_id},
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        
        db.session.delete(tenant)
        db.session.commit()
        
        return jsonify({'message': 'Tenant deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Delete tenant error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500 