import sys
import os

# Ensure the user_service directory is in the PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
from app import create_app, db
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
    })
    
    # Create the database and load test data
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()

@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app."""
    return app.test_client()