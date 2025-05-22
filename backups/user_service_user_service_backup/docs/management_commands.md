# User Service Management Commands

This document provides detailed information about the available management commands for the User Service.

## Basic Commands

### Database Management

#### Create Database
```bash
flask create_db [--force]
```
Creates all database tables. Use `--force` to skip confirmation.

#### Drop Database
```bash
flask drop_db [--force]
```
Drops all database tables. Use `--force` to skip confirmation.

### User Management

#### Create Admin/Vendor User
```bash
flask create_admin
```
Interactive command to create a new admin or vendor user. Options:
- `--role`: User role (admin/vendor, default: admin)
- `--verified`: Mark email as verified

Example:
```bash
flask create_admin --role vendor --verified
```

#### List Users
```bash
flask list_users [--tenant TENANT] [--role ROLE] [--active] [--verified] [--format FORMAT]
```
Lists users with filtering options:
- `--tenant`: Filter by tenant name
- `--role`: Filter by role
- `--active`: Show only active users
- `--verified`: Show only verified users
- `--format`: Output format (text/json)

Examples:
```bash
# List all users
flask list_users

# List active admin users in JSON format
flask list_users --role admin --active --format json

# List users from specific tenant
flask list_users --tenant "Acme Corp"
```

### Application Management

#### Run Application
```bash
flask run [--host HOST] [--port PORT] [--debug] [--reload] [--workers WORKERS]
```
Runs the Flask application with various options:
- `--host`: Host to bind to (default: 127.0.0.1)
- `--port`: Port to bind to (default: 5000)
- `--debug`: Enable debug mode
- `--reload`: Enable auto-reload
- `--workers`: Number of worker processes (default: 1)

Examples:
```bash
# Run in debug mode
flask run --debug

# Run with multiple workers
flask run --workers 4 --reload
```

#### Run Tests
```bash
flask test [--coverage] [--verbose] [--failfast]
```
Runs the test suite with options:
- `--coverage`: Run tests with coverage report
- `--verbose`: Show detailed test output
- `--failfast`: Stop on first failure

Examples:
```bash
# Run tests with coverage
flask test --coverage

# Run tests in verbose mode
flask test --verbose
```

### Database Migrations

#### Initialize Migrations
```bash
flask init_migrations [--force]
```
Initializes the database migrations. Use `--force` to reinitialize existing migrations.

#### Create Migration
```bash
flask migrate [--message MESSAGE]
```
Creates a new migration with an optional message.

#### Upgrade Database
```bash
flask upgrade [--revision REVISION]
```
Upgrades the database to a later version. Defaults to latest version.

#### Downgrade Database
```bash
flask downgrade --revision REVISION
```
Downgrades the database to a previous version.

Examples:
```bash
# Create a new migration
flask migrate --message "Add user preferences"

# Upgrade to latest version
flask upgrade

# Downgrade to specific version
flask downgrade --revision a1b2c3d4
```

### Maintenance

#### Cleanup Old Activities
```bash
flask cleanup [--days DAYS]
```
Deletes user activities older than specified days (default: 30).

Example:
```bash
# Delete activities older than 90 days
flask cleanup --days 90
```

### Development Setup

#### Setup Development Environment
```bash
flask setup_dev
```
Sets up the development environment by:
1. Creating necessary directories (logs, instance)
2. Creating default config.json if not exists
3. Initializing database
4. Initializing migrations

## Configuration

The application can be configured using a `config.json` file. The development setup command creates a default configuration:

```json
{
    "development": {
        "database_url": "sqlite:///dev.db",
        "secret_key": "dev-secret-key",
        "jwt_secret_key": "jwt-dev-secret-key"
    }
}
```

## Best Practices

1. **Database Management**
   - Always backup your database before running migrations
   - Use `--force` with caution
   - Test migrations in development before production

2. **User Management**
   - Use strong passwords
   - Verify email addresses for admin users
   - Regularly review user list for inactive accounts

3. **Application Deployment**
   - Use multiple workers in production
   - Enable auto-reload in development
   - Monitor application logs

4. **Testing**
   - Run tests with coverage regularly
   - Fix failing tests immediately
   - Add tests for new features

5. **Maintenance**
   - Schedule regular cleanup of old activities
   - Monitor database size
   - Review user activity logs

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check database URL in config.json
   - Verify database server is running
   - Check user permissions

2. **Migration Errors**
   - Ensure migrations are up to date
   - Check for conflicting migrations
   - Verify database schema

3. **User Creation Issues**
   - Check email format
   - Verify password requirements
   - Ensure tenant exists

4. **Application Startup Issues**
   - Check port availability
   - Verify dependencies are installed
   - Check configuration file

### Getting Help

For additional help:
1. Check the application logs
2. Review the documentation
3. Contact the development team 