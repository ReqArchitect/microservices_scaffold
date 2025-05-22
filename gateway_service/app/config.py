import os
from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    CANVAS_SERVICE_URL: str = os.getenv('CANVAS_SERVICE_URL', 'http://localhost:8001')
    STRATEGY_SERVICE_URL: str = os.getenv('STRATEGY_SERVICE_URL', 'http://localhost:8002')
    BUSINESS_LAYER_SERVICE_URL: str = os.getenv('BUSINESS_LAYER_SERVICE_URL', 'http://localhost:8003')
    APPLICATION_LAYER_SERVICE_URL: str = os.getenv('APPLICATION_LAYER_SERVICE_URL', 'http://localhost:8004')
    TECHNOLOGY_LAYER_SERVICE_URL: str = os.getenv('TECHNOLOGY_LAYER_SERVICE_URL', 'http://localhost:8005')
    MOTIVATION_SERVICE_URL: str = os.getenv('MOTIVATION_SERVICE_URL', 'http://localhost:8006')
    IMPLEMENTATION_MIGRATION_SERVICE_URL: str = os.getenv('IMPLEMENTATION_MIGRATION_SERVICE_URL', 'http://localhost:8007')
    FILE_SERVICE_URL: str = os.getenv('FILE_SERVICE_URL', 'http://localhost:8008')
    NOTIFICATION_SERVICE_URL: str = os.getenv('NOTIFICATION_SERVICE_URL', 'http://localhost:8009')
    BILLING_SERVICE_URL: str = os.getenv('BILLING_SERVICE_URL', 'http://localhost:8010')
    AUTH_PUBLIC_KEY_URL: str = os.getenv('AUTH_PUBLIC_KEY_URL', '')
    AUTH_SERVICE_URL: str = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001')
    CORS_ORIGINS: List[str] = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))

settings = Settings() 