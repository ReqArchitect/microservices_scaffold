"""Test configuration."""
import os

# Test database
SQLALCHEMY_DATABASE_URI = os.getenv(
    'DATABASE_URL',
    'postgresql+psycopg://postgres:password@localhost:5432/initiative_service_test'
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Auth service
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5000')

# Testing
TESTING = True
DEBUG = False

# Circuit breaker
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 3
CIRCUIT_BREAKER_RECOVERY_TIMEOUT = 5
CIRCUIT_BREAKER_HALF_OPEN_TIMEOUT = 2

# Rate limiting
RATELIMIT_ENABLED = False

# Caching
CACHE_TYPE = "simple"
CACHE_DEFAULT_TIMEOUT = 300

# Metrics
METRICS_ENABLED = False

# Logging
LOG_LEVEL = "DEBUG"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# JWT
JWT_SECRET_KEY = 'test-secret-key' 