import pytest
from flask import Flask, jsonify
from app.utils.error_handlers import (
    handle_400, handle_401, handle_403, handle_404,
    handle_405, handle_429, handle_500, handle_validation_error
)
from marshmallow import ValidationError

@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

def test_handle_400(app):
    """Test 400 Bad Request handler."""
    with app.app_context():
        error = {'message': 'Bad Request', 'errors': ['Invalid input']}
        response = handle_400(error)
        assert response.status_code == 400
        assert response.json['error'] == 'Bad Request'
        assert response.json['message'] == 'Invalid input'

def test_handle_401(app):
    """Test 401 Unauthorized handler."""
    with app.app_context():
        error = {'message': 'Unauthorized', 'errors': ['Authentication required']}
        response = handle_401(error)
        assert response.status_code == 401
        assert response.json['error'] == 'Unauthorized'
        assert response.json['message'] == 'Authentication required'

def test_handle_403(app):
    """Test 403 Forbidden handler."""
    with app.app_context():
        error = {'message': 'Forbidden', 'errors': ['Permission denied']}
        response = handle_403(error)
        assert response.status_code == 403
        assert response.json['error'] == 'Forbidden'
        assert response.json['message'] == 'Permission denied'

def test_handle_404(app):
    """Test 404 Not Found handler."""
    with app.app_context():
        error = {'message': 'Not Found', 'errors': ['Resource not found']}
        response = handle_404(error)
        assert response.status_code == 404
        assert response.json['error'] == 'Not Found'
        assert response.json['message'] == 'Resource not found'

def test_handle_405(app):
    """Test 405 Method Not Allowed handler."""
    with app.app_context():
        error = {'message': 'Method Not Allowed', 'errors': ['Method not supported']}
        response = handle_405(error)
        assert response.status_code == 405
        assert response.json['error'] == 'Method Not Allowed'
        assert response.json['message'] == 'Method not supported'

def test_handle_429(app):
    """Test 429 Too Many Requests handler."""
    with app.app_context():
        error = {'message': 'Too Many Requests', 'errors': ['Rate limit exceeded']}
        response = handle_429(error)
        assert response.status_code == 429
        assert response.json['error'] == 'Too Many Requests'
        assert response.json['message'] == 'Rate limit exceeded'

def test_handle_500(app):
    """Test 500 Internal Server Error handler."""
    with app.app_context():
        error = {'message': 'Internal Server Error', 'errors': ['An unexpected error occurred']}
        response = handle_500(error)
        assert response.status_code == 500
        assert response.json['error'] == 'Internal Server Error'
        assert response.json['message'] == 'An unexpected error occurred'

def test_handle_validation_error(app):
    """Test validation error handler."""
    with app.app_context():
        error = ValidationError('Invalid input', field_name='email')
        response = handle_validation_error(error)
        assert response.status_code == 400
        assert response.json['error'] == 'Validation Error'
        assert 'email' in response.json['message']

def test_error_handler_with_custom_message(app):
    """Test error handler with custom message."""
    with app.app_context():
        error = {'message': 'Custom Error', 'errors': ['Custom error message']}
        response = handle_400(error)
        assert response.status_code == 400
        assert response.json['error'] == 'Bad Request'
        assert response.json['message'] == 'Custom error message'

def test_error_handler_with_multiple_errors(app):
    """Test error handler with multiple errors."""
    with app.app_context():
        error = {
            'message': 'Validation Error',
            'errors': ['Error 1', 'Error 2', 'Error 3']
        }
        response = handle_400(error)
        assert response.status_code == 400
        assert response.json['error'] == 'Bad Request'
        assert len(response.json['errors']) == 3
        assert 'Error 1' in response.json['errors']
        assert 'Error 2' in response.json['errors']
        assert 'Error 3' in response.json['errors']

def test_error_handler_with_headers(app):
    """Test error handler with custom headers."""
    with app.app_context():
        error = {'message': 'Rate limit exceeded', 'errors': ['Too many requests']}
        response = handle_429(error)
        assert response.status_code == 429
        assert 'Retry-After' in response.headers
        assert response.headers['Content-Type'] == 'application/json'

def test_error_handler_with_traceback(app):
    """Test error handler with traceback in development."""
    app.config['DEBUG'] = True
    with app.app_context():
        error = {'message': 'Internal Server Error', 'errors': ['An error occurred']}
        response = handle_500(error)
        assert response.status_code == 500
        assert 'traceback' in response.json

def test_error_handler_without_traceback(app):
    """Test error handler without traceback in production."""
    app.config['DEBUG'] = False
    with app.app_context():
        error = {'message': 'Internal Server Error', 'errors': ['An error occurred']}
        response = handle_500(error)
        assert response.status_code == 500
        assert 'traceback' not in response.json

def test_error_handler_with_validation_error_details(app):
    """Test error handler with validation error details."""
    with app.app_context():
        error = ValidationError({
            'email': ['Invalid email format'],
            'password': ['Password too short']
        })
        response = handle_validation_error(error)
        assert response.status_code == 400
        assert response.json['error'] == 'Validation Error'
        assert 'email' in response.json['errors']
        assert 'password' in response.json['errors']
        assert 'Invalid email format' in response.json['errors']['email']
        assert 'Password too short' in response.json['errors']['password']

def test_error_handler_with_nested_validation_errors(app):
    """Test error handler with nested validation errors."""
    with app.app_context():
        error = ValidationError({
            'user': {
                'email': ['Invalid email format'],
                'profile': {
                    'age': ['Must be greater than 0']
                }
            }
        })
        response = handle_validation_error(error)
        assert response.status_code == 400
        assert response.json['error'] == 'Validation Error'
        assert 'user' in response.json['errors']
        assert 'email' in response.json['errors']['user']
        assert 'profile' in response.json['errors']['user']
        assert 'age' in response.json['errors']['user']['profile'] 