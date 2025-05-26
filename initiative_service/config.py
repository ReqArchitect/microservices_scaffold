import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    # Service identity and discovery
    SERVICE_NAME = os.environ.get('SERVICE_NAME', 'initiative_service')
    SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5004))
    
    # Core settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    SQLALCHEMY_DATABASE_URI = os.environ.get('INITIATIVE_SERVICE_DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }

    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = 'HS256'
    JWT_IDENTITY_CLAIM = 'identity'
    JWT_USER_CLAIMS = 'user_claims'
    JWT_ERROR_MESSAGE_KEY = 'error'
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_TOKEN_LOCATION = ['headers']
    JWT_BLACKLIST_ENABLED = False
    
    # Service registry (Consul) configuration
    CONSUL_HOST = os.environ.get('CONSUL_HOST', 'localhost')
    CONSUL_PORT = int(os.environ.get('CONSUL_PORT', 8500))
    AUTO_REGISTER_SERVICE = os.environ.get('AUTO_REGISTER_SERVICE', 'true').lower() == 'true'
    
    # Circuit breaker configuration
    CIRCUIT_BREAKER_ENABLED = os.environ.get('CIRCUIT_BREAKER_ENABLED', 'true').lower() == 'true'
    CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.environ.get('CIRCUIT_BREAKER_FAILURE_THRESHOLD', 5))
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT = int(os.environ.get('CIRCUIT_BREAKER_RECOVERY_TIMEOUT', 30))
    
    # Distributed tracing configuration
    JAEGER_HOST = os.environ.get('JAEGER_HOST', 'localhost')
    JAEGER_PORT = int(os.environ.get('JAEGER_PORT', 6831))
    TRACING_ENABLED = os.environ.get('TRACING_ENABLED', 'true').lower() == 'true'
    
    # API versioning
    API_VERSION = os.environ.get('API_VERSION', 'v1')
    LATEST_API_VERSION = os.environ.get('LATEST_API_VERSION', 'v1')
    
    # Outbox pattern
    OUTBOX_PROCESSING_INTERVAL = int(os.environ.get('OUTBOX_PROCESSING_INTERVAL', 10))  # seconds
    OUTBOX_MAX_RETRY = int(os.environ.get('OUTBOX_MAX_RETRY', 3))
    OUTBOX_ENABLED = os.environ.get('OUTBOX_ENABLED', 'true').lower() == 'true'

    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL')
    RATELIMIT_STRATEGY = "fixed-window"
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_HEADERS_ENABLED = True

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.environ.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOG_FILE = "logs/initiative_service.log"

    # API
    API_TITLE = "Initiative Service API"
    API_VERSION = os.environ.get('API_VERSION', 'v1')
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    # Cache
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    CACHE_DEFAULT_TIMEOUT = 300

    # Metrics
    PROMETHEUS_METRICS_ENABLED = True
    METRICS_UPDATE_INTERVAL = 60  # seconds

    SWAGGER = {
        'title': 'Initiative Service API',
        'uiversion': 3,
        'version': '1.0.0',
        'description': 'API for managing initiatives'
    }

    # Service Integration
    AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://localhost:5000')

    # Circuit Breaker Settings
    CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.environ.get('CIRCUIT_BREAKER_FAILURE_THRESHOLD', 5))
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT = int(os.environ.get('CIRCUIT_BREAKER_RECOVERY_TIMEOUT', 60))
    CIRCUIT_BREAKER_ENABLED = os.environ.get('CIRCUIT_BREAKER_ENABLED', 'true').lower() == 'true'

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    RATELIMIT_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql+psycopg2://postgres:password@localhost:5432/initiative_service')
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', 'postgresql+psycopg2://postgres:password@localhost:5432/initiative_service_test')
    RATELIMIT_ENABLED = False
    CACHE_TYPE = "simple"
    LOG_LEVEL = "DEBUG"
    
    # JWT Configuration
    JWT_ACCESS_TOKEN_EXPIRES = False  # Disable token expiration in tests
    JWT_SECRET_KEY = 'test-jwt-secret'  # Use a fixed secret key for tests
    JWT_ALGORITHM = 'HS256'
    JWT_IDENTITY_CLAIM = 'identity'  # Already using 'identity'
    JWT_USER_CLAIMS = 'user_claims'
    JWT_ERROR_MESSAGE_KEY = 'error'
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_TOKEN_LOCATION = ['headers']
    JWT_BLACKLIST_ENABLED = False
    
    CACHE_NO_NULL_WARNING = True
    PROMETHEUS_METRICS_ENABLED = False
    SQLALCHEMY_ECHO = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = "WARNING"
    RATELIMIT_ENABLED = True
    CACHE_TYPE = "redis"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ECHO = False
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Service identity and discovery
SERVICE_NAME = os.environ.get('SERVICE_NAME', 'initiative_service')
SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5002))

# Service registry (Consul) configuration
CONSUL_HOST = os.environ.get('CONSUL_HOST', 'localhost')
CONSUL_PORT = int(os.environ.get('CONSUL_PORT', 8500))
AUTO_REGISTER_SERVICE = os.environ.get('AUTO_REGISTER_SERVICE', 'true').lower() == 'true'

# Circuit breaker configuration
CIRCUIT_BREAKER_ENABLED = os.environ.get('CIRCUIT_BREAKER_ENABLED', 'true').lower() == 'true'
CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.environ.get('CIRCUIT_BREAKER_FAILURE_THRESHOLD', 5))
CIRCUIT_BREAKER_RECOVERY_TIMEOUT = int(os.environ.get('CIRCUIT_BREAKER_RECOVERY_TIMEOUT', 30))

# Distributed tracing configuration
JAEGER_HOST = os.environ.get('JAEGER_HOST', 'localhost')
JAEGER_PORT = int(os.environ.get('JAEGER_PORT', 6831))
TRACING_ENABLED = os.environ.get('TRACING_ENABLED', 'true').lower() == 'true'

# API versioning
API_VERSION = os.environ.get('API_VERSION', 'v1')
LATEST_API_VERSION = os.environ.get('LATEST_API_VERSION', 'v1')

# Outbox pattern
OUTBOX_PROCESSING_INTERVAL = int(os.environ.get('OUTBOX_PROCESSING_INTERVAL', 10))  # seconds
OUTBOX_MAX_RETRY = int(os.environ.get('OUTBOX_MAX_RETRY', 3))
OUTBOX_ENABLED = os.environ.get('OUTBOX_ENABLED', 'true').lower() == 'true'
