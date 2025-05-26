import pytest
import os
from app import create_app, db
from flask_jwt_extended import create_access_token
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    
    # Create the database and load test data
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def auth_header_factory(app):
    def _make(user_id=1, role='admin', tenant_id=1):
        with app.app_context():
            token = create_access_token(
                identity=str(user_id),
                additional_claims={"tenant_id": tenant_id, "role": role}
            )
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    return _make

@pytest.fixture
def log_capture():
    # TODO: Implement log capture fixture
    pass

@pytest.fixture
def audit_log_capture():
    # TODO: Implement audit log capture fixture
    pass

@pytest.fixture(params=["vendor_admin", "tenant_admin", "user"])
def rbac_role(request):
    return request.param

@pytest.fixture(params=[1, 2])
def tenant_id(request):
    return request.param