# User Service

A microservice for user management, authentication, and authorization.

## Features

- User registration and authentication
- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
- Multi-tenant support
- Rate limiting
- Activity logging
- Email verification
- Password reset functionality
- API documentation with Swagger
- Prometheus metrics
- Structured logging

## Prerequisites

- Python 3.8+
- PostgreSQL
- Redis (for rate limiting in production)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd user_service
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

The service supports three environments:

- Development (default)
- Testing
- Production

Configuration is managed through environment variables and the `config.py` file.

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string (for rate limiting)
- `SECRET_KEY`: Flask secret key
- `JWT_SECRET_KEY`: JWT signing key
- `MAIL_SERVER`: SMTP server for emails
- `MAIL_PORT`: SMTP port
- `MAIL_USERNAME`: SMTP username
- `MAIL_PASSWORD`: SMTP password
- `MAIL_DEFAULT_SENDER`: Default sender email

## Running the Service

### Development

```bash
flask run
```

### Production

```bash
gunicorn "app:create_app('production')"
```

## API Documentation

The API documentation is available at `/apidocs` when the service is running.

### Authentication

The service uses JWT tokens for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <token>
```

### Endpoints

#### Authentication

- `POST /api/register`: Register a new user
- `POST /api/login`: Login and get access token
- `POST /api/refresh`: Refresh access token
- `POST /api/logout`: Logout and invalidate token
- `POST /api/verify-email`: Verify email address
- `POST /api/reset-password`: Request password reset
- `POST /api/reset-password/<token>`: Reset password

#### User Management

- `GET /api/users`: List users (admin only)
- `PUT /api/users/<id>`: Update user (admin only)
- `GET /api/users/<id>/activity`: Get user activity log (admin only)

#### System

- `GET /api/metrics`: Get system metrics (vendor only)

## Monitoring

### Prometheus Metrics

The service exposes Prometheus metrics at `/metrics`:

- `http_requests_total`: Total HTTP requests
- `http_request_duration_seconds`: HTTP request latency

### Logging

Logs are written to `logs/user_service.log` with rotation.

## Testing

Run tests with:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app tests/
```

## Database Migrations

Create a new migration:

```bash
flask db migrate -m "description"
```

Apply migrations:

```bash
flask db upgrade
```

## Security

- JWT tokens with short expiration
- Refresh token rotation
- Rate limiting
- Password hashing
- CSRF protection
- Secure cookie settings
- Input validation
- SQL injection protection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 