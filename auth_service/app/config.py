import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:password@localhost:5432/auth_service")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_ERROR_MESSAGE_KEY = 'msg'
    JWT_JSON_KEY = 'access_token'
    JWT_IDENTITY_CLAIM = 'identity'  # Consistent identity claim across all services

    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.getenv("REDIS_URL", "memory://")
    RATELIMIT_STRATEGY = "fixed-window"
    RATELIMIT_DEFAULT = "200 per day;50 per hour;10 per minute"
    RATELIMIT_HEADERS_ENABLED = True

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = "logs/auth_service.log"

    # API
    API_TITLE = "Authentication Service API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # Cache
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_DEFAULT_TIMEOUT = 300

    # Metrics
    PROMETHEUS_METRICS_ENABLED = True
    METRICS_UPDATE_INTERVAL = 60  # seconds

    # Circuit Breaker
    CIRCUIT_BREAKER_ENABLED = True
    CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT = 60  # seconds

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-secret-key"

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    # Production-specific settings
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # Must be set in production
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")  # Must be set in production 