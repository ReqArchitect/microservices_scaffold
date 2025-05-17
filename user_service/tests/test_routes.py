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
def test_vendor(app):
    vendor = User(
        email="vendor@example.com",
        password_hash="hashed_password",
        full_name="Vendor User",
        role="vendor",
        tenant_id=None,
        is_active=True,
        is_email_verified=True
    )
    db.session.add(vendor)
    db.session.commit()
    return vendor

@pytest.fixture
def admin_token(test_user):
    return create_access_token(identity={
        "id": test_user.id,
        "tenant_id": test_user.tenant_id,
        "role": test_user.role
    })

@pytest.fixture
def vendor_token(test_vendor):
    return create_access_token(identity={
        "id": test_vendor.id,
        "tenant_id": test_vendor.tenant_id,
        "role": test_vendor.role
    })

@pytest.fixture
def refresh_token(test_user):
    return create_refresh_token(identity={
        "id": test_user.id,
        "tenant_id": test_user.tenant_id,
        "role": test_user.role
    })

def get_auth_header(user_id=1, tenant_id=1, role='admin'):
    token = create_access_token(identity={"id": user_id, "tenant_id": tenant_id, "role": role})
    return {'Authorization': f'Bearer {token}'}

def test_register_user(client):
    response = client.post('/api/v1/users/register', json={
        'email': 'test@example.com',
        'password': 'Test123!@#',
        'full_name': 'Test User',
        'tenant_name': 'Test Tenant'
    })
    if response.status_code != 201:
        print('DEBUG: status_code:', response.status_code)
        print('DEBUG: response.data:', response.data)
    assert response.status_code == 201
    assert response.json['message'] == 'User registered successfully'

def test_register_duplicate_user(client):
    # First registration
    client.post('/api/v1/users/register', json={
        'email': 'test@example.com',
        'password': 'Test123!@#',
        'full_name': 'Test User',
        'tenant_name': 'Test Tenant'
    })
    
    # Second registration with same email
    response = client.post('/api/v1/users/register', json={
        'email': 'test@example.com',
        'password': 'Test123!@#',
        'full_name': 'Test User',
        'tenant_name': 'Test Tenant'
    })
    assert response.status_code == 400
    assert response.json['message'] == 'User already exists'

def test_login_user(client):
    # Register user first
    client.post('/api/v1/users/register', json={
        'email': 'test@example.com',
        'password': 'Test123!@#',
        'full_name': 'Test User',
        'tenant_name': 'Test Tenant'
    })
    
    # Login
    response = client.post('/api/v1/auth/login', json={
        'email': 'test@example.com',
        'password': 'Test123!@#',
        'tenant_name': 'Test Tenant'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json
    assert 'refresh_token' in response.json

def test_get_current_user(client):
    # Register and login
    client.post('/api/v1/users/register', json={
        'email': 'test@example.com',
        'password': 'Test123!@#',
        'full_name': 'Test User',
        'tenant_name': 'Test Tenant'
    })
    
    response = client.get('/api/v1/users/me', headers=get_auth_header())
    assert response.status_code == 200
    assert response.json['email'] == 'test@example.com'
    assert response.json['full_name'] == 'Test User'

def test_update_user(client):
    # Register user
    client.post('/api/v1/users/register', json={
        'email': 'test@example.com',
        'password': 'Test123!@#',
        'full_name': 'Test User',
        'tenant_name': 'Test Tenant'
    })
    
    # Update user
    response = client.put('/api/v1/users/me', 
        headers=get_auth_header(),
        json={
            'full_name': 'Updated Name',
            'preferences': {'theme': 'dark'}
        }
    )
    assert response.status_code == 200
    assert response.json['message'] == 'User updated successfully'

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
        headers=get_auth_header(),
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
    response = client.get('/api/v1/users/me/activity', headers=get_auth_header())
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_health_check(client):
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'
    assert 'timestamp' in response.json 

def test_refresh_token(client, refresh_token):
    """Test refresh token endpoint"""
    response = client.post(
        "/api/v1/users/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "access_token" in data

def test_refresh_token_invalid(client):
    """Test refresh token with invalid token"""
    response = client.post(
        "/api/v1/users/refresh",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401

def test_list_users_admin(client, admin_token, test_tenant):
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
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "users" in data
    assert "total" in data
    assert data["total"] == 4  # 3 new users + 1 admin

def test_list_users_vendor(client, vendor_token, test_tenant):
    """Test list users endpoint for vendor"""
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {vendor_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "users" in data
    assert "total" in data

def test_list_users_unauthorized(client):
    """Test list users endpoint without authentication"""
    response = client.get("/api/v1/users")
    assert response.status_code == 401

def test_update_user_admin(client, admin_token, test_user):
    """Test update user endpoint for admin"""
    response = client.put(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": False}
    )
    assert response.status_code == 200
    updated_user = User.query.get(test_user.id)
    assert not updated_user.is_active

def test_update_user_vendor(client, vendor_token, test_user):
    """Test update user endpoint for vendor"""
    response = client.put(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {vendor_token}"},
        json={"role": "user"}
    )
    assert response.status_code == 200
    updated_user = User.query.get(test_user.id)
    assert updated_user.role == "user"

def test_update_user_unauthorized(client, test_user):
    """Test update user endpoint without authentication"""
    response = client.put(
        f"/api/v1/users/{test_user.id}",
        json={"is_active": False}
    )
    assert response.status_code == 401

def test_get_user_activity(client, admin_token, test_user):
    """Test get user activity endpoint"""
    # Create some activity logs
    for i in range(3):
        activity = UserActivity(
            user_id=test_user.id,
            action=f"test_action_{i}",
            details={"test": "data"},
            ip_address="127.0.0.1"
        )
        db.session.add(activity)
    db.session.commit()

    response = client.get(
        f"/api/v1/users/{test_user.id}/activity",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 3
    assert all("action" in activity for activity in data)
    assert all("details" in activity for activity in data)
    assert all("ip_address" in activity for activity in data)
    assert all("created_at" in activity for activity in data)

def test_get_metrics_vendor(client, vendor_token, test_tenant):
    """Test get metrics endpoint for vendor"""
    # Create some test data
    for i in range(3):
        user = User(
            email=f"user{i}@example.com",
            password_hash="hashed_password",
            full_name=f"User {i}",
            role="user",
            tenant_id=test_tenant.id,
            is_active=True,
            is_email_verified=True
        )
        db.session.add(user)
    db.session.commit()

    response = client.get(
        "/api/v1/users/metrics",
        headers={"Authorization": f"Bearer {vendor_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "users" in data
    assert "tenants" in data
    assert "recent_activities" in data
    assert data["users"]["total"] == 4  # 3 new users + 1 admin
    assert data["users"]["active"] == 4
    assert data["users"]["verified"] == 4
    assert data["tenants"] == 1

def test_get_metrics_unauthorized(client):
    """Test get metrics endpoint without vendor role"""
    response = client.get("/api/v1/users/metrics")
    assert response.status_code == 401

def test_pagination_list_users(client, admin_token, test_tenant):
    """Test pagination in list users endpoint"""
    # Create 15 test users
    for i in range(15):
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

    # Test first page
    response = client.get(
        "/api/v1/users?limit=10&offset=0",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["users"]) == 10
    assert data["total"] == 16  # 15 new users + 1 admin

    # Test second page
    response = client.get(
        "/api/v1/users?limit=10&offset=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["users"]) == 6  # Remaining users

def test_filter_list_users(client, admin_token, test_tenant):
    """Test filtering in list users endpoint"""
    # Create users with different roles
    roles = ["user", "admin", "user"]
    for i, role in enumerate(roles):
        user = User(
            email=f"user{i}@example.com",
            password_hash="hashed_password",
            full_name=f"User {i}",
            role=role,
            tenant_id=test_tenant.id,
            is_active=True
        )
        db.session.add(user)
    db.session.commit()

    # Test role filter
    response = client.get(
        "/api/v1/users?role=user",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert all(user["role"] == "user" for user in data["users"])
    assert data["total"] == 2  # Only users with role "user" 

def test_refresh_token_expired(client, test_user):
    """Test refresh token with expired token"""
    # Create an expired refresh token
    expired_token = create_refresh_token(
        identity={
            "id": test_user.id,
            "tenant_id": test_user.tenant_id,
            "role": test_user.role
        },
        expires_delta=timedelta(microseconds=1)
    )
    import time
    time.sleep(0.1)  # Wait for token to expire
    
    response = client.post(
        "/api/v1/users/refresh",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401

def test_refresh_token_inactive_user(client, test_user):
    """Test refresh token with inactive user"""
    test_user.is_active = False
    db.session.commit()
    
    refresh_token = create_refresh_token(identity={
        "id": test_user.id,
        "tenant_id": test_user.tenant_id,
        "role": test_user.role
    })
    
    response = client.post(
        "/api/v1/users/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert response.status_code == 401

def test_list_users_invalid_pagination(client, admin_token):
    """Test list users with invalid pagination parameters"""
    response = client.get(
        "/api/v1/users?limit=-1&offset=0",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400

    response = client.get(
        "/api/v1/users?limit=0&offset=-1",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400

def test_list_users_invalid_role_filter(client, admin_token):
    """Test list users with invalid role filter"""
    response = client.get(
        "/api/v1/users?role=invalid_role",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["users"]) == 0
    assert data["total"] == 0

def test_update_user_invalid_data(client, admin_token, test_user):
    """Test update user with invalid data"""
    response = client.put(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"role": "invalid_role"}
    )
    assert response.status_code == 400

    response = client.put(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": "not_a_boolean"}
    )
    assert response.status_code == 400

def test_update_user_nonexistent(client, admin_token):
    """Test update non-existent user"""
    response = client.put(
        "/api/v1/users/99999",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": False}
    )
    assert response.status_code == 404

def test_get_user_activity_nonexistent(client, admin_token):
    """Test get activity for non-existent user"""
    response = client.get(
        "/api/v1/users/99999/activity",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404

def test_get_user_activity_invalid_pagination(client, admin_token, test_user):
    """Test get user activity with invalid pagination"""
    response = client.get(
        f"/api/v1/users/{test_user.id}/activity?limit=-1&offset=0",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400

def test_get_metrics_rate_limiting(client, vendor_token):
    """Test metrics endpoint rate limiting"""
    for _ in range(11):  # Assuming rate limit is 10 per minute
        response = client.get(
            "/api/v1/users/metrics",
            headers={"Authorization": f"Bearer {vendor_token}"}
        )
    assert response.status_code == 429

def test_cross_tenant_access(client, admin_token, test_tenant):
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
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 403

def test_user_activity_ordering(client, admin_token, test_user):
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
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify activities are ordered by created_at desc
    timestamps = [datetime.fromisoformat(activity["created_at"]) for activity in data]
    assert timestamps == sorted(timestamps, reverse=True)

def test_user_activity_filtering(client, admin_token, test_user):
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
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]["action"] == "login"

def test_metrics_data_consistency(client, vendor_token, test_tenant):
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
        headers={"Authorization": f"Bearer {vendor_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify metrics consistency
    assert data["users"]["total"] == 5  # 4 new users + 1 admin
    assert data["users"]["active"] == 2  # Only active users
    assert data["users"]["verified"] == 2  # Only verified users 