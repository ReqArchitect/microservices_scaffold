import pytest
import logging
import json
from datetime import datetime
from flask import Flask
from app.utils.logging import setup_logging, log_request, log_response, log_error

@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['LOG_LEVEL'] = 'DEBUG'
    return app

@pytest.fixture
def logger():
    """Create a test logger."""
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.INFO)
    
    # Create a memory handler for testing
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    return logger

def test_setup_logging(app):
    """Test logging setup."""
    with app.app_context():
        setup_logging(app)
        assert app.logger.level == logging.DEBUG
        assert len(app.logger.handlers) > 0

def test_log_request(app):
    """Test request logging."""
    with app.app_context():
        setup_logging(app)
        
        # Mock request
        class MockRequest:
            method = 'GET'
            path = '/api/v1/users'
            headers = {'Authorization': 'Bearer token'}
            data = b'{"key": "value"}'
            args = {'page': '1', 'per_page': '10'}
            
        request = MockRequest()
        log_request(request)
        
        # Verify log output
        log_output = app.logger.handlers[0].buffer.getvalue()
        log_data = json.loads(log_output)
        
        assert log_data['type'] == 'request'
        assert log_data['method'] == 'GET'
        assert log_data['path'] == '/api/v1/users'
        assert 'Authorization' in log_data['headers']
        assert log_data['data'] == '{"key": "value"}'
        assert log_data['args'] == {'page': '1', 'per_page': '10'}

def test_log_response(app):
    """Test response logging."""
    with app.app_context():
        setup_logging(app)
        
        # Mock response
        class MockResponse:
            status_code = 200
            data = b'{"message": "success"}'
            headers = {'Content-Type': 'application/json'}
            
        response = MockResponse()
        log_response(response)
        
        # Verify log output
        log_output = app.logger.handlers[0].buffer.getvalue()
        log_data = json.loads(log_output)
        
        assert log_data['type'] == 'response'
        assert log_data['status_code'] == 200
        assert log_data['data'] == '{"message": "success"}'
        assert log_data['headers'] == {'Content-Type': 'application/json'}

def test_log_error(app):
    """Test error logging."""
    with app.app_context():
        setup_logging(app)
        
        # Mock error
        error = ValueError('Invalid input')
        log_error(error)
        
        # Verify log output
        log_output = app.logger.handlers[0].buffer.getvalue()
        log_data = json.loads(log_output)
        
        assert log_data['type'] == 'error'
        assert log_data['error_type'] == 'ValueError'
        assert log_data['error_message'] == 'Invalid input'
        assert 'traceback' in log_data

def test_log_request_without_data(app):
    """Test request logging without data."""
    with app.app_context():
        setup_logging(app)
        
        # Mock request without data
        class MockRequest:
            method = 'GET'
            path = '/api/v1/users'
            headers = {}
            data = b''
            args = {}
            
        request = MockRequest()
        log_request(request)
        
        # Verify log output
        log_output = app.logger.handlers[0].buffer.getvalue()
        log_data = json.loads(log_output)
        
        assert log_data['type'] == 'request'
        assert log_data['method'] == 'GET'
        assert log_data['path'] == '/api/v1/users'
        assert log_data['data'] == ''
        assert log_data['args'] == {}

def test_log_response_with_error(app):
    """Test response logging with error status."""
    with app.app_context():
        setup_logging(app)
        
        # Mock error response
        class MockResponse:
            status_code = 400
            data = b'{"error": "Bad Request"}'
            headers = {'Content-Type': 'application/json'}
            
        response = MockResponse()
        log_response(response)
        
        # Verify log output
        log_output = app.logger.handlers[0].buffer.getvalue()
        log_data = json.loads(log_output)
        
        assert log_data['type'] == 'response'
        assert log_data['status_code'] == 400
        assert log_data['data'] == '{"error": "Bad Request"}'

def test_log_error_with_context(app):
    """Test error logging with context."""
    with app.app_context():
        setup_logging(app)
        
        # Mock error with context
        error = ValueError('Invalid input')
        context = {
            'user_id': 123,
            'action': 'create_user',
            'request_id': 'abc123'
        }
        log_error(error, context)
        
        # Verify log output
        log_output = app.logger.handlers[0].buffer.getvalue()
        log_data = json.loads(log_output)
        
        assert log_data['type'] == 'error'
        assert log_data['error_type'] == 'ValueError'
        assert log_data['error_message'] == 'Invalid input'
        assert log_data['context'] == context

def test_log_request_with_sensitive_data(app):
    """Test request logging with sensitive data masking."""
    with app.app_context():
        setup_logging(app)
        
        # Mock request with sensitive data
        class MockRequest:
            method = 'POST'
            path = '/api/v1/auth/login'
            headers = {
                'Authorization': 'Bearer secret_token',
                'X-API-Key': 'secret_key'
            }
            data = b'{"password": "secret123", "email": "user@example.com"}'
            args = {}
            
        request = MockRequest()
        log_request(request)
        
        # Verify log output
        log_output = app.logger.handlers[0].buffer.getvalue()
        log_data = json.loads(log_output)
        
        assert log_data['type'] == 'request'
        assert log_data['method'] == 'POST'
        assert log_data['path'] == '/api/v1/auth/login'
        assert 'Bearer [MASKED]' in log_data['headers']['Authorization']
        assert '[MASKED]' in log_data['headers']['X-API-Key']
        assert 'password' not in log_data['data']
        assert 'email' in log_data['data']

def test_log_response_with_sensitive_data(app):
    """Test response logging with sensitive data masking."""
    with app.app_context():
        setup_logging(app)
        
        # Mock response with sensitive data
        class MockResponse:
            status_code = 200
            data = b'{"token": "secret_token", "refresh_token": "secret_refresh"}'
            headers = {
                'Set-Cookie': 'session=secret_session; HttpOnly'
            }
            
        response = MockResponse()
        log_response(response)
        
        # Verify log output
        log_output = app.logger.handlers[0].buffer.getvalue()
        log_data = json.loads(log_output)
        
        assert log_data['type'] == 'response'
        assert log_data['status_code'] == 200
        assert 'token' not in log_data['data']
        assert 'refresh_token' not in log_data['data']
        assert '[MASKED]' in log_data['headers']['Set-Cookie']

def test_log_request_with_file_upload(app):
    """Test request logging with file upload."""
    with app.app_context():
        setup_logging(app)
        
        # Mock request with file upload
        class MockRequest:
            method = 'POST'
            path = '/api/v1/upload'
            headers = {'Content-Type': 'multipart/form-data'}
            files = {'file': 'test.txt'}
            data = b''
            args = {}
            
        request = MockRequest()
        log_request(request)
        
        # Verify log output
        log_output = app.logger.handlers[0].buffer.getvalue()
        log_data = json.loads(log_output)
        
        assert log_data['type'] == 'request'
        assert log_data['method'] == 'POST'
        assert log_data['path'] == '/api/v1/upload'
        assert 'files' in log_data
        assert log_data['files'] == {'file': 'test.txt'}

def test_log_request_with_query_params(app):
    """Test request logging with query parameters."""
    with app.app_context():
        setup_logging(app)
        
        # Mock request with query parameters
        class MockRequest:
            method = 'GET'
            path = '/api/v1/search'
            headers = {}
            data = b''
            args = {
                'q': 'test',
                'sort': 'desc',
                'filter': 'active'
            }
            
        request = MockRequest()
        log_request(request)
        
        # Verify log output
        log_output = app.logger.handlers[0].buffer.getvalue()
        log_data = json.loads(log_output)
        
        assert log_data['type'] == 'request'
        assert log_data['method'] == 'GET'
        assert log_data['path'] == '/api/v1/search'
        assert log_data['args'] == {
            'q': 'test',
            'sort': 'desc',
            'filter': 'active'
        } 