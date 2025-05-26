import pytest
from application_layer_service.app import create_app, db
from application_layer_service.config import TestConfig
from flask_jwt_extended import create_access_token
from factory import Factory, SubFactory
from app.models import ApplicationComponent, ApplicationService, ApplicationInterface

class TenantFactory(Factory):
    class Meta:
        model = dict  # Replace with actual Tenant model if available
    id = 1
    name = 'Test Tenant'

class UserFactory(Factory):
    class Meta:
        model = dict  # Replace with actual User model if available
    id = 1
    email = 'user@example.com'
    full_name = 'Test User'
    role = 'admin'
    tenant_id = 1

@pytest.fixture
def app():
    app = create_app(TestConfig)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user_factory():
    return UserFactory

@pytest.fixture
def tenant_factory():
    return TenantFactory

@pytest.fixture
def auth_header_factory(app):
    def _make(user=None, role='admin', tenant_id=1):
        with app.app_context():
            token = create_access_token(
                identity=str(user['id']) if user else '1',
                additional_claims={"tenant_id": tenant_id, "role": role}
            )
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    return _make
