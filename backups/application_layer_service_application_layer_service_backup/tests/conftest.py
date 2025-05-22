import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from application_layer_service.app import create_app, db
from application_layer_service.config import TestConfig
from flask_jwt_extended import create_access_token
import pytest

@pytest.fixture
def client():
    app = create_app(TestConfig)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

@pytest.fixture
def auth_header():
    app = create_app(TestConfig)
    with app.app_context():
        token = create_access_token(
            identity="1",  # user_id as string
            additional_claims={"tenant_id": 1}
        )
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
