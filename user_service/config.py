import os

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Service Integration
    AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://localhost:5000')
    
    # Circuit Breaker Settings
    CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT = 60
    CIRCUIT_BREAKER_ENABLED = True

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg://postgres:password@localhost:5432/user_service'

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg://postgres:password@localhost:5432/user_service_test'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
