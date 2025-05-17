import pytest
from app import create_app
from app.extensions import db
from app.models import BusinessCase

@pytest.fixture
def app():
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def business_case(app):
    bc = BusinessCase()
    db.session.add(bc)
    db.session.commit()
    return bc.id 