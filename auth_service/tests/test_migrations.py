import pytest
import os
from flask import Flask
from flask_migrate import Migrate, upgrade, downgrade
from app import create_app, db

@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = create_app('testing')
    return app

@pytest.fixture
def migrate(app):
    """Create a Migrate instance for testing."""
    return Migrate(app, db)

def test_migration_creation(app, migrate):
    """Test migration creation."""
    with app.app_context():
        # Create migrations directory if it doesn't exist
        migrations_dir = os.path.join(app.root_path, '..', 'migrations')
        if not os.path.exists(migrations_dir):
            os.makedirs(migrations_dir)
        
        # Check if migrations directory exists
        assert os.path.exists(migrations_dir)
        assert os.path.isdir(migrations_dir)
        
        # Check if versions directory exists
        versions_dir = os.path.join(migrations_dir, 'versions')
        assert os.path.exists(versions_dir)
        assert os.path.isdir(versions_dir)

def test_migration_upgrade(app, migrate):
    """Test migration upgrade."""
    with app.app_context():
        # Run upgrade
        upgrade()
        
        # Check if tables are created
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        # Check for expected tables
        assert 'users' in tables
        assert 'tenants' in tables
        assert 'roles' in tables
        assert 'permissions' in tables
        assert 'user_activities' in tables
        assert 'user_roles' in tables
        assert 'role_permissions' in tables

def test_migration_downgrade(app, migrate):
    """Test migration downgrade."""
    with app.app_context():
        # First upgrade to create tables
        upgrade()
        
        # Then downgrade
        downgrade()
        
        # Check if tables are removed
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        # Check that tables are removed
        assert 'users' not in tables
        assert 'tenants' not in tables
        assert 'roles' not in tables
        assert 'permissions' not in tables
        assert 'user_activities' not in tables
        assert 'user_roles' not in tables
        assert 'role_permissions' not in tables

def test_migration_columns(app, migrate):
    """Test migration column definitions."""
    with app.app_context():
        # Run upgrade
        upgrade()
        
        # Get column information
        inspector = db.inspect(db.engine)
        
        # Check users table columns
        user_columns = {col['name']: col for col in inspector.get_columns('users')}
        assert 'id' in user_columns
        assert 'email' in user_columns
        assert 'password' in user_columns
        assert 'first_name' in user_columns
        assert 'last_name' in user_columns
        assert 'tenant_id' in user_columns
        assert 'is_active' in user_columns
        assert 'is_superuser' in user_columns
        assert 'last_login' in user_columns
        assert 'created_at' in user_columns
        assert 'updated_at' in user_columns
        
        # Check tenants table columns
        tenant_columns = {col['name']: col for col in inspector.get_columns('tenants')}
        assert 'id' in tenant_columns
        assert 'name' in tenant_columns
        assert 'description' in tenant_columns
        assert 'is_active' in tenant_columns
        assert 'created_at' in tenant_columns
        assert 'updated_at' in tenant_columns
        
        # Check roles table columns
        role_columns = {col['name']: col for col in inspector.get_columns('roles')}
        assert 'id' in role_columns
        assert 'name' in role_columns
        assert 'description' in role_columns
        assert 'created_at' in role_columns
        assert 'updated_at' in role_columns
        
        # Check permissions table columns
        permission_columns = {col['name']: col for col in inspector.get_columns('permissions')}
        assert 'id' in permission_columns
        assert 'name' in permission_columns
        assert 'description' in permission_columns
        assert 'created_at' in permission_columns
        assert 'updated_at' in permission_columns

def test_migration_foreign_keys(app, migrate):
    """Test migration foreign key constraints."""
    with app.app_context():
        # Run upgrade
        upgrade()
        
        # Get foreign key information
        inspector = db.inspect(db.engine)
        
        # Check users table foreign keys
        user_fks = inspector.get_foreign_keys('users')
        assert any(fk['referred_table'] == 'tenants' for fk in user_fks)
        
        # Check user_activities table foreign keys
        activity_fks = inspector.get_foreign_keys('user_activities')
        assert any(fk['referred_table'] == 'users' for fk in activity_fks)
        
        # Check user_roles table foreign keys
        user_role_fks = inspector.get_foreign_keys('user_roles')
        assert any(fk['referred_table'] == 'users' for fk in user_role_fks)
        assert any(fk['referred_table'] == 'roles' for fk in user_role_fks)
        
        # Check role_permissions table foreign keys
        role_permission_fks = inspector.get_foreign_keys('role_permissions')
        assert any(fk['referred_table'] == 'roles' for fk in role_permission_fks)
        assert any(fk['referred_table'] == 'permissions' for fk in role_permission_fks)

def test_migration_indexes(app, migrate):
    """Test migration indexes."""
    with app.app_context():
        # Run upgrade
        upgrade()
        
        # Get index information
        inspector = db.inspect(db.engine)
        
        # Check users table indexes
        user_indexes = inspector.get_indexes('users')
        assert any(idx['name'] == 'ix_users_email' for idx in user_indexes)
        
        # Check tenants table indexes
        tenant_indexes = inspector.get_indexes('tenants')
        assert any(idx['name'] == 'ix_tenants_name' for idx in tenant_indexes)
        
        # Check roles table indexes
        role_indexes = inspector.get_indexes('roles')
        assert any(idx['name'] == 'ix_roles_name' for idx in role_indexes)
        
        # Check permissions table indexes
        permission_indexes = inspector.get_indexes('permissions')
        assert any(idx['name'] == 'ix_permissions_name' for idx in permission_indexes)

def test_migration_unique_constraints(app, migrate):
    """Test migration unique constraints."""
    with app.app_context():
        # Run upgrade
        upgrade()
        
        # Get unique constraint information
        inspector = db.inspect(db.engine)
        
        # Check users table unique constraints
        user_indexes = inspector.get_indexes('users')
        email_index = next(idx for idx in user_indexes if idx['name'] == 'ix_users_email')
        assert email_index['unique'] is True
        
        # Check tenants table unique constraints
        tenant_indexes = inspector.get_indexes('tenants')
        name_index = next(idx for idx in tenant_indexes if idx['name'] == 'ix_tenants_name')
        assert name_index['unique'] is True
        
        # Check roles table unique constraints
        role_indexes = inspector.get_indexes('roles')
        name_index = next(idx for idx in role_indexes if idx['name'] == 'ix_roles_name')
        assert name_index['unique'] is True
        
        # Check permissions table unique constraints
        permission_indexes = inspector.get_indexes('permissions')
        name_index = next(idx for idx in permission_indexes if idx['name'] == 'ix_permissions_name')
        assert name_index['unique'] is True 