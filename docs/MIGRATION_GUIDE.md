# Migration Guide for Enhanced Architecture

This guide outlines the steps needed to migrate your existing services to the enhanced architecture. Follow this structured approach to implement each component with minimal disruption.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Service Registry Integration](#service-registry-integration)
3. [API Versioning](#api-versioning)
4. [Distributed Tracing](#distributed-tracing)
5. [Outbox Pattern](#outbox-pattern)
6. [Monitoring and Metrics](#monitoring-and-metrics)
7. [Database Migration](#database-migration)
8. [Testing Your Migration](#testing-your-migration)

## Prerequisites

Before starting, ensure you have:

1. Backed up your service code
2. Installed the necessary dependencies:
   ```
   pip install -r requirements-enhanced.txt
   ```
3. Started the infrastructure services:
   ```
   docker-compose -f docker-compose-enhanced.yml up -d consul jaeger
   ```

## Service Registry Integration

### Step 1: Update Configuration

Add these settings to your `config.py`:

```python
# Service identity
SERVICE_NAME = os.environ.get('SERVICE_NAME', 'your_service_name')
SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5000))

# Service registry (Consul)
CONSUL_HOST = os.environ.get('CONSUL_HOST', 'localhost')
CONSUL_PORT = int(os.environ.get('CONSUL_PORT', 8500))
AUTO_REGISTER_SERVICE = os.environ.get('AUTO_REGISTER_SERVICE', 'true').lower() == 'true'
```

### Step 2: Initialize Service Registry in app/__init__.py

```python
from common_utils.service_registry import ServiceRegistry

# Initialize extension
service_registry = ServiceRegistry()

def create_app():
    # ... existing code ...
    
    # Initialize service registry
    service_registry.init_app(app)
    
    # ... existing code ...
```

### Step 3: Add Health Check Endpoint

If you don't already have one:

```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'service': app.config.get('SERVICE_NAME')}, 200
```

## API Versioning

### Step 1: Add API Version Configuration

```python
# API versioning
API_VERSION = os.environ.get('API_VERSION', 'v1')
LATEST_API_VERSION = os.environ.get('LATEST_API_VERSION', 'v1')
```

### Step 2: Create Versioned Routes

1. Create a new file `app/routes_versioned.py`:

```python
from common_utils.versioning import versioned_blueprint, latest_version

def create_api_blueprint(version):
    """Create a versioned blueprint for the API"""
    bp = versioned_blueprint('api', __name__, version)
    
    # Define your routes here, migrating from existing routes
    @bp.route('/your-endpoint', methods=['GET'])
    @latest_version  # Mark as the latest version if appropriate
    def your_endpoint():
        # Your route logic
        pass
    
    return bp
```

### Step 3: Register Versioned API

```python
from common_utils.versioning import VersionedAPI

# Initialize extension
versioned_api = VersionedAPI()

def create_app():
    # ... existing code ...
    
    # Initialize versioned API
    versioned_api.init_app(app)
    
    # Import and register versioned routes
    from .routes_versioned import create_api_blueprint
    api_version = app.config.get('API_VERSION')
    api_bp = create_api_blueprint(api_version)
    versioned_api.register_version(api_version, api_bp)
    
    # ... existing code ...
```

## Distributed Tracing

### Step 1: Add Tracing Configuration

```python
# Distributed tracing
JAEGER_HOST = os.environ.get('JAEGER_HOST', 'localhost')
JAEGER_PORT = int(os.environ.get('JAEGER_PORT', 6831))
TRACING_ENABLED = os.environ.get('TRACING_ENABLED', 'true').lower() == 'true'
```

### Step 2: Initialize Tracer

```python
from common_utils.tracing import Tracer

# Initialize extension
tracer = Tracer()

def create_app():
    # ... existing code ...
    
    # Initialize tracer
    tracer.init_app(app)
    
    # ... existing code ...
```

## Outbox Pattern

### Step 1: Add Outbox Configuration

```python
# Outbox pattern
OUTBOX_ENABLED = os.environ.get('OUTBOX_ENABLED', 'true').lower() == 'true'
OUTBOX_PROCESSING_INTERVAL = int(os.environ.get('OUTBOX_PROCESSING_INTERVAL', 10))
OUTBOX_MAX_RETRY = int(os.environ.get('OUTBOX_MAX_RETRY', 3))
```

### Step 2: Add OutboxEvent Model

```python
import uuid
import datetime
from common_utils.outbox import OutboxMixin

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
        import json
        event = cls(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=str(aggregate_id),
            payload=json.dumps(payload)
        )
        session.add(event)
        return event
```

### Step 3: Apply OutboxMixin to Domain Models

```python
class YourModel(db.Model, OutboxMixin):
    __outbox_enabled__ = True
    
    # ... existing fields ...
    
    def to_dict(self):
        """Serialize model to dict for API and outbox events"""
        return {
            'id': self.id,
            # Other fields
        }
```

### Step 4: Add Outbox Processor to main.py

```python
import threading
import time

# After app = create_app()

# Background thread for outbox processing
def process_outbox_events():
    with app.app_context():
        from common_utils.outbox import OutboxProcessor
        from app.models import OutboxEvent
        
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
                    app.logger.info(f"Processed {processed} outbox events")
            except Exception as e:
                app.logger.error(f"Error in outbox processor: {str(e)}")
            
            interval = app.config.get('OUTBOX_PROCESSING_INTERVAL', 10)
            time.sleep(interval)

# Start outbox processor if enabled
outbox_enabled = app.config.get('OUTBOX_ENABLED', True)
if outbox_enabled:
    outbox_thread = threading.Thread(target=process_outbox_events, daemon=True)
    outbox_thread.start()
    app.logger.info("Outbox processor started")
```

## Monitoring and Metrics

### Step 1: Initialize Prometheus Metrics

```python
from prometheus_flask_exporter import PrometheusMetrics

# Initialize extension
metrics = PrometheusMetrics.for_app_factory()

def create_app():
    # ... existing code ...
    
    # Initialize metrics
    metrics.init_app(app)
    
    # ... existing code ...
```

### Step 2: Add Metrics to Routes

In your versioned routes:

```python
@bp.route('/your-endpoint', methods=['GET'])
@metrics.counter('endpoint_requests', 'Number of requests to your endpoint')
def your_endpoint():
    # Your route logic
    pass
```

## Database Migration

After adding the OutboxEvent model, run database migrations:

```bash
flask db migrate -m "Add OutboxEvent model for data consistency"
flask db upgrade
```

## Testing Your Migration

1. **Service Registry**:
   - Start your service and check Consul UI (http://localhost:8500)
   - Verify your service is registered with health status

2. **API Versioning**:
   - Test versioned endpoints: `/api/v1/your-endpoint`
   - Test unversioned redirect: `/api/your-endpoint`

3. **Distributed Tracing**:
   - Make a request to your service
   - Check traces in Jaeger UI (http://localhost:16686)

4. **Outbox Pattern**:
   - Perform an action that creates/updates a model
   - Check logs for outbox processing messages
   - Verify the event is processed correctly

5. **Metrics**:
   - Access the metrics endpoint: `/metrics`
   - Verify counters and histograms are being recorded

## Debugging Common Issues

1. **Service not registering in Consul**:
   - Check connectivity to Consul (CONSUL_HOST and CONSUL_PORT)
   - Ensure health check endpoint is available and returns 200

2. **Traces not appearing in Jaeger**:
   - Verify JAEGER_HOST and JAEGER_PORT settings
   - Check that TRACING_ENABLED is set to true

3. **Outbox events not processing**:
   - Check OutboxEvent table in the database
   - Verify outbox processor thread is running
   - Look for errors in logs related to event processing

4. **API version not working**:
   - Ensure versioned_api is properly initialized
   - Check that blueprint is registered with the correct version

## Advanced Configuration

For production environments, consider these additional configurations:

1. **Circuit Breaker**:
   ```python
   CIRCUIT_BREAKER_ENABLED = os.environ.get('CIRCUIT_BREAKER_ENABLED', 'true').lower() == 'true'
   CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.environ.get('CIRCUIT_BREAKER_FAILURE_THRESHOLD', 5))
   CIRCUIT_BREAKER_RECOVERY_TIMEOUT = int(os.environ.get('CIRCUIT_BREAKER_RECOVERY_TIMEOUT', 30))
   ```

2. **Rate Limiting**:
   - Consider adding rate limiting to protect your API from abuse

3. **Secure Configuration**:
   - Move secrets to a secure vault
   - Use environment variables for all configuration in production
