import pytest
from datetime import datetime, timedelta
from app.models import User, Tenant, UserActivity, Role, Permission, UserRole
from app.extensions import db

@pytest.fixture
def app():
    """Create a Flask app for testing."""
    from app import create_app
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_user(app):
    """Create a test user."""
    user = User(
        username='testuser',
        email='test@example.com',
        password='password123',
        first_name='Test',
        last_name='User',
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def test_role(app):
    """Create a test role."""
    role = Role(
        name='test_role',
        description='Test role for testing'
    )
    db.session.add(role)
    db.session.commit()
    return role

@pytest.fixture
def test_permission(app):
    """Create a test permission."""
    permission = Permission(
        name='test_permission',
        description='Test permission for testing'
    )
    db.session.add(permission)
    db.session.commit()
    return permission

def test_user_creation(app):
    """Test user creation."""
    user = User(
        username='newuser',
        email='new@example.com',
        password='password123',
        first_name='New',
        last_name='User',
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    
    assert user.id is not None
    assert user.username == 'newuser'
    assert user.email == 'new@example.com'
    assert user.first_name == 'New'
    assert user.last_name == 'User'
    assert user.is_active is True
    assert user.created_at is not None
    assert user.updated_at is not None

def test_user_password_hashing(app):
    """Test user password hashing."""
    user = User(
        username='passworduser',
        email='password@example.com',
        password='password123'
    )
    db.session.add(user)
    db.session.commit()
    
    assert user.password != 'password123'
    assert user.check_password('password123') is True
    assert user.check_password('wrongpassword') is False

def test_user_activity_logging(app):
    """Test user activity logging."""
    # Create a user
    user = User(email='test@example.com', password='password123')
    db.session.add(user)
    db.session.commit()
    
    # Create activity
    activity = UserActivity(
        user_id=user.id,
        action='login',
        ip_address='127.0.0.1',
        user_agent='test-agent'
    )
    db.session.add(activity)
    db.session.commit()
    
    # Check activity attributes
    assert activity.user_id == user.id
    assert activity.action == 'login'
    assert activity.ip_address == '127.0.0.1'
    assert activity.user_agent == 'test-agent'
    assert activity.created_at is not None

def test_tenant_creation(app):
    """Test tenant creation."""
    tenant = Tenant(
        name='Test Tenant',
        description='Test Description',
        is_active=True
    )
    db.session.add(tenant)
    db.session.commit()
    
    # Check tenant attributes
    assert tenant.name == 'Test Tenant'
    assert tenant.description == 'Test Description'
    assert tenant.is_active is True
    assert tenant.created_at is not None
    assert tenant.updated_at is not None

def test_role_creation(app):
    """Test role creation."""
    role = Role(
        name='admin',
        description='Administrator role'
    )
    db.session.add(role)
    db.session.commit()
    
    # Check role attributes
    assert role.name == 'admin'
    assert role.description == 'Administrator role'
    assert role.created_at is not None
    assert role.updated_at is not None

def test_permission_creation(app):
    """Test permission creation."""
    permission = Permission(
        name='create_user',
        description='Create new users'
    )
    db.session.add(permission)
    db.session.commit()
    
    # Check permission attributes
    assert permission.name == 'create_user'
    assert permission.description == 'Create new users'
    assert permission.created_at is not None
    assert permission.updated_at is not None

def test_user_role_assignment(app, test_user, test_role):
    """Test user role assignment."""
    user_role = UserRole(user_id=test_user.id, role_id=test_role.id)
    db.session.add(user_role)
    db.session.commit()
    
    assert test_user.roles.count() == 1
    assert test_role in test_user.roles
    assert test_user in test_role.users

def test_role_permission_assignment(app, test_role, test_permission):
    """Test role permission assignment."""
    test_role.permissions.append(test_permission)
    db.session.commit()
    
    assert test_role.permissions.count() == 1
    assert test_permission in test_role.permissions
    assert test_role in test_permission.roles

def test_user_permission_inheritance(app, test_user, test_role, test_permission):
    """Test user permission inheritance through roles."""
    user_role = UserRole(user_id=test_user.id, role_id=test_role.id)
    test_role.permissions.append(test_permission)
    db.session.add(user_role)
    db.session.commit()
    
    assert test_permission in test_user.permissions

def test_user_soft_delete(app, test_user):
    """Test user soft delete."""
    test_user.is_active = False
    db.session.commit()
    
    assert test_user.is_active is False
    assert User.query.filter_by(username='testuser').first() is not None
    assert User.query.filter_by(username='testuser', is_active=True).first() is None

def test_role_unique_name(app, test_role):
    """Test role unique name constraint."""
    duplicate_role = Role(
        name='test_role',
        description='Duplicate role'
    )
    db.session.add(duplicate_role)
    
    with pytest.raises(Exception):
        db.session.commit()

def test_permission_unique_name(app, test_permission):
    """Test permission unique name constraint."""
    duplicate_permission = Permission(
        name='test_permission',
        description='Duplicate permission'
    )
    db.session.add(duplicate_permission)
    
    with pytest.raises(Exception):
        db.session.commit()

def test_user_unique_email(app, test_user):
    """Test user unique email constraint."""
    duplicate_user = User(
        username='anotheruser',
        email='test@example.com',
        password='password123'
    )
    db.session.add(duplicate_user)
    
    with pytest.raises(Exception):
        db.session.commit()

def test_user_unique_username(app, test_user):
    """Test user unique username constraint."""
    duplicate_user = User(
        username='testuser',
        email='another@example.com',
        password='password123'
    )
    db.session.add(duplicate_user)
    
    with pytest.raises(Exception):
        db.session.commit()

def test_user_role_cascade_delete(app, test_user, test_role):
    """Test user role cascade delete."""
    user_role = UserRole(user_id=test_user.id, role_id=test_role.id)
    db.session.add(user_role)
    db.session.commit()
    
    db.session.delete(test_user)
    db.session.commit()
    
    assert UserRole.query.filter_by(user_id=test_user.id).first() is None

def test_role_permission_cascade_delete(app, test_role, test_permission):
    """Test role permission cascade delete."""
    test_role.permissions.append(test_permission)
    db.session.commit()
    
    db.session.delete(test_role)
    db.session.commit()
    
    assert Permission.query.filter_by(id=test_permission.id).first() is not None
    assert test_permission not in test_role.permissions

def test_user_timestamps(app):
    """Test user timestamp updates."""
    user = User(
        username='timestampuser',
        email='timestamp@example.com',
        password='password123'
    )
    db.session.add(user)
    db.session.commit()
    
    created_at = user.created_at
    updated_at = user.updated_at
    
    user.first_name = 'Updated'
    db.session.commit()
    
    assert user.created_at == created_at
    assert user.updated_at > updated_at

def test_user_full_name(app):
    """Test user full name property."""
    user = User(
        username='fullnameuser',
        email='fullname@example.com',
        password='password123',
        first_name='Full',
        last_name='Name'
    )
    
    assert user.full_name == 'Full Name'

def test_user_repr(app, test_user):
    """Test user string representation."""
    assert str(test_user) == f'<User {test_user.username}>'
    assert repr(test_user) == f'<User {test_user.username}>'

def test_role_repr(app, test_role):
    """Test role string representation."""
    assert str(test_role) == f'<Role {test_role.name}>'
    assert repr(test_role) == f'<Role {test_role.name}>'

def test_permission_repr(app, test_permission):
    """Test permission string representation."""
    assert str(test_permission) == f'<Permission {test_permission.name}>'
    assert repr(test_permission) == f'<Permission {test_permission.name}>'

def test_user_role_repr(app, test_user, test_role):
    """Test user role string representation."""
    user_role = UserRole(user_id=test_user.id, role_id=test_role.id)
    assert str(user_role) == f'<UserRole {test_user.username}:{test_role.name}>'
    assert repr(user_role) == f'<UserRole {test_user.username}:{test_role.name}>'

def test_user_tenant_relationship(app):
    """Test user-tenant relationship."""
    # Create a tenant
    tenant = Tenant(name='Test Tenant')
    db.session.add(tenant)
    db.session.commit()
    
    # Create users in the tenant
    user1 = User(email='user1@example.com', password='password123', tenant_id=tenant.id)
    user2 = User(email='user2@example.com', password='password123', tenant_id=tenant.id)
    db.session.add_all([user1, user2])
    db.session.commit()
    
    # Check tenant-users relationship
    assert len(tenant.users) == 2
    assert user1 in tenant.users
    assert user2 in tenant.users
    assert user1.tenant == tenant
    assert user2.tenant == tenant

def test_user_last_login_update(app):
    """Test user last login update."""
    user = User(email='test@example.com', password='password123')
    db.session.add(user)
    db.session.commit()
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Check last login update
    assert user.last_login is not None
    assert isinstance(user.last_login, datetime)

def test_user_activity_relationship(app):
    """Test user-activity relationship."""
    # Create a user
    user = User(email='test@example.com', password='password123')
    db.session.add(user)
    db.session.commit()
    
    # Create activities
    activity1 = UserActivity(user_id=user.id, action='login')
    activity2 = UserActivity(user_id=user.id, action='logout')
    db.session.add_all([activity1, activity2])
    db.session.commit()
    
    # Check user-activities relationship
    assert len(user.activities) == 2
    assert activity1 in user.activities
    assert activity2 in user.activities
    assert activity1.user == user
    assert activity2.user == user

def test_tenant_activation(app):
    """Test tenant activation/deactivation."""
    tenant = Tenant(name='Test Tenant')
    db.session.add(tenant)
    db.session.commit()
    
    # Deactivate tenant
    tenant.is_active = False
    db.session.commit()
    
    # Check tenant status
    assert tenant.is_active is False
    
    # Reactivate tenant
    tenant.is_active = True
    db.session.commit()
    
    # Check tenant status
    assert tenant.is_active is True 