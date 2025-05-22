import pytest
import responses
from flask import current_app
from common_utils.auth_client import AuthServiceClient, auth_required

@pytest.fixture
def auth_client(app):
    """Create an auth client for testing."""
    return AuthServiceClient()

@pytest.fixture
def mock_auth_responses():
    """Mock responses from auth service."""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        # Mock token validation
        rsps.add(
            responses.POST,
            f"{current_app.config['AUTH_SERVICE_URL']}/api/v1/auth/validate",
            json={
                "id": 1,
                "email": "test@example.com",
                "role": "admin",
                "roles": ["admin"],
                "tenant_id": 1
            },
            status=200
        )
        
        # Mock permissions check
        rsps.add(
            responses.GET,
            f"{current_app.config['AUTH_SERVICE_URL']}/api/v1/auth/permissions",
            json=["create_initiative", "update_initiative", "list_initiatives"],
            status=200
        )
        
        # Mock initiative access check
        rsps.add(
            responses.POST,
            f"{current_app.config['AUTH_SERVICE_URL']}/api/v1/auth/validate-access",
            json={"has_access": True},
            status=200
        )
        
        yield rsps

def test_validate_token(auth_client, mock_auth_responses):
    """Test token validation."""
    result = auth_client.validate_token("test_token")
    assert result["id"] == 1
    assert result["email"] == "test@example.com"
    assert "admin" in result["roles"]

def test_get_user_permissions(auth_client, mock_auth_responses):
    """Test getting user permissions."""
    permissions = auth_client.get_user_permissions("test_token")
    assert "create_initiative" in permissions
    assert "update_initiative" in permissions
    assert "list_initiatives" in permissions

def test_validate_initiative_access(auth_client, mock_auth_responses):
    """Test initiative access validation."""
    result = auth_client.validate_initiative_access("test_token", 1)
    assert result["has_access"] is True

def test_auth_error_handling(app, auth_client):
    """Test error handling for auth service failures."""
    error_cases = [
        (401, "Invalid token"),
        (403, "Insufficient permissions"),
        (500, "Authentication service unavailable")
    ]
    
    for status_code, expected_error in error_cases:
        with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
            rsps.add(
                responses.POST,
                f"{current_app.config['AUTH_SERVICE_URL']}/api/v1/auth/validate",
                json={"error": "Error message"},
                status=status_code
            )
            
            with pytest.raises(Exception) as exc:
                auth_client.validate_token("test_token")
            
            if status_code == 500:
                assert "500" in str(exc.value)
            else:
                assert str(status_code) in str(exc.value)

def test_circuit_breaker_open(app, auth_client):
    """Test circuit breaker opens after multiple failures."""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        # Configure to fail 5 times (threshold)
        for _ in range(5):
            rsps.add(
                responses.POST,
                f"{current_app.config['AUTH_SERVICE_URL']}/api/v1/auth/validate",
                json={"error": "Service error"},
                status=500
            )
        
        # Make 5 failing requests
        for _ in range(5):
            with pytest.raises(Exception):
                auth_client.validate_token("test_token")
        
        # Next request should fail fast with circuit breaker
        with pytest.raises(CircuitBreakerError) as exc:
            auth_client.validate_token("test_token")
        assert "circuit breaker is open" in str(exc.value).lower()

def test_auth_required_decorator(app, client, mock_auth_responses):
    """Test auth_required decorator."""
    # Create a test route
    @app.route('/test')
    @auth_required(permissions=['create_initiative'])
    def test_route():
        return {"message": "success"}
    
    # Test without auth header
    response = client.get('/test')
    assert response.status_code == 401
    
    # Test with valid auth header
    response = client.get('/test', headers={'Authorization': 'Bearer admin_token'})
    assert response.status_code == 200
    assert response.json["message"] == "success"

def test_auth_required_with_initiative(app, client, mock_auth_responses):
    """Test auth_required decorator with initiative validation."""
    # Insert a dummy initiative with id=1
    from app import db
    from app.models import Initiative
    with app.app_context():
        if not Initiative.query.get(1):
            initiative = Initiative(id=1, title='Test', description='Test', strategic_objective='Test', tenant_id=1, owner_id=1, created_by=1, updated_by=1)
            db.session.add(initiative)
            db.session.commit()
    # Create a test route
    @app.route('/test/<int:initiative_id>')
    @auth_required(validate_initiative=True)
    def test_route(initiative_id):
        return {"message": "success"}
    # Test with valid auth and initiative access
    response = client.get('/test/1', headers={'Authorization': 'Bearer admin_token'})
    assert response.status_code == 200
    assert response.json["message"] == "success"

def test_auth_required_insufficient_permissions(app, client):
    """Test auth_required decorator with insufficient permissions."""
    with responses.RequestsMock() as rsps:
        # Mock token validation
        rsps.add(
            responses.POST,
            f"{current_app.config['AUTH_SERVICE_URL']}/api/v1/auth/validate",
            json={"id": 1, "email": "test@example.com", "role": "user"},
            status=200
        )
        # Mock permissions (empty list)
        rsps.add(
            responses.GET,
            f"{current_app.config['AUTH_SERVICE_URL']}/api/v1/auth/permissions",
            json=[],
            status=200
        )
        # Create a test route
        @app.route('/test')
        @auth_required(permissions=['create_initiative'])
        def test_route():
            return {"message": "success"}
        # Test with insufficient permissions
        response = client.get('/test', headers={'Authorization': 'Bearer test_token'})
        assert response.status_code == 403
        assert "insufficient permissions" in response.json["error"].lower() 