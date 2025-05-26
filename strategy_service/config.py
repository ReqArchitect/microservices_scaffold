import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///strategy_service.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-secret-key')
    SWAGGER = {
        'title': 'Strategy Service API',
        'uiversion': 3
    }
    
    # Service identity and discovery
    SERVICE_NAME = os.environ.get('SERVICE_NAME', 'strategy_service')
    SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5001))
    
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

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', 'sqlite:///strategy_service_test.db')
    AUTO_REGISTER_SERVICE = False
    TRACING_ENABLED = False
    CIRCUIT_BREAKER_ENABLED = False
