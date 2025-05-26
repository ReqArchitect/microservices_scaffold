import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///kpi_service.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default_secret_key')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ['true', '1', 't']
    
    # Service identity and discovery
    SERVICE_NAME = os.environ.get('SERVICE_NAME', 'kpi_service')
    SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5003))
    
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

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql+psycopg2://postgres:password@localhost:5432/kpi_service')
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', 'postgresql+psycopg2://postgres:password@localhost:5432/kpi_service_test')
    RATELIMIT_ENABLED = False
    CACHE_TYPE = "simple"
    LOG_LEVEL = "DEBUG"
    AUTO_REGISTER_SERVICE = False
    TRACING_ENABLED = False
    CIRCUIT_BREAKER_ENABLED = False
    OUTBOX_ENABLED = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = "WARNING"
    RATELIMIT_ENABLED = True
    CACHE_TYPE = "redis"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ECHO = False
    CACHE_REDIS_URL = os.getenv('REDIS_URL')
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Service identity and discovery
SERVICE_NAME = os.environ.get('SERVICE_NAME', 'kpi_service')
SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5003))

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
