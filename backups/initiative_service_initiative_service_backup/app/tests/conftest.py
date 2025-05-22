import pytest
from app import create_app, db
from app.config import TestingConfig

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers():
    return {
        'X-User-ID': '1',
        'X-Tenant-ID': '1',
        'Content-Type': 'application/json'
    }

@pytest.fixture
def another_auth_headers():
    return {
        'X-User-ID': '2',
        'X-Tenant-ID': '2',
        'Content-Type': 'application/json'
    } 