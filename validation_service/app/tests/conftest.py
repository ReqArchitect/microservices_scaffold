import pytest
from validation_service.app import create_app
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    app = create_app("testing")
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
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