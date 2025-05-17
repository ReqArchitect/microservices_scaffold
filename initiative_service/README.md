# Initiative Service

A microservice for managing initiatives in a multi-tenant environment.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with the following variables:

```env
# Flask configuration
FLASK_APP=main.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database configuration
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/initiative_service
TEST_DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/initiative_service_test

# JWT configuration
JWT_SECRET_KEY=your-jwt-secret-key-here

# Redis configuration
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO

# Rate limiting
RATELIMIT_ENABLED=true
RATELIMIT_DEFAULT=200 per day;50 per hour

# Cache
CACHE_TYPE=redis
CACHE_DEFAULT_TIMEOUT=300

# Metrics
PROMETHEUS_METRICS_ENABLED=true
```

4. Initialize the database:
```bash
flask db upgrade
```

5. Run the service:
```bash
flask run
```

## Development

### Running Tests
```bash
pytest
```

### Code Coverage
```bash
pytest --cov=app tests/
```

## API Documentation

The API documentation is available at `/apidocs` when the service is running.

## Features

- Multi-tenant support
- Role-based access control
- Rate limiting
- Caching with Redis
- Prometheus metrics
- Swagger/OpenAPI documentation
- JWT authentication
- Database migrations

## Dependencies

- Flask 2.3.3
- Flask-SQLAlchemy 3.0.5
- Flask-Migrate 4.0.4
- Flask-JWT-Extended 4.5.2
- Flask-CORS 4.0.0
- Flask-Caching 2.0.2
- Flask-Limiter 3.5.0
- Flasgger 0.9.7.1
- python-dotenv 1.0.0
- psycopg[binary] 3.2.7
- prometheus-client 0.17.1
- prometheus-flask-exporter 0.22.4
- pytest 7.4.0
- pytest-cov 4.1.0
- redis 5.0.1
- gunicorn 21.2.0

## License

MIT 