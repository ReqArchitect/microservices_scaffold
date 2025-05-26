"""
Configuration for the template service
"""
import os

SQLALCHEMY_DATABASE_URI = os.environ.get('TEMPLATE_SERVICE_DATABASE_URL')

class Config:
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    
    # Swagger documentation
    SWAGGER = {
        'title': 'Template Service API',
        'uiversion': 3,
        'version': os.environ.get('VERSION', 'v1'),
        'description': 'API documentation for Template Service',
        'termsOfService': '',
        'specs': [
            {
                'endpoint': 'apispec',
                'route': '/apispec.json',
                'rule_filter': lambda rule: True,  # all rules
                'model_filter': lambda tag: True,  # all models
            }
        ],
        'static_url_path': '/flasgger_static',
        'swagger_ui': True,
        'specs_route': '/docs/'
    }
    
    # Service configuration
    SERVICE_NAME = os.environ.get('SERVICE_NAME', 'template_service')
    SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5100))
    API_VERSION = os.environ.get('API_VERSION', 'v1')
    
    # Service registry (Consul) configuration
    CONSUL_HOST = os.environ.get('CONSUL_HOST', 'localhost')
    CONSUL_PORT = int(os.environ.get('CONSUL_PORT', 8500))
    AUTO_REGISTER_SERVICE = os.environ.get('AUTO_REGISTER_SERVICE', 'true').lower() == 'true'
    
    # Distributed tracing configuration
    JAEGER_HOST = os.environ.get('JAEGER_HOST', 'localhost')
    JAEGER_PORT = int(os.environ.get('JAEGER_PORT', 6831))
    TRACING_ENABLED = os.environ.get('TRACING_ENABLED', 'true').lower() == 'true'
    
    # AI Service configuration
    AI_ASSISTANT_SERVICE_URL = os.environ.get('AI_ASSISTANT_SERVICE_URL', 'http://ai-assistant-service:5200')
    AI_ORCHESTRATOR_SERVICE_URL = os.environ.get('AI_ORCHESTRATOR_SERVICE_URL', 'http://ai-orchestrator-service:5100')
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///template_service_dev.db')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///template_service_test.db')
    
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@template-db-service:5432/template_service')
    
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
