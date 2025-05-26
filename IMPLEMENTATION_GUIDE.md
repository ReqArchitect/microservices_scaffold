# Implementing Enhanced Architecture in Microservices

This guide explains how to implement the enhanced architecture components in each microservice of the ReqArchitect system.

## Prerequisites

1. Install the common requirements for all services:
   ```bash
   pip install -r requirements-enhanced.txt
   ```

2. Ensure infrastructure services are running:
   ```bash
   # Start service registry
   cd service_registry
   docker-compose up -d
   
   # Start distributed tracing
   cd ../monitoring/jaeger
   docker-compose up -d
   
   # Start service mesh
   cd ../../
   docker-compose -f docker-compose-enhanced.yml up -d envoy consul jaeger
   ```

## Step 1: Update Config File

Modify your service's `config.py` to include these new settings:

```python
# Service identity and discovery
SERVICE_NAME = os.environ.get('SERVICE_NAME', 'your_service_name')
SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5000))  # Use appropriate default port

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
```

## Step 2: Update requirements.txt

Add these dependencies to your service's `requirements.txt`:

```
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
```

## Step 3: Update Models for Outbox Pattern

Add the OutboxEvent model and modify existing models:

```python
from common_utils.outbox import OutboxMixin
import uuid
import datetime

# Outbox Event model for data consistency
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

# Add OutboxMixin to your domain models
class YourModel(db.Model, OutboxMixin):
    __outbox_enabled__ = True
    
    # Your model fields
    
    def to_dict(self):
        # Return a dictionary representation of your model
        pass
```

## Step 4: Update app/__init__.py

Modify your service's Flask application factory:

```python
from common_utils.service_registry import ServiceRegistry
from common_utils.tracing import Tracer
from common_utils.versioning import VersionedAPI
from prometheus_flask_exporter import PrometheusMetrics

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
metrics = PrometheusMetrics.for_app_factory()
service_registry = ServiceRegistry()
tracer = Tracer()
versioned_api = VersionedAPI()

def create_app(config_object=None):
    app = Flask(__name__)
    # ... existing config setup ...
    
    # Initialize core extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    metrics.init_app(app)
    
    # Initialize enhanced architecture components
    service_registry.init_app(app)
    tracer.init_app(app)
    versioned_api.init_app(app)

    # Register health check endpoint
    @app.route('/health')
    @metrics.do_not_track()
    def health_check():
        return {'status': 'healthy', 'service': app.config.get('SERVICE_NAME')}, 200

    # Import routes with versioning
    from .routes_versioned import create_api_blueprint
    
    # Create and register versioned blueprint
    api_version = app.config.get('API_VERSION')
    api_bp = create_api_blueprint(api_version)
    versioned_api.register_version(api_version, api_bp)
    
    # ... register other blueprints ...

    return app
```

## Step 5: Create Versioned Routes

Create a new file `app/routes_versioned.py`:

```python
from common_utils.versioning import versioned_blueprint, latest_version
from prometheus_flask_exporter import PrometheusMetrics

def create_api_blueprint(version):
    """Create a versioned blueprint for the API"""
    bp = versioned_blueprint('api', __name__, version)
    
    metrics = PrometheusMetrics(bp)
    
    # Define your routes
    @bp.route('/your-endpoint', methods=['GET'])
    @metrics.counter('endpoint_requests', 'Number of requests to this endpoint')
    def your_endpoint():
        # Your route logic
        pass
    
    @bp.route('/another-endpoint', methods=['POST'])
    @latest_version  # Mark this as the latest version
    def another_endpoint():
        # Your route logic
        pass
    
    # ... more routes ...
    
    return bp
```

## Step 6: Add Outbox Processor

Update your `main.py` to include the outbox processor:

```python
from app import create_app, db
from app.models import OutboxEvent
import threading
import time
import logging

app = create_app()

# Background thread for outbox processing
def process_outbox_events():
    """Background thread to process outbox events"""
    with app.app_context():
        from common_utils.outbox import OutboxProcessor
        
        processor = OutboxProcessor(db, OutboxEvent)
        
        # Register handlers for different event types
        @processor.register_handler('your_event_type')
        def handle_your_event(aggregate_id, payload, event):
            # Handle the event
            pass
        
        # Main processing loop
        while True:
            try:
                processed = processor.process_pending_events(limit=10)
                if processed > 0:
                    logging.info(f"Processed {processed} outbox events")
            except Exception as e:
                logging.error(f"Error in outbox processor: {str(e)}")
            
            interval = app.config.get('OUTBOX_PROCESSING_INTERVAL', 10)
            time.sleep(interval)

# Start outbox processor if enabled
outbox_enabled = os.environ.get('OUTBOX_ENABLED', 'true').lower() == 'true'
if outbox_enabled:
    outbox_thread = threading.Thread(target=process_outbox_events, daemon=True)
    outbox_thread.start()

if __name__ == "__main__":
    port = int(os.environ.get('SERVICE_PORT', 5000))
    app.run(host="0.0.0.0", port=port)
```

## Step 7: Update Dockerfile

Ensure your Dockerfile installs the new dependencies:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=main.py

EXPOSE ${SERVICE_PORT:-5000}

CMD ["python", "main.py"]
```

## Step 8: Run Database Migrations

After adding the OutboxEvent model, run migrations:

```bash
flask db migrate -m "Add OutboxEvent model"
flask db upgrade
```

## Testing the Implementation

1. Start your service with the new features:
   ```bash
   python main.py
   ```

2. Check the service registration in Consul:
   - Open Consul UI at http://localhost:8500

3. Monitor distributed traces:
   - Open Jaeger UI at http://localhost:16686
   - Search for traces from your service

4. Test versioned API endpoints:
   - Call your API using versioned endpoints: `/api/v1/your-endpoint`
   - Call unversioned endpoint (redirects to latest): `/api/your-endpoint`

5. Verify outbox events are being processed:
   - Check your logs for outbox processing messages
   - Verify that events trigger the expected side effects
