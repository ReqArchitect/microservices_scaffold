#!/usr/bin/env python
"""
Enhanced Architecture Deployment Script

This script automates the implementation of enhanced architecture components
across all microservices in the ReqArchitect system, following the 
implementation guide.
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
import re

# Root directory
ROOT_DIR = Path(__file__).resolve().parent

# Services directory pattern
SERVICE_PATTERN = "*_service"

# Backup directory
BACKUP_DIR = ROOT_DIR / "backups"

# Configuration templates
CONFIG_TEMPLATE = """
# Service identity and discovery
SERVICE_NAME = os.environ.get('SERVICE_NAME', '{service_name}')
SERVICE_PORT = int(os.environ.get('SERVICE_PORT', {service_port}))

# Service registry (Consul) configuration
CONSUL_HOST = os.environ.get('CONSUL_HOST', 'localhost')
CONSUL_PORT = int(os.environ.get('CONSUL_PORT', 8500))
AUTO_REGISTER_SERVICE = os.environ.get('AUTO_REGISTER_SERVICE', 'true').lower() == 'true'

# Circuit breaker configuration
CIRCUIT_BREAKER_ENABLED = os.environ.get('CIRCUIT_BREAKER_ENABLED', 'true').lower() == 'true'
CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.environ.get('CIRCUIT_BREAKER_FAILURE_THRESHOLD', 5))
CIRCUIT_BREAKER_RECOVERY_TIMEOUT = int(os.environ.get('CIRCUIT_BREAKER_RECOVERY_TIMEOUT', 30))

# Distributed tracing configuration
JAEGER_HOST = os.environ.get('JAEGER_HOST', 'localhost')
JAEGER_PORT = int(os.environ.get('JAEGER_PORT', 6831))
TRACING_ENABLED = os.environ.get('TRACING_ENABLED', 'true').lower() == 'true'

# API versioning
API_VERSION = os.environ.get('API_VERSION', 'v1')
LATEST_API_VERSION = os.environ.get('LATEST_API_VERSION', 'v1')

# Outbox pattern
OUTBOX_PROCESSING_INTERVAL = int(os.environ.get('OUTBOX_PROCESSING_INTERVAL', 10))  # seconds
OUTBOX_MAX_RETRY = int(os.environ.get('OUTBOX_MAX_RETRY', 3))
OUTBOX_ENABLED = os.environ.get('OUTBOX_ENABLED', 'true').lower() == 'true'
"""

REQUIREMENTS_ADDITIONS = """
# Service Registry
python-consul==1.1.0

# Distributed Tracing
opentelemetry-api>=1.15.0
opentelemetry-sdk>=1.15.0
opentelemetry-exporter-jaeger>=1.15.0
opentelemetry-instrumentation-flask>=0.37b0
opentelemetry-instrumentation-requests>=0.37b0
opentelemetry-instrumentation-sqlalchemy>=0.37b0

# Monitoring
prometheus-flask-exporter>=0.22.4

# API Versioning
apispec>=6.0.0
flask-apispec>=0.11.0
"""

ROUTES_VERSIONED_TEMPLATE = """
from flask import jsonify, request, current_app
from app.models import db
from common_utils.versioning import versioned_blueprint, latest_version
from prometheus_flask_exporter import PrometheusMetrics
from flask_jwt_extended import jwt_required, get_jwt_identity

def create_api_blueprint(version):
    \"\"\"Create a versioned blueprint for the API\"\"\"
    bp = versioned_blueprint('api', __name__, version)
    
    metrics = PrometheusMetrics(bp)
    
    # Health check endpoint (public)
    @bp.route('/health', methods=['GET'])
    @metrics.do_not_track()
    def health_check():
        return jsonify({'status': 'healthy', 'service': current_app.config.get('SERVICE_NAME')}), 200
        
    # TODO: Replace with actual endpoints for this service
    @bp.route('/sample', methods=['GET'])
    @jwt_required()
    @metrics.counter('sample_requests_counter', 'Number of sample endpoint requests')
    @metrics.histogram('sample_requests_histogram', 'Request latency for sample endpoint')
    @latest_version  # Mark as the latest version
    def sample_endpoint():
        user_id = get_jwt_identity()
        return jsonify({
            'message': f'Hello from {current_app.config.get("SERVICE_NAME")}',
            'user_id': user_id,
            'version': version
        }), 200
    
    return bp
"""

OUTBOX_MODEL_TEMPLATE = """
# Outbox Event model for cross-service data consistency
class OutboxEvent(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = db.Column(db.String(100), nullable=False, index=True)
    aggregate_type = db.Column(db.String(100), nullable=False)
    aggregate_id = db.Column(db.String(36), nullable=False)
    payload = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="pending", index=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    error = db.Column(db.Text, nullable=True)
    retry_count = db.Column(db.Integer, default=0)

    @classmethod
    def create_event(cls, session, event_type, aggregate_type, aggregate_id, payload):
        \"\"\"Create a new outbox event\"\"\"
        import json
        event = cls(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=str(aggregate_id),
            payload=json.dumps(payload)
        )
        session.add(event)
        return event
"""

APP_INIT_ADDITIONS = """
from common_utils.service_registry import ServiceRegistry
from common_utils.tracing import Tracer
from common_utils.versioning import VersionedAPI
from prometheus_flask_exporter import PrometheusMetrics

# Initialize extensions
metrics = PrometheusMetrics.for_app_factory()
service_registry = ServiceRegistry()
tracer = Tracer()
versioned_api = VersionedAPI()
"""

APP_INIT_CREATE_APP_ADDITIONS = """
    # Initialize enhanced architecture components
    metrics.init_app(app)
    service_registry.init_app(app)
    tracer.init_app(app)
    versioned_api.init_app(app)

    # Import routes with versioning
    from .routes_versioned import create_api_blueprint
    
    # Create and register versioned blueprint
    api_version = app.config.get('API_VERSION')
    api_bp = create_api_blueprint(api_version)
    versioned_api.register_version(api_version, api_bp)
"""

MAIN_OUTBOX_ADDITIONS = """
# Background thread for outbox processing
def process_outbox_events():
    \"\"\"Background thread to process outbox events\"\"\"
    with app.app_context():
        from common_utils.outbox import OutboxProcessor
        from app.models import OutboxEvent
        
        processor = OutboxProcessor(db, OutboxEvent)
        
        # Register handlers for different event types (customize for each service)
        # Example handler:
        # @processor.register_handler('entity_created')
        # def handle_entity_created(aggregate_id, payload, event):
        #     # Handle the event
        #     pass
        
        # Main processing loop
        while True:
            try:
                processed = processor.process_pending_events(limit=10)
                if processed > 0:
                    app.logger.info(f"Processed {processed} outbox events")
            except Exception as e:
                app.logger.error(f"Error in outbox processor: {str(e)}")
            
            interval = app.config.get('OUTBOX_PROCESSING_INTERVAL', 10)
            time.sleep(interval)

# Start outbox processor if enabled
outbox_enabled = app.config.get('OUTBOX_ENABLED', True)
if outbox_enabled:
    import threading
    import time
    outbox_thread = threading.Thread(target=process_outbox_events, daemon=True)
    outbox_thread.start()
    app.logger.info("Outbox processor started")
"""

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Enhanced Architecture Deployment')
    parser.add_argument('--service', type=str, help='Specific service to upgrade (default: all)')
    parser.add_argument('--skip-backup', action='store_true', help='Skip creating backups')
    parser.add_argument('--dry-run', action='store_true', help='Print actions without executing')
    return parser.parse_args()

def get_services():
    """Get list of all services in the project"""
    services = []
    for path in ROOT_DIR.glob(SERVICE_PATTERN):
        if path.is_dir():
            services.append(path.name)
    return services

def backup_service(service_name):
    """Create a backup of the service"""
    service_path = ROOT_DIR / service_name
    backup_path = BACKUP_DIR / f"{service_name}_{os.path.basename(os.path.normpath(service_path))}_backup"
    
    if not BACKUP_DIR.exists():
        BACKUP_DIR.mkdir()
    
    # Use shutil to copy the entire directory
    shutil.copytree(service_path, backup_path, dirs_exist_ok=True)
    print(f"✅ Backed up {service_name} to {backup_path}")

def get_service_port(service_name):
    """Get the port for a service from its configuration or docker-compose"""
    # Try to extract from docker-compose.yml
    docker_compose_path = ROOT_DIR / "docker-compose.yml"
    if docker_compose_path.exists():
        with open(docker_compose_path, 'r') as f:
            content = f.read()
            # Look for service definition and port
            service_pattern = rf'{service_name}:.*?ports:.*?"(\d+):\d+"'
            match = re.search(service_pattern, content, re.DOTALL)
            if match:
                return match.group(1)
    
    # Default ports based on service name
    default_ports = {
        'user_service': 5000,
        'strategy_service': 5001,
        'business_layer_service': 5002,
        'kpi_service': 5003,
        'business_case_service': 5004,
        'application_layer_service': 5005,
        'auth_service': 5006,
        'initiative_service': 5007,
        'gateway_service': 8080,
        'canvas_service': 5008,
    }
    
    return default_ports.get(service_name, 5000)

def update_config(service_name, dry_run=False):
    """Update the service's config.py with new settings"""
    config_path = ROOT_DIR / service_name / "config.py"
    service_port = get_service_port(service_name)
    
    if not config_path.exists():
        print(f"⚠️ Config file not found for {service_name}")
        return False

    with open(config_path, 'r') as f:
        content = f.read()
    
    # Check if config already contains the new settings
    if 'SERVICE_NAME' in content and 'CONSUL_HOST' in content:
        print(f"ℹ️ Config for {service_name} already contains enhanced settings")
        return True

    # Prepare the new config
    new_content = content.strip() + "\n" + CONFIG_TEMPLATE.format(
        service_name=service_name, 
        service_port=service_port
    )
    
    if dry_run:
        print(f"Would update {config_path}")
        return True
    
    with open(config_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Updated config for {service_name}")
    return True

def update_requirements(service_name, dry_run=False):
    """Update requirements.txt with new dependencies"""
    req_path = ROOT_DIR / service_name / "requirements.txt"
    
    if not req_path.exists():
        print(f"⚠️ requirements.txt not found for {service_name}")
        return False
    
    with open(req_path, 'r') as f:
        content = f.read()
    
    # Check if requirements already contain the new dependencies
    if 'python-consul' in content and 'opentelemetry' in content:
        print(f"ℹ️ Requirements for {service_name} already contain enhanced dependencies")
        return True
    
    # Prepare new requirements
    new_content = content.strip() + "\n" + REQUIREMENTS_ADDITIONS
    
    if dry_run:
        print(f"Would update {req_path}")
        return True
    
    with open(req_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Updated requirements for {service_name}")
    return True

def add_versioned_routes(service_name, dry_run=False):
    """Add versioned routes file"""
    app_dir = ROOT_DIR / service_name / "app"
    
    if not app_dir.exists():
        print(f"⚠️ App directory not found for {service_name}")
        return False
    
    routes_path = app_dir / "routes_versioned.py"
    
    if routes_path.exists():
        print(f"ℹ️ Versioned routes already exist for {service_name}")
        return True
    
    if dry_run:
        print(f"Would create {routes_path}")
        return True
    
    with open(routes_path, 'w') as f:
        f.write(ROUTES_VERSIONED_TEMPLATE)
    
    print(f"✅ Created versioned routes for {service_name}")
    return True

def update_models(service_name, dry_run=False):
    """Update models with OutboxEvent and OutboxMixin"""
    models_path = ROOT_DIR / service_name / "app" / "models.py"
    
    if not models_path.exists():
        print(f"⚠️ Models file not found for {service_name}")
        return False
    
    with open(models_path, 'r') as f:
        content = f.read()
    
    # Check if models already contain OutboxEvent
    if 'OutboxEvent' in content:
        print(f"ℹ️ Models for {service_name} already contain OutboxEvent")
        return True
    
    # Add imports if needed
    imports_to_add = []
    if 'import uuid' not in content:
        imports_to_add.append('import uuid')
    if 'import datetime' not in content:
        imports_to_add.append('import datetime')
    if 'from common_utils.outbox import OutboxMixin' not in content:
        imports_to_add.append('from common_utils.outbox import OutboxMixin')
    
    imports_text = '\n'.join(imports_to_add)
    if imports_text:
        imports_text += '\n'
    
    # Prepare new models content
    new_content = imports_text + content.strip() + "\n\n" + OUTBOX_MODEL_TEMPLATE
    
    if dry_run:
        print(f"Would update {models_path}")
        return True
    
    with open(models_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Updated models for {service_name}")
    return True

def update_app_init(service_name, dry_run=False):
    """Update app/__init__.py with necessary setup"""
    init_path = ROOT_DIR / service_name / "app" / "__init__.py"
    
    if not init_path.exists():
        print(f"⚠️ app/__init__.py not found for {service_name}")
        return False
    
    with open(init_path, 'r') as f:
        content = f.read()
    
    # Check if already updated
    if 'from common_utils.service_registry import ServiceRegistry' in content:
        print(f"ℹ️ app/__init__.py for {service_name} already updated")
        return True
    
    # Find imports section
    import_section_end = content.find('\n\n', content.find('import'))
    if import_section_end == -1:
        import_section_end = len(content)
    
    # Find create_app function
    create_app_match = re.search(r'def create_app\([^)]*\):\s*', content)
    if not create_app_match:
        print(f"⚠️ create_app function not found in {service_name}/app/__init__.py")
        return False
    
    create_app_pos = create_app_match.end()
    
    # Find where to insert the new code inside create_app
    # Look for typical initialization patterns
    init_patterns = [
        r'jwt\.init_app\(app\)',
        r'CORS\(app\)',
        r'migrate\.init_app\(app, db\)'
    ]
    
    insert_pos = -1
    for pattern in init_patterns:
        match = re.search(pattern, content)
        if match:
            insert_pos = match.end()
            # Find the end of the line or statement
            newline_pos = content.find('\n', insert_pos)
            if newline_pos != -1:
                insert_pos = newline_pos + 1
            break
    
    if insert_pos == -1:
        # Fallback: insert after app creation
        app_creation = re.search(r'app = Flask\([^)]*\)', content)
        if app_creation:
            insert_pos = app_creation.end()
            newline_pos = content.find('\n', insert_pos)
            if newline_pos != -1:
                insert_pos = newline_pos + 1
    
    if insert_pos == -1:
        print(f"⚠️ Could not determine where to insert code in {service_name}/app/__init__.py")
        return False
    
    # Prepare the updated content
    new_content = (
        content[:import_section_end] + "\n" + APP_INIT_ADDITIONS + "\n" + 
        content[import_section_end:insert_pos] + APP_INIT_CREATE_APP_ADDITIONS + 
        content[insert_pos:]
    )
    
    if dry_run:
        print(f"Would update {init_path}")
        return True
    
    with open(init_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Updated app/__init__.py for {service_name}")
    return True

def update_main(service_name, dry_run=False):
    """Update main.py with outbox processor"""
    # Check for different possible main file names
    possible_mains = [
        ROOT_DIR / service_name / "main.py",
        ROOT_DIR / service_name / "run.py",
        ROOT_DIR / service_name / "wsgi.py",
        ROOT_DIR / service_name / "app.py"
    ]
    
    main_path = None
    for path in possible_mains:
        if path.exists():
            main_path = path
            break
    
    if not main_path:
        print(f"⚠️ Main application file not found for {service_name}. Checked for main.py, run.py, wsgi.py, app.py")
        return True  # Return True to avoid failing the whole process
    
    with open(main_path, 'r') as f:
        content = f.read()
    
    # Check if already updated
    if 'process_outbox_events' in content:
        print(f"ℹ️ main.py for {service_name} already updated")
        return True
    
    # Find where to insert outbox processor
    # Look for app creation
    app_creation = re.search(r'app = create_app\([^)]*\)', content)
    if not app_creation:
        print(f"⚠️ App creation not found in {service_name}/main.py")
        return False
    
    insert_pos = app_creation.end()
    # Find the end of the line or statement
    newline_pos = content.find('\n', insert_pos)
    if newline_pos != -1:
        insert_pos = newline_pos + 1
    
    # Prepare the updated content
    new_content = content[:insert_pos] + "\n" + MAIN_OUTBOX_ADDITIONS + "\n" + content[insert_pos:]
    
    if dry_run:
        print(f"Would update {main_path}")
        return True
    
    with open(main_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Updated main.py for {service_name}")
    return True

def run_migrations(service_name, dry_run=False):
    """Run database migrations for the service"""
    if dry_run:
        print(f"Would run migrations for {service_name}")
        return True
    
    try:
        os.chdir(ROOT_DIR / service_name)
        subprocess.run([sys.executable, "-m", "flask", "db", "migrate", "-m", "Add OutboxEvent model"], check=True)
        subprocess.run([sys.executable, "-m", "flask", "db", "upgrade"], check=True)
        print(f"✅ Ran migrations for {service_name}")
        os.chdir(ROOT_DIR)
        return True
    except subprocess.SubprocessError as e:
        print(f"⚠️ Error running migrations for {service_name}: {str(e)}")
        os.chdir(ROOT_DIR)
        return False

def implement_service(service_name, skip_backup=False, dry_run=False):
    """Implement enhanced architecture in a single service"""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Implementing enhanced architecture in {service_name}...")
    
    if not skip_backup and not dry_run:
        backup_service(service_name)
    
    # Perform all updates
    status = []
    status.append(update_config(service_name, dry_run))
    status.append(update_requirements(service_name, dry_run))
    status.append(add_versioned_routes(service_name, dry_run))
    status.append(update_models(service_name, dry_run))
    status.append(update_app_init(service_name, dry_run))
    status.append(update_main(service_name, dry_run))
    
    if not dry_run and all(status):
        run_migrations(service_name, dry_run)
    
    if all(status):
        print(f"✅ Successfully implemented enhanced architecture in {service_name}")
    else:
        print(f"⚠️ Some steps failed for {service_name}")

def main():
    """Main entry point"""
    args = parse_args()
    
    # Get services to upgrade
    if args.service:
        services = [args.service]
    else:
        services = get_services()
    
    print(f"{'[DRY RUN] ' if args.dry_run else ''}Implementing enhanced architecture in {len(services)} services: {', '.join(services)}\n")
    
    for service in services:
        implement_service(service, args.skip_backup, args.dry_run)
    
    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Implementation complete!")
    
    if not args.dry_run:
        print("\nNext steps:")
        print("1. Review the changes and ensure all services start correctly")
        print("2. Test the versioned API endpoints")
        print("3. Verify service registration in Consul")
        print("4. Check distributed tracing in Jaeger")
        print("5. Monitor the outbox processing in logs")

if __name__ == "__main__":
    main()
