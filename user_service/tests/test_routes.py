import pytest
from app import create_app, db
from app.models import User, Tenant, UserActivity
from flask_jwt_extended import create_access_token, create_refresh_token
import json
from datetime import datetime, timedelta
from app.utils import validate_password, validate_email_format, generate_password_reset_token, generate_email_verification_token, log_user_activity, get_tenant_id

@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_tenant(app):
    tenant = Tenant(name="test_tenant")
    db.session.add(tenant)
    db.session.commit()
    return tenant

@pytest.fixture
def test_user(app, test_tenant):
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        full_name="Test User",
        role="admin",
        tenant_id=test_tenant.id,
        is_active=True,
        is_email_verified=True
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def test_vendor(app, test_tenant):
    vendor = User(
        email="vendor@example.com",
        password_hash="hashed_password",
        full_name="Vendor User",
        role="vendor",
        tenant_id=test_tenant.id,
        is_active=True,
        is_email_verified=True
    )
    db.session.add(vendor)
    db.session.commit()
    return vendor

def get_gateway_headers(user_id=1, tenant_id=1, role='admin'):
    return {
        'X-User-ID': str(user_id),
        'X-Tenant-ID': str(tenant_id),
        'X-Role': role
    }

def test_register_user(client):
    response = client.post('/api/v1/users/register', json={
        'email': 'test@example.com',
        'password': 'Test123!@#',
        'full_name': 'Test User',
        'tenant_name': 'Test Tenant'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'User registered successfully'

def test_register_duplicate_user(client):
    client.post('/api/v1/users/register', json={
        'email': 'test@example.com',
        'password': 'Test123!@#',
        'full_name': 'Test User',
        'tenant_name': 'Test Tenant'
    })
    response = client.post('/api/v1/users/register', json={
        'email': 'test@example.com',
        'password': 'Test123!@#',
        'full_name': 'Test User',
        'tenant_name': 'Test Tenant'
    })
    assert response.status_code == 400
    assert response.json['message'] == 'User already exists'

def test_login_user(client):
    client.post('/api/v1/users/register', json={
        'email': 'test@example.com',
        'password': 'Test123!@#',
        'full_name': 'Test User',
        'tenant_name': 'Test Tenant'
    })
    response = client.post('/api/v1/auth/login', json={
        'email': 'test@example.com',
        'password': 'Test123!@#',
        'tenant_name': 'Test Tenant'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json
    assert 'refresh_token' in response.json

def test_login_user_invalid(client):
    response = client.post('/api/v1/auth/login', json={
        'email': 'notfound@example.com',
        'password': 'wrong',
        'tenant_name': 'Test Tenant'
    })
    assert response.status_code in (400, 401)

def test_login_user_missing_fields(client):
    response = client.post('/api/v1/auth/login', json={})
    assert response.status_code == 400

def test_get_current_user(client, auth_header_factory):
    client.post('/api/v1/users/register', json={
        'email': 'test@example.com',
        'password': 'Test123!@#',
        'full_name': 'Test User',
        'tenant_name': 'Test Tenant'
    })
    headers = auth_header_factory(role='user')
    response = client.get('/api/v1/users/me', headers=headers)
    assert response.status_code == 200
    assert response.json['email'] == 'test@example.com'
    assert response.json['full_name'] == 'Test User'

def test_get_current_user_unauthorized(client):
    response = client.get('/api/v1/users/me')
    assert response.status_code == 401

def test_update_user(client, auth_header_factory):
    client.post('/api/v1/users/register', json={
        'email': 'test@example.com',
        'password': 'Test123!@#',
        'full_name': 'Test User',
        'tenant_name': 'Test Tenant'
    })
    headers = auth_header_factory(role='user')
    response = client.put('/api/v1/users/me', headers=headers, json={
        'full_name': 'Updated Name',
        'preferences': {'theme': 'dark'}
    })
    assert response.status_code == 200
    assert response.json['message'] == 'User updated successfully'

def test_update_user_unauthorized(client):
    response = client.put('/api/v1/users/me', json={'full_name': 'Updated'})
    assert response.status_code == 401

@pytest.mark.parametrize("role", ["vendor_admin", "tenant_admin"])
def test_list_users_rbac(client, auth_header_factory, role):
    headers = auth_header_factory(role=role)
    response = client.get('/api/v1/users', headers=headers)
    assert response.status_code == 200
    assert 'users' in response.json

@pytest.mark.parametrize("role", ["user", "guest", None])
def test_list_users_forbidden(client, auth_header_factory, role):
    headers = auth_header_factory(role=role) if role else {}
    response = client.get('/api/v1/users', headers=headers)
    assert response.status_code in (401, 403)

def test_cross_tenant_access_forbidden(client, auth_header_factory):
    # Register user in tenant 1
    client.post('/api/v1/users/register', json={
        'email': 'test@example.com',
        'password': 'Test123!@#',
        'full_name': 'Test User',
        'tenant_name': 'Tenant1'
    })
    # Try to access as user from tenant 2
    headers = auth_header_factory(role='user', tenant_id=2)
    response = client.get('/api/v1/users/me', headers=headers)
    assert response.status_code in (401, 403)

def test_change_password(client):
    # Register user
    client.post('/api/v1/users/register', json={
        'email': 'test@example.com',
        'password': 'Test123!@#',
        'full_name': 'Test User',
        'tenant_name': 'Test Tenant'
    })
    
    # Change password
    response = client.put('/api/v1/users/me/password',
        headers=get_gateway_headers(),
        json={
            'current_password': 'Test123!@#',
            'new_password': 'NewTest123!@#'
        }
    )
    assert response.status_code == 200
    assert response.json['message'] == 'Password changed successfully'

def test_request_password_reset(client):
    # Register user
    client.post('/api/v1/users/register', json={
        'email': 'test@example.com',
        'password': 'Test123!@#',
        'full_name': 'Test User',
        'tenant_name': 'Test Tenant'
    })
    
    # Request password reset
    response = client.post('/api/v1/users/request-password-reset', json={
        'email': 'test@example.com',
        'tenant_name': 'Test Tenant'
    })
    assert response.status_code == 200

def test_get_user_activity(client):
    # Register user
    client.post('/api/v1/users/register', json={
        'email': 'test@example.com',
        'password': 'Test123!@#',
        'full_name': 'Test User',
        'tenant_name': 'Test Tenant'
    })
    
    # Get activity
    response = client.get('/api/v1/users/me/activity', headers=get_gateway_headers())
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_health_check(client):
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'
    assert 'timestamp' in response.json 

def test_refresh_token(client, test_user):
    """Test refresh token endpoint"""
    response = client.post(
        "/api/v1/users/refresh",
        headers=get_gateway_headers(test_user.id, test_user.tenant_id, test_user.role)
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "access_token" in data

def test_refresh_token_invalid(client):
    """Test refresh token with invalid token"""
    response = client.post(
        "/api/v1/users/refresh",
        headers=get_gateway_headers(1, 1, 'invalid_role')
    )
    assert response.status_code == 401

def test_list_users_admin(client, test_user, test_tenant):
    """Test list users endpoint for admin"""
    # Create additional test users
    for i in range(3):
        user = User(
            email=f"user{i}@example.com",
            password_hash="hashed_password",
            full_name=f"User {i}",
            role="user",
            tenant_id=test_tenant.id,
            is_active=True
        )
        db.session.add(user)
    db.session.commit()

    response = client.get(
        "/api/v1/users",
        headers=get_gateway_headers()
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "users" in data
    assert "total" in data
    assert data["total"] == 4  # 3 new users + 1 admin

def test_list_users_vendor(client, test_vendor, test_tenant):
    """Test list users endpoint for vendor"""
    response = client.get(
        "/api/v1/users",
        headers=get_gateway_headers(test_vendor.id, test_vendor.tenant_id, test_vendor.role)
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "users" in data
    assert "total" in data

def test_list_users_unauthorized(client):
    """Test list users endpoint without authentication"""
    response = client.get("/api/v1/users")
    assert response.status_code == 401

def test_update_user_admin(client, test_user):
    """Test update user endpoint for admin"""
    response = client.put(
        f"/api/v1/users/{test_user.id}",
        headers=get_gateway_headers(),
        json={"is_active": False}
    )
    assert response.status_code == 200
    updated_user = User.query.get(test_user.id)
    assert not updated_user.is_active

def test_update_user_vendor(client, test_vendor):
    """Test update user endpoint for vendor"""
    response = client.put(
        f"/api/v1/users/{test_vendor.id}",
        headers=get_gateway_headers(test_vendor.id, test_vendor.tenant_id, test_vendor.role),
        json={"role": "user"}
    )
    assert response.status_code == 200
    updated_user = User.query.get(test_vendor.id)
    assert updated_user.role == "user"

def test_update_user_invalid_data(client, test_user):
    """Test update user with invalid data"""
    response = client.put(
        f"/api/v1/users/{test_user.id}",
        headers=get_gateway_headers(),
        json={"role": "invalid_role"}
    )
    assert response.status_code == 400

    response = client.put(
        f"/api/v1/users/{test_user.id}",
        headers=get_gateway_headers(),
        json={"is_active": "not_a_boolean"}
    )
    assert response.status_code == 400

def test_update_user_nonexistent(client):
    """Test update non-existent user"""
    response = client.put(
        "/api/v1/users/99999",
        headers=get_gateway_headers(),
        json={"is_active": False}
    )
    assert response.status_code == 404

def test_get_user_activity_nonexistent(client):
    """Test get activity for non-existent user"""
    response = client.get(
        "/api/v1/users/99999/activity",
        headers=get_gateway_headers()
    )
    assert response.status_code == 404

def test_get_user_activity_invalid_pagination(client, test_user):
    """Test get user activity with invalid pagination"""
    response = client.get(
        f"/api/v1/users/{test_user.id}/activity?limit=-1&offset=0",
        headers=get_gateway_headers()
    )
    assert response.status_code == 400

def test_get_metrics_rate_limiting(client, test_vendor):
    """Test metrics endpoint rate limiting"""
    for _ in range(11):  # Assuming rate limit is 10 per minute
        response = client.get(
            "/api/v1/users/metrics",
            headers=get_gateway_headers(test_vendor.id, test_vendor.tenant_id, test_vendor.role)
        )
    assert response.status_code == 429

def test_cross_tenant_access(client, test_user, test_tenant):
    """Test cross-tenant access prevention"""
    # Create another tenant and user
    other_tenant = Tenant(name="other_tenant")
    db.session.add(other_tenant)
    db.session.commit()
    
    other_user = User(
        email="other@example.com",
        password_hash="hashed_password",
        full_name="Other User",
        role="user",
        tenant_id=other_tenant.id,
        is_active=True
    )
    db.session.add(other_user)
    db.session.commit()
    
    # Try to access other tenant's user
    response = client.get(
        f"/api/v1/users/{other_user.id}/activity",
        headers=get_gateway_headers()
    )
    assert response.status_code == 403

def test_user_activity_ordering(client, test_user):
    """Test user activity ordering"""
    # Create activities with different timestamps
    activities = []
    for i in range(3):
        activity = UserActivity(
            user_id=test_user.id,
            action=f"test_action_{i}",
            details={"test": "data"},
            ip_address="127.0.0.1",
            created_at=datetime.utcnow() - timedelta(minutes=i)
        )
        activities.append(activity)
        db.session.add(activity)
    db.session.commit()
    
    response = client.get(
        f"/api/v1/users/{test_user.id}/activity",
        headers=get_gateway_headers()
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify activities are ordered by created_at desc
    timestamps = [datetime.fromisoformat(activity["created_at"]) for activity in data]
    assert timestamps == sorted(timestamps, reverse=True)

def test_user_activity_filtering(client, test_user):
    """Test user activity filtering"""
    # Create activities with different actions
    actions = ["login", "update_profile", "change_password"]
    for action in actions:
        activity = UserActivity(
            user_id=test_user.id,
            action=action,
            details={"test": "data"},
            ip_address="127.0.0.1"
        )
        db.session.add(activity)
    db.session.commit()
    
    # Test filtering by action
    response = client.get(
        f"/api/v1/users/{test_user.id}/activity?action=login",
        headers=get_gateway_headers()
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]["action"] == "login"

def test_metrics_data_consistency(client, test_vendor, test_tenant):
    """Test metrics data consistency"""
    # Create users with different states
    users = [
        {"is_active": True, "is_email_verified": True},
        {"is_active": True, "is_email_verified": False},
        {"is_active": False, "is_email_verified": True},
        {"is_active": False, "is_email_verified": False}
    ]
    
    for i, user_data in enumerate(users):
        user = User(
            email=f"user{i}@example.com",
            password_hash="hashed_password",
            full_name=f"User {i}",
            role="user",
            tenant_id=test_tenant.id,
            **user_data
        )
        db.session.add(user)
    db.session.commit()
    
    response = client.get(
        "/api/v1/users/metrics",
        headers=get_gateway_headers(test_vendor.id, test_vendor.tenant_id, test_vendor.role)
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify metrics consistency
    assert data["users"]["total"] == 5  # 4 new users + 1 admin
    assert data["users"]["active"] == 2  # Only active users
    assert data["users"]["verified"] == 2  # Only verified users 