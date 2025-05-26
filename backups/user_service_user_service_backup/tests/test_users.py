import pytest
from datetime import datetime
import time
import sys
from app import create_app, db
from app.models import User, Tenant, UserActivity
import traceback
import json
from app.utils import validate_password, validate_email_format, generate_password_reset_token, generate_email_verification_token, log_user_activity, get_tenant_id

@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'RATELIMIT_ENABLED': False  # Disable rate limiting during tests
    })
    return app

@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app."""
    return app.test_client()

def cleanup_database(app):
    """Clean up the database before running tests"""
    with app.app_context():
        try:
            # Start a transaction
            db.session.begin_nested()
            
            try:
                # Delete all records from tables
                UserActivity.query.delete()
                User.query.delete()
                Tenant.query.delete()
                
                # Commit the changes
                db.session.commit()
                print("Database cleaned up successfully")
            except Exception as e:
                db.session.rollback()
                print(f"Error during cleanup: {str(e)}")
                print(f"Traceback: {traceback.format_exc()}")
                raise
        except Exception as e:
            print(f"Error cleaning up database: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")

def test_register_users(app, client):
    # Clean up database before running tests
    cleanup_database(app)
    
    # Test data for user registration
    users = [
        # Vendor admin
        {
            "email": "vendor_admin@example.com",
            "password": "Admin123!",
            "full_name": "Vendor Admin",
            "tenant_name": "SaaS Vendor",
            "role": "vendor_admin"
        },
        # Tenant admins
        {
            "email": "admin@acme.com",
            "password": "Admin123!",
            "full_name": "Acme Admin",
            "tenant_name": "Acme Corp",
            "role": "tenant_admin"
        },
        {
            "email": "admin@globex.com",
            "password": "Admin123!",
            "full_name": "Globex Admin",
            "tenant_name": "Globex Inc",
            "role": "tenant_admin"
        },
        {
            "email": "admin@initech.com",
            "password": "Admin123!",
            "full_name": "Initech Admin",
            "tenant_name": "Initech Ltd",
            "role": "tenant_admin"
        },
        # Regular users
        {
            "email": "user1@acme.com",
            "password": "User123!",
            "full_name": "John Acme",
            "tenant_name": "Acme Corp"
        },
        {
            "email": "user2@acme.com",
            "password": "User123!",
            "full_name": "Jane Acme",
            "tenant_name": "Acme Corp"
        },
        {
            "email": "user1@globex.com",
            "password": "User123!",
            "full_name": "Gary Globex",
            "tenant_name": "Globex Inc"
        },
        {
            "email": "user2@globex.com",
            "password": "User123!",
            "full_name": "Linda Globex",
            "tenant_name": "Globex Inc"
        },
        {
            "email": "user1@initech.com",
            "password": "User123!",
            "full_name": "Tom Initech",
            "tenant_name": "Initech Ltd"
        },
        {
            "email": "user2@initech.com",
            "password": "User123!",
            "full_name": "Sara Initech",
            "tenant_name": "Initech Ltd"
        }
    ]

    # Register each user
    for user in users:
        try:
            response = client.post(
                "/api/v1/users/register",
                headers={"Content-Type": "application/json"},
                json=user
            )
            
            # Print response for debugging
            print(f"\nRegistering user: {user['email']}")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.get_json()}")
            
            if response.status_code != 201:
                print(f"Error details: {json.dumps(response.get_json(), indent=2)}")
                print(f"Response data: {response.data}")
            
            assert response.status_code == 201, f"Failed to register user {user['email']}: {response.get_json()}"
            
        except Exception as e:
            print(f"Error registering user {user['email']}: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            raise

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 