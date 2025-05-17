import os
import sys
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Tenant

def init_db():
    """Initialize the database with a vendor admin."""
    app = create_app()
    
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Check if vendor admin already exists
        if User.query.filter_by(role='vendor_admin').first():
            print("Vendor admin already exists.")
            return
            
        # Create default tenant
        default_tenant = Tenant(
            name='Default Tenant',
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            settings={
                'max_users': 100,
                'allowed_roles': ['user', 'tenant_admin'],
                'features': ['basic', 'advanced']
            }
        )
        db.session.add(default_tenant)
        db.session.commit()
        
        # Create vendor admin
        vendor_admin = User(
            email='admin@example.com',
            full_name='Vendor Admin',
            role='vendor_admin',
            tenant_id=default_tenant.id,
            is_active=True,
            is_email_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        vendor_admin.set_password('admin123')  # Change this in production!
        
        db.session.add(vendor_admin)
        db.session.commit()
        
        print("Database initialized with vendor admin:")
        print(f"Email: {vendor_admin.email}")
        print(f"Password: admin123")
        print("\nIMPORTANT: Change the admin password immediately!")

if __name__ == '__main__':
    init_db() 