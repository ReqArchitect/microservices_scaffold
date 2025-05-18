import pytest
import responses
from app import create_app, db
from app.models import BusinessCase
from config import TestConfig

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_token():
    return 'admin_token'

@pytest.fixture
def another_token():
    return 'admin_token_tenant2'

@pytest.fixture
def auth_headers(test_token):
    return {
        'Authorization': f'Bearer {test_token}',
        'Content-Type': 'application/json'
    }

@pytest.fixture
def another_auth_headers(another_token):
    return {
        'Authorization': f'Bearer {another_token}',
        'Content-Type': 'application/json'
    }

@pytest.fixture(autouse=True)
def mock_auth_service_endpoints(app):
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        def validate_token_callback(request):
            auth_header = request.headers.get('Authorization', '')
            token = auth_header.replace('Bearer ', '')
            if token == 'admin_token':
                return (200, {}, '{"id": 1, "email": "test@example.com", "role": "admin", "roles": ["admin"], "tenant_id": 1}')
            elif token == 'admin_token_tenant2':
                return (200, {}, '{"id": 2, "email": "test2@example.com", "role": "admin", "roles": ["admin"], "tenant_id": 2}')
            else:
                return (401, {}, '{"error": "Invalid token"}')
        rsps.add_callback(
            responses.POST,
            f"{app.config['AUTH_SERVICE_URL']}/api/v1/auth/validate",
            callback=validate_token_callback,
            content_type='application/json',
        )
        def get_permissions_callback(request):
            token = request.headers.get('Authorization', '')
            if 'admin_token' in token:
                return (200, {}, '["create_business_case", "update_business_case", "delete_business_case"]')
            else:
                return (200, {}, '[]')
        rsps.add_callback(
            responses.GET,
            f"{app.config['AUTH_SERVICE_URL']}/api/v1/auth/permissions",
            callback=get_permissions_callback,
            content_type='application/json',
        )
        yield rsps 