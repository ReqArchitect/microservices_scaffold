# Sample Implementation for Strategy Service
# This file demonstrates how to set up a service with the enhanced architecture components

## Step 1: Update requirements.txt

```txt
# Core Flask
flask>=2.0.0
flask-sqlalchemy>=2.5.0
flask-migrate>=3.0.0
flask-jwt-extended>=4.0.0
flask-cors>=3.0.0
flask-restful>=0.3.9
psycopg2-binary>=2.8.6

# Enhanced Architecture Components
python-consul==1.1.0
opentelemetry-api>=1.15.0
opentelemetry-sdk>=1.15.0
opentelemetry-exporter-jaeger>=1.15.0
opentelemetry-instrumentation-flask>=0.37b0
opentelemetry-instrumentation-requests>=0.37b0
opentelemetry-instrumentation-sqlalchemy>=0.37b0
prometheus-flask-exporter>=0.22.4
apispec>=6.0.0
flask-apispec>=0.11.0
```

## Step 2: Update config.py

```python
import os

class Config:
    """Base configuration."""
    # Original settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///strategy_service.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-secret-key')
    
    # Enhanced architecture settings
    SERVICE_NAME = os.environ.get('SERVICE_NAME', 'strategy_service')
    SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5001))
    
    # Service registry (Consul)
    CONSUL_HOST = os.environ.get('CONSUL_HOST', 'localhost')
    CONSUL_PORT = int(os.environ.get('CONSUL_PORT', 8500))
    AUTO_REGISTER_SERVICE = os.environ.get('AUTO_REGISTER_SERVICE', 'true').lower() == 'true'
    
    # Circuit breaker
    CIRCUIT_BREAKER_ENABLED = os.environ.get('CIRCUIT_BREAKER_ENABLED', 'true').lower() == 'true'
    CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.environ.get('CIRCUIT_BREAKER_FAILURE_THRESHOLD', 5))
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT = int(os.environ.get('CIRCUIT_BREAKER_RECOVERY_TIMEOUT', 30))
    
    # Distributed tracing
    JAEGER_HOST = os.environ.get('JAEGER_HOST', 'localhost')
    JAEGER_PORT = int(os.environ.get('JAEGER_PORT', 6831))
    TRACING_ENABLED = os.environ.get('TRACING_ENABLED', 'true').lower() == 'true'
    
    # API versioning
    API_VERSION = os.environ.get('API_VERSION', 'v1')
    LATEST_API_VERSION = os.environ.get('LATEST_API_VERSION', 'v1')
    
    # Outbox pattern
    OUTBOX_ENABLED = os.environ.get('OUTBOX_ENABLED', 'true').lower() == 'true'
    OUTBOX_PROCESSING_INTERVAL = int(os.environ.get('OUTBOX_PROCESSING_INTERVAL', 10))
    OUTBOX_MAX_RETRY = int(os.environ.get('OUTBOX_MAX_RETRY', 3))
    
    # Swagger documentation
    SWAGGER = {
        'title': 'Strategy Service API',
        'uiversion': 3,
        'version': API_VERSION
    }

class TestConfig(Config):
    """Test configuration."""
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', 'sqlite:///strategy_service_test.db')
    TESTING = True
```

## Step 3: Update app/models.py to include OutboxEvent and outbox mixins

```python
import uuid
import datetime
from app import db
from common_utils.outbox import OutboxMixin

class OutboxEvent(db.Model):
    """Model for the Outbox pattern to ensure data consistency across services"""
    
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
        """Create a new outbox event"""
        import json
        event = cls(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=str(aggregate_id),
            payload=json.dumps(payload)
        )
        session.add(event)
        return event

class Capability(db.Model, OutboxMixin):
    """Strategy capability model with outbox pattern integration"""
    __outbox_enabled__ = True  # Enable outbox pattern for this model
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def to_dict(self):
        """Serialize to dict for API responses and outbox events"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CourseOfAction(db.Model, OutboxMixin):
    """Course of action model with outbox pattern integration"""
    __outbox_enabled__ = True  # Enable outbox pattern for this model
    
    id = db.Column(db.Integer, primary_key=True)
    capability_id = db.Column(db.Integer, db.ForeignKey('capability.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    capability = db.relationship('Capability', backref=db.backref('courses_of_action', lazy=True))
    
    def to_dict(self):
        """Serialize to dict for API responses and outbox events"""
        return {
            'id': self.id,
            'capability_id': self.capability_id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
```

## Step 4: Create versioned routes in app/routes_versioned.py

```python
from flask import jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from common_utils.versioning import versioned_blueprint, latest_version
from prometheus_flask_exporter import PrometheusMetrics
from app.models import db, Capability, CourseOfAction
from app import logger
import uuid
import datetime

def create_api_blueprint(version):
    """Create a versioned blueprint for the API"""
    bp = versioned_blueprint('api', __name__, version)
    metrics = PrometheusMetrics(bp)
    
    # Health check endpoint (public)
    @bp.route('/health', methods=['GET'])
    @metrics.do_not_track()
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': current_app.config.get('SERVICE_NAME'),
            'version': version,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }), 200
    
    # Capabilities endpoints
    @bp.route('/capabilities', methods=['GET'])
    @jwt_required()
    @metrics.counter('get_capabilities_counter', 'Number of get all capabilities requests')
    @metrics.histogram('get_capabilities_latency', 'Latency of get all capabilities requests')
    @latest_version
    def get_capabilities():
        """Get all capabilities"""
        try:
            capabilities = Capability.query.all()
            return jsonify([c.to_dict() for c in capabilities]), 200
        except Exception as e:
            logger.error(f"Error getting capabilities: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/capabilities/<int:id>', methods=['GET'])
    @jwt_required()
    @metrics.counter('get_capability_counter', 'Number of get capability requests')
    @latest_version
    def get_capability(id):
        """Get a specific capability"""
        try:
            capability = Capability.query.get(id)
            if not capability:
                return jsonify({'error': 'Capability not found'}), 404
            return jsonify(capability.to_dict()), 200
        except Exception as e:
            logger.error(f"Error getting capability {id}: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/capabilities', methods=['POST'])
    @jwt_required()
    @metrics.counter('create_capability_counter', 'Number of create capability requests')
    @latest_version
    def create_capability():
        """Create a new capability"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Validate required fields
            required_fields = ['title', 'description']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # Create capability
            capability = Capability(
                title=data['title'],
                description=data['description']
            )
            
            db.session.add(capability)
            db.session.commit()
            
            # Outbox pattern is automatically triggered via the OutboxMixin
            
            return jsonify(capability.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating capability: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/capabilities/<int:id>', methods=['PUT'])
    @jwt_required()
    @metrics.counter('update_capability_counter', 'Number of update capability requests')
    @latest_version
    def update_capability(id):
        """Update a capability"""
        try:
            capability = Capability.query.get(id)
            if not capability:
                return jsonify({'error': 'Capability not found'}), 404
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Update fields
            if 'title' in data:
                capability.title = data['title']
            if 'description' in data:
                capability.description = data['description']
            
            db.session.commit()
            
            # Outbox pattern is automatically triggered via the OutboxMixin
            
            return jsonify(capability.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating capability {id}: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/capabilities/<int:id>', methods=['DELETE'])
    @jwt_required()
    @metrics.counter('delete_capability_counter', 'Number of delete capability requests')
    @latest_version
    def delete_capability(id):
        """Delete a capability"""
        try:
            capability = Capability.query.get(id)
            if not capability:
                return jsonify({'error': 'Capability not found'}), 404
            
            db.session.delete(capability)
            db.session.commit()
            
            # Outbox pattern is automatically triggered via the OutboxMixin
            
            return jsonify({'message': 'Capability deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting capability {id}: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    # Similar endpoints for Courses of Action would be implemented here
    
    return bp
```

## Step 5: Update app/__init__.py to include enhanced architecture components

```python
import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Enhanced architecture components
from common_utils.service_registry import ServiceRegistry
from common_utils.tracing import Tracer
from common_utils.versioning import VersionedAPI
from prometheus_flask_exporter import PrometheusMetrics

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
metrics = PrometheusMetrics.for_app_factory()
service_registry = ServiceRegistry()
tracer = Tracer()
versioned_api = VersionedAPI()

def create_app(config_object=None):
    """Flask application factory"""
    app = Flask(__name__)
    
    # Load configuration
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object('config.Config')
    
    # Initialize core extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
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
    
    # Log initialization
    logger.info(f"Initialized {app.config.get('SERVICE_NAME')} with API version {api_version}")
    
    return app
```

## Step 6: Update main.py to include outbox processor

```python
import os
import threading
import time
from app import create_app, db, logger
from app.models import OutboxEvent

app = create_app()

# Background thread for outbox processing
def process_outbox_events():
    """Background thread to process outbox events"""
    with app.app_context():
        from common_utils.outbox import OutboxProcessor
        
        processor = OutboxProcessor(db, OutboxEvent)
        
        # Register handlers for different event types
        @processor.register_handler('capability_created')
        def handle_capability_created(aggregate_id, payload, event):
            logger.info(f"Processing capability_created event for {aggregate_id}")
            # Add business logic for when a capability is created
            # For example, notify business_layer_service
            
        @processor.register_handler('capability_updated')
        def handle_capability_updated(aggregate_id, payload, event):
            logger.info(f"Processing capability_updated event for {aggregate_id}")
            # Add business logic for when a capability is updated
            
        @processor.register_handler('capability_deleted')
        def handle_capability_deleted(aggregate_id, payload, event):
            logger.info(f"Processing capability_deleted event for {aggregate_id}")
            # Add business logic for when a capability is deleted
        
        # Main processing loop
        while True:
            try:
                processed = processor.process_pending_events(limit=10)
                if processed > 0:
                    logger.info(f"Processed {processed} outbox events")
            except Exception as e:
                logger.error(f"Error in outbox processor: {str(e)}")
            
            interval = app.config.get('OUTBOX_PROCESSING_INTERVAL', 10)
            time.sleep(interval)

# Start outbox processor if enabled
outbox_enabled = app.config.get('OUTBOX_ENABLED', True)
if outbox_enabled:
    outbox_thread = threading.Thread(target=process_outbox_events, daemon=True)
    outbox_thread.start()
    logger.info("Outbox processor started")

if __name__ == "__main__":
    port = app.config.get('SERVICE_PORT', 5001)
    app.run(host='0.0.0.0', port=port)
```

## Step 7: Add Dockerfile with enhanced components

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=main.py
ENV SERVICE_PORT=5001

# Expose port
EXPOSE ${SERVICE_PORT}

# Run the application
CMD ["python", "main.py"]
```

## Running the Enhanced Service

### Local Development

```powershell
# Install dependencies
pip install -r requirements.txt

# Run the service
python main.py
```

### Using Docker Compose

```powershell
# Start infrastructure services
docker-compose -f docker-compose-enhanced.yml up -d consul jaeger

# Start the service
docker-compose -f docker-compose-enhanced.yml up -d strategy_service
```

### Using Kubernetes

```powershell
# Deploy the infrastructure
kubectl apply -f k8s/common-infrastructure.yaml

# Deploy the service
kubectl apply -f k8s/strategy-service.yaml
```

## Testing the Enhanced Architecture

1. **Service Registry**: Check Consul UI at http://localhost:8500
2. **Distributed Tracing**: Check Jaeger UI at http://localhost:16686
3. **API Versioning**: Compare `/api/v1/capabilities` and `/api/capabilities`
4. **Outbox Pattern**: Create a capability and check logs for outbox processing
5. **Metrics**: Check Prometheus metrics at http://localhost:5001/metrics
