# Authentication Service

A centralized authentication and authorization service for the microservices architecture.

## Features

- JWT-based authentication with consistent identity claims
- Role-based access control (RBAC)
- Multi-tenant support
- Circuit breaker implementation for fault tolerance
- API versioning with deprecation support
- Comprehensive logging and monitoring
- Rate limiting
- Caching with Redis
- Prometheus metrics

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
flask db upgrade
```

5. Run the service:
```bash
flask run
```

## API Documentation

The API documentation is available at `/swagger-ui` when the service is running.

### Authentication

All endpoints require JWT authentication unless specified otherwise. Include the token in the Authorization header:
```
Authorization: Bearer <token>
```

### API Versions

The service supports multiple API versions with deprecation and sunset policies:

- v1 (Current)
- v2 (Coming soon)

## Circuit Breaker

The service implements circuit breakers to prevent cascading failures:

```python
from app.utils.circuit_breaker import circuit_breaker

@circuit_breaker(failure_threshold=5, recovery_timeout=60)
def your_function():
    # Your code here
    pass
```

## API Versioning

Use the versioning decorator to manage API versions:

```python
from app.utils.versioning import api_version

@api_version('v1', deprecated=False)
def your_endpoint():
    # Your code here
    pass
```

## Monitoring

The service exposes Prometheus metrics at `/metrics`:

- Request counts
- Latency
- Error rates
- Circuit breaker status
- Cache hit/miss rates

## Development

### Running Tests

```bash
pytest
```

### Code Style

```bash
black .
flake8
mypy .
```

### Database Migrations

```bash
flask db migrate -m "Description"
flask db upgrade
```

## Deployment

1. Build the Docker image:
```bash
docker build -t auth-service .
```

2. Run the container:
```bash
docker run -p 5000:5000 auth-service
```

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `REDIS_URL`: Redis connection string
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `CIRCUIT_BREAKER_ENABLED`: Enable/disable circuit breakers
- `CIRCUIT_BREAKER_FAILURE_THRESHOLD`: Number of failures before opening circuit
- `CIRCUIT_BREAKER_RECOVERY_TIMEOUT`: Time in seconds before attempting recovery

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT 