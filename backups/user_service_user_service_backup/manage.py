from flask.cli import FlaskGroup
from app import create_app
from app.models import db, User, Tenant, UserActivity
from flask_migrate import Migrate, upgrade, downgrade
import click
import os
import json
from datetime import datetime, timedelta
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cli = FlaskGroup(create_app=create_app)
migrate = Migrate()

def load_config():
    """Load configuration from config.json if it exists."""
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}

@cli.command("create_db")
@click.option("--force", is_flag=True, help="Force creation without confirmation")
def create_db(force):
    """Creates the database tables."""
    if not force and not click.confirm("Are you sure you want to create the database tables?"):
        return
    
    try:
        db.create_all()
        click.echo("✅ Database tables created successfully!")
    except Exception as e:
        click.echo(f"❌ Error creating database tables: {str(e)}", err=True)

@cli.command("drop_db")
@click.option("--force", is_flag=True, help="Force drop without confirmation")
def drop_db(force):
    """Drops the database tables."""
    if not force and not click.confirm("Are you sure you want to drop all tables? This cannot be undone!"):
        return
    
    try:
        db.drop_all()
        click.echo("✅ Database tables dropped successfully!")
    except Exception as e:
        click.echo(f"❌ Error dropping database tables: {str(e)}", err=True)

@cli.command("create_admin")
@click.option("--email", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--full-name", prompt=True)
@click.option("--tenant-name", prompt=True)
@click.option("--role", default="admin", type=click.Choice(["admin", "vendor"]))
@click.option("--verified", is_flag=True, help="Mark email as verified")
def create_admin(email, password, full_name, tenant_name, role, verified):
    """Creates an admin or vendor user."""
    from app.utils import validate_password, validate_email_format, generate_password_hash
    
    try:
        # Validate email
        is_valid_email, email_message = validate_email_format(email)
        if not is_valid_email:
            click.echo(f"❌ Error: {email_message}", err=True)
            return

        # Validate password
        is_valid_password, password_message = validate_password(password)
        if not is_valid_password:
            click.echo(f"❌ Error: {password_message}", err=True)
            return

        # Create tenant if it doesn't exist
        tenant = Tenant.query.filter_by(name=tenant_name).first()
        if not tenant:
            tenant = Tenant(name=tenant_name)
            db.session.add(tenant)
            db.session.commit()
            click.echo(f"✅ Created new tenant: {tenant_name}")

        # Create user
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            role=role,
            tenant_id=tenant.id,
            is_active=True,
            is_email_verified=verified
        )
        db.session.add(user)
        db.session.commit()
        click.echo(f"✅ Created {role} user: {email}")
    except Exception as e:
        click.echo(f"❌ Error creating user: {str(e)}", err=True)

@cli.command("list_users")
@click.option("--tenant", help="Filter by tenant name")
@click.option("--role", help="Filter by role")
@click.option("--active", is_flag=True, help="Show only active users")
@click.option("--verified", is_flag=True, help="Show only verified users")
@click.option("--format", type=click.Choice(["text", "json"]), default="text")
def list_users(tenant, role, active, verified, format):
    """Lists users in the database with filtering options."""
    try:
        query = User.query

        if tenant:
            tenant_obj = Tenant.query.filter_by(name=tenant).first()
            if tenant_obj:
                query = query.filter_by(tenant_id=tenant_obj.id)
            else:
                click.echo(f"❌ Tenant not found: {tenant}", err=True)
                return

        if role:
            query = query.filter_by(role=role)
        if active:
            query = query.filter_by(is_active=True)
        if verified:
            query = query.filter_by(is_email_verified=True)

        users = query.all()
        
        if not users:
            click.echo("No users found matching the criteria.")
            return

        if format == "json":
            result = []
            for user in users:
                tenant = Tenant.query.get(user.tenant_id)
                result.append({
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "tenant": tenant.name if tenant else None,
                    "is_active": user.is_active,
                    "is_email_verified": user.is_email_verified,
                    "last_login": user.last_login.isoformat() if user.last_login else None
                })
            click.echo(json.dumps(result, indent=2))
        else:
            for user in users:
                tenant = Tenant.query.get(user.tenant_id)
                click.echo(f"\nUser ID: {user.id}")
                click.echo(f"Email: {user.email}")
                click.echo(f"Name: {user.full_name}")
                click.echo(f"Role: {user.role}")
                click.echo(f"Tenant: {tenant.name if tenant else 'None'}")
                click.echo(f"Active: {'✅' if user.is_active else '❌'}")
                click.echo(f"Verified: {'✅' if user.is_email_verified else '❌'}")
                click.echo(f"Last Login: {user.last_login or 'Never'}")
                click.echo("---")
    except Exception as e:
        click.echo(f"❌ Error listing users: {str(e)}", err=True)

@cli.command("run")
@click.option("--host", default="127.0.0.1", help="The host to bind to")
@click.option("--port", default=5000, help="The port to bind to")
@click.option("--debug", is_flag=True, help="Run in debug mode")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
@click.option("--workers", default=1, help="Number of worker processes")
def run(host, port, debug, reload, workers):
    """Runs the Flask application with various options."""
    app = create_app()
    
    if workers > 1:
        try:
            import gunicorn.app.base
            class StandaloneApplication(gunicorn.app.base.BaseApplication):
                def __init__(self, app, options=None):
                    self.options = options or {}
                    self.application = app
                    super().__init__()

                def load_config(self):
                    for key, value in self.options.items():
                        self.cfg.set(key, value)

                def load(self):
                    return self.application

            options = {
                'bind': f'{host}:{port}',
                'workers': workers,
                'reload': reload,
                'accesslog': '-',
                'errorlog': '-',
            }
            StandaloneApplication(app, options).run()
        except ImportError:
            click.echo("❌ Gunicorn not installed. Install it with: pip install gunicorn", err=True)
            return
    else:
        app.run(host=host, port=port, debug=debug)

@cli.command("test")
@click.option("--coverage", is_flag=True, help="Run tests with coverage")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--failfast", is_flag=True, help="Stop on first failure")
def test(coverage, verbose, failfast):
    """Runs the tests with various options."""
    import pytest
    
    args = ["tests"]
    if verbose:
        args.append("-v")
    if failfast:
        args.append("-x")
    if coverage:
        args.extend(["--cov=app", "--cov-report=term-missing"])
    
    pytest.main(args)

@cli.command("init_migrations")
@click.option("--force", is_flag=True, help="Force initialization even if migrations exist")
def init_migrations(force):
    """Initializes the database migrations."""
    if os.path.exists("migrations") and not force:
        click.echo("❌ Migrations directory already exists! Use --force to reinitialize.")
        return
    
    try:
        if os.path.exists("migrations") and force:
            import shutil
            shutil.rmtree("migrations")
        
        migrate.init_app(create_app(), db)
        click.echo("✅ Migrations initialized successfully!")
    except Exception as e:
        click.echo(f"❌ Error initializing migrations: {str(e)}", err=True)

@cli.command("migrate")
@click.option("--message", "-m", help="Migration message")
def migrate_db(message):
    """Creates a new migration."""
    try:
        from flask_migrate import migrate as flask_migrate
        flask_migrate(message=message)
        click.echo("✅ Migration created successfully!")
    except Exception as e:
        click.echo(f"❌ Error creating migration: {str(e)}", err=True)

@cli.command("upgrade")
@click.option("--revision", default="head", help="Revision to upgrade to")
def upgrade_db(revision):
    """Upgrades the database to a later version."""
    try:
        upgrade(revision=revision)
        click.echo(f"✅ Database upgraded to {revision} successfully!")
    except Exception as e:
        click.echo(f"❌ Error upgrading database: {str(e)}", err=True)

@cli.command("downgrade")
@click.option("--revision", required=True, help="Revision to downgrade to")
def downgrade_db(revision):
    """Downgrades the database to a previous version."""
    if not click.confirm(f"Are you sure you want to downgrade to {revision}?"):
        return
    
    try:
        downgrade(revision=revision)
        click.echo(f"✅ Database downgraded to {revision} successfully!")
    except Exception as e:
        click.echo(f"❌ Error downgrading database: {str(e)}", err=True)

@cli.command("cleanup")
@click.option("--days", default=30, help="Delete activities older than this many days")
def cleanup(days):
    """Cleans up old user activities."""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted = UserActivity.query.filter(UserActivity.created_at < cutoff_date).delete()
        db.session.commit()
        click.echo(f"✅ Deleted {deleted} old activity records!")
    except Exception as e:
        click.echo(f"❌ Error cleaning up activities: {str(e)}", err=True)

@cli.command("setup_dev")
def setup_dev():
    """Sets up the development environment."""
    try:
        # Create necessary directories
        os.makedirs("logs", exist_ok=True)
        os.makedirs("instance", exist_ok=True)
        
        # Create config.json if it doesn't exist
        if not os.path.exists("config.json"):
            config = {
                "development": {
                    "database_url": "sqlite:///dev.db",
                    "secret_key": "dev-secret-key",
                    "jwt_secret_key": "jwt-dev-secret-key"
                }
            }
            with open("config.json", "w") as f:
                json.dump(config, f, indent=2)
            click.echo("✅ Created config.json")
        
        # Initialize database
        db.create_all()
        click.echo("✅ Database initialized")
        
        # Initialize migrations
        if not os.path.exists("migrations"):
            migrate.init_app(create_app(), db)
            click.echo("✅ Migrations initialized")
        
        click.echo("✅ Development environment setup complete!")
    except Exception as e:
        click.echo(f"❌ Error setting up development environment: {str(e)}", err=True)

if __name__ == "__main__":
    cli()
