import pytest
import os
from app import create_app

@pytest.fixture
def app():
    """Create a Flask app for testing."""
    return create_app('testing')

def test_testing_config(app):
    """Test testing configuration."""
    assert app.config['TESTING'] is True
    assert app.config['DEBUG'] is False
    assert app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgresql')
    assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False
    assert app.config['JWT_SECRET_KEY'] == 'test-secret-key'
    assert app.config['JWT_ACCESS_TOKEN_EXPIRES'] == 3600
    assert app.config['JWT_REFRESH_TOKEN_EXPIRES'] == 604800

def test_development_config(app):
    """Test development configuration."""
    app.config.from_object('app.config.DevelopmentConfig')
    assert app.config['DEBUG'] is True
    assert app.config['TESTING'] is False
    assert app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgresql')
    assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False

def test_production_config(app):
    """Test production configuration."""
    app.config.from_object('app.config.ProductionConfig')
    assert app.config['DEBUG'] is False
    assert app.config['TESTING'] is False
    assert app.config['SQLALCHEMY_DATABASE_URI'] == os.environ.get('DATABASE_URL')
    assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False

def test_jwt_config(app):
    """Test JWT configuration."""
    assert app.config['JWT_SECRET_KEY'] is not None
    assert app.config['JWT_ACCESS_TOKEN_EXPIRES'] is not None
    assert app.config['JWT_REFRESH_TOKEN_EXPIRES'] is not None
    assert app.config['JWT_TOKEN_LOCATION'] == ['headers']
    assert app.config['JWT_HEADER_NAME'] == 'Authorization'
    assert app.config['JWT_HEADER_TYPE'] == 'Bearer'
    assert app.config['JWT_IDENTITY_CLAIM'] == 'sub'

def test_rate_limiting_config(app):
    """Test rate limiting configuration."""
    assert app.config['RATELIMIT_DEFAULT'] == '200 per day'
    assert app.config['RATELIMIT_STORAGE_URL'] == 'memory://'
    assert app.config['RATELIMIT_STRATEGY'] == 'fixed-window'
    assert app.config['RATELIMIT_HEADERS_ENABLED'] is True

def test_caching_config(app):
    """Test caching configuration."""
    assert app.config['CACHE_TYPE'] == 'SimpleCache'
    assert app.config['CACHE_DEFAULT_TIMEOUT'] == 300
    assert app.config['CACHE_THRESHOLD'] == 1000

def test_metrics_config(app):
    """Test metrics configuration."""
    assert app.config['METRICS_ENABLED'] is True
    assert app.config['METRICS_PATH'] == '/metrics'
    assert app.config['METRICS_PORT'] == 9090

def test_circuit_breaker_config(app):
    """Test circuit breaker configuration."""
    assert app.config['CIRCUIT_BREAKER_FAILURE_THRESHOLD'] == 5
    assert app.config['CIRCUIT_BREAKER_RECOVERY_TIMEOUT'] == 60
    assert app.config['CIRCUIT_BREAKER_ENABLED'] is True

def test_logging_config(app):
    """Test logging configuration."""
    assert app.config['LOG_LEVEL'] == 'INFO'
    assert app.config['LOG_FORMAT'] == '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    assert app.config['LOG_FILE'] == 'app.log'

def test_cors_config(app):
    """Test CORS configuration."""
    assert app.config['CORS_ORIGINS'] == ['*']
    assert app.config['CORS_METHODS'] == ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    assert app.config['CORS_ALLOW_HEADERS'] == ['Content-Type', 'Authorization']

def test_redis_config(app):
    """Test Redis configuration."""
    assert app.config['REDIS_URL'] == 'redis://localhost:6379/0'
    assert app.config['REDIS_MAX_CONNECTIONS'] == 10
    assert app.config['REDIS_SOCKET_TIMEOUT'] == 5

def test_security_config(app):
    """Test security configuration."""
    assert app.config['SECURITY_PASSWORD_SALT'] is not None
    assert app.config['SECURITY_PASSWORD_HASH'] == 'bcrypt'
    assert app.config['SECURITY_PASSWORD_LENGTH'] == 8
    assert app.config['SECURITY_TOKEN_MAX_AGE'] == 3600

def test_api_config(app):
    """Test API configuration."""
    assert app.config['API_TITLE'] == 'Auth Service API'
    assert app.config['API_VERSION'] == 'v1'
    assert app.config['API_DESCRIPTION'] == 'Authentication and Authorization Service API'
    assert app.config['API_TERMS_OF_SERVICE'] == 'http://example.com/terms/'
    assert app.config['API_CONTACT_EMAIL'] == 'api@example.com'
    assert app.config['API_LICENSE'] == 'MIT'
    assert app.config['API_LICENSE_URL'] == 'http://opensource.org/licenses/MIT'

def test_swagger_config(app):
    """Test Swagger configuration."""
    assert app.config['SWAGGER_UI_DOC_EXPANSION'] == 'list'
    assert app.config['SWAGGER_UI_OPERATIONS_SORTER'] == 'alpha'
    assert app.config['SWAGGER_UI_TAGS_SORTER'] == 'alpha'
    assert app.config['SWAGGER_UI_DEEP_LINKING'] is True

def test_pagination_config(app):
    """Test pagination configuration."""
    assert app.config['PAGINATION_DEFAULT_PAGE'] == 1
    assert app.config['PAGINATION_DEFAULT_PER_PAGE'] == 10
    assert app.config['PAGINATION_MAX_PER_PAGE'] == 100

def test_error_handling_config(app):
    """Test error handling configuration."""
    assert app.config['ERROR_404_HELP'] is True
    assert app.config['ERROR_405_HELP'] is True
    assert app.config['ERROR_INCLUDE_MESSAGE'] is True
    assert app.config['ERROR_INCLUDE_VALIDATION'] is True 