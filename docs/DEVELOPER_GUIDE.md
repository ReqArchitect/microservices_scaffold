# Developer Documentation for Enhanced Microservices Architecture

## Table of Contents

1. [Overview](#overview)
2. [Architecture Components](#architecture-components)
3. [Setup Instructions](#setup-instructions)
4. [Development Workflow](#development-workflow)
5. [Security](#security)
6. [Monitoring and Observability](#monitoring-and-observability)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)
10. [API Reference](#api-reference)

## Overview

This document provides comprehensive guidance for developers working with our enhanced microservices architecture. The architecture is built on Flask with several components that support resilient, scalable, and maintainable microservices.

## Architecture Components

### Service Mesh with Envoy

Our service mesh implementation uses Envoy proxy to provide:

- Layer 7 routing and load balancing
- Health checks and circuit breaking
- Metrics collection and request tracing
- mTLS for service-to-service communication
- Retry and timeout policies

**Usage:**
```python
# No special integration code needed - Envoy handles traffic routing
# Reference services using their service name
response = requests.get("http://strategy-service:5001/api/v1/capabilities")
```

### Service Registry and Discovery (Consul)

Services register with Consul for dynamic discovery:

```python
# In your Flask application initialization
from common_utils.service_registry import register_service

register_service(app, service_name, service_port)
```

### Distributed Tracing (Jaeger/OpenTelemetry)

Track request flows across services:

```python
# Initialize tracing in your Flask application
from common_utils.tracing import init_tracer

init_tracer(app, service_name)

# Create spans for important operations
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("operation_name"):
    # Your code here
    pass
```

### Data Consistency (Outbox Pattern)

Ensure cross-service data consistency:

```python
# Import the OutboxEvent model
from common_utils.outbox import OutboxEvent

# Create a new outbox event within a transaction
def update_entity(db_session, entity_id, data):
    with db_session.begin_nested():
        entity = Entity.query.get(entity_id)
        entity.name = data["name"]
        db_session.add(entity)
        
        # Create outbox event
        event = OutboxEvent(
            aggregate_type="Entity",
            aggregate_id=str(entity_id),
            event_type="EntityUpdated",
            payload=json.dumps(data)
        )
        db_session.add(event)
        
    db_session.commit()
```

The background processor will automatically process these events.

### API Versioning

Version your APIs to maintain backward compatibility:

```python
# In your Flask application
from common_utils.versioning import create_versioned_blueprint

# Create a versioned blueprint
v1_blueprint = create_versioned_blueprint("v1", __name__)

# Define routes on the versioned blueprint
@v1_blueprint.route("/resource")
def get_resource_v1():
    return jsonify({"version": "v1", "data": [...]})

v2_blueprint = create_versioned_blueprint("v2", __name__)

@v2_blueprint.route("/resource")
def get_resource_v2():
    return jsonify({"version": "v2", "data": [...]})

# Register the blueprints with your Flask application
app.register_blueprint(v1_blueprint, url_prefix="/api/v1")
app.register_blueprint(v2_blueprint, url_prefix="/api/v2")
```

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Kubernetes (minikube or a cloud provider)
- Python 3.8+
- kubectl

### Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/your-org/flask_microservices_scaffold.git
cd flask_microservices_scaffold
```

2. Install required dependencies:
```bash
python setup_local_env.py
```

3. Start the development environment:
```bash
docker-compose -f docker-compose-enhanced.yml up
```

### Setting up Kubernetes Environment

1. Apply infrastructure components:
```bash
kubectl apply -f k8s/common-infrastructure.yaml
```

2. Deploy services:
```bash
./k8s/deploy_all.sh
```

## Development Workflow

### Creating a New Service

1. Create a new service directory:
```bash
mkdir my_service
cd my_service
```

2. Create the basic structure:
```
my_service/
  ├── app/
  │   ├── __init__.py
  │   ├── models.py
  │   └── routes_versioned.py
  ├── migrations/
  ├── tests/
  ├── config.py
  ├── main.py
  └── requirements.txt
```

3. Implement the required components:
   - Service registration
   - Tracing
   - API versioning
   - Health checks

### Adding APIs

1. Create routes in `routes_versioned.py`:
```python
from common_utils.versioning import create_versioned_blueprint

v1 = create_versioned_blueprint("v1", __name__)

@v1.route("/resource", methods=["GET"])
def get_resources():
    # Implementation
    pass

@v1.route("/resource/<resource_id>", methods=["GET", "PUT", "DELETE"])
def resource_operations(resource_id):
    # Implementation
    pass
```

2. Register the blueprint in `app/__init__.py`:
```python
from app.routes_versioned import v1

app.register_blueprint(v1, url_prefix="/api/v1")
```

### Implementing Cross-Service Interactions

Use the outbox pattern:

```python
# Producer service
def create_resource(db_session, resource_data):
    with db_session.begin_nested():
        # Create the resource
        resource = Resource(**resource_data)
        db_session.add(resource)
        
        # Create an outbox event
        event = OutboxEvent(
            aggregate_type="Resource",
            aggregate_id=str(resource.id),
            event_type="ResourceCreated",
            payload=json.dumps(resource_data)
        )
        db_session.add(event)
    
    db_session.commit()
    return resource
```

```python
# Consumer service
@event_consumer.register("ResourceCreated")
def handle_resource_created(event_data):
    # Process the event
    resource_data = json.loads(event_data["payload"])
    # Update local data or trigger additional processing
    pass
```

## Security

### mTLS Configuration

The service mesh provides mutual TLS authentication between services:

1. Certificates must be generated using:
```bash
./service_mesh/generate_certs.sh
```

2. Certificate secrets must be applied:
```bash
kubectl apply -f k8s/tls-secrets.yaml
```

### JWT Authentication

Services should validate the JWT token provided by the Auth service:

```python
from common_utils.auth import jwt_required

@app.route("/protected-resource")
@jwt_required
def protected_resource():
    # Access the current user from the JWT token
    current_user = g.user
    return jsonify({"message": "Access granted to", "user": current_user})
```

## Monitoring and Observability

### Accessing Dashboards

- **Consul UI**: http://localhost:8500
- **Jaeger UI**: http://localhost:16686
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090

### Adding Custom Metrics

Use Prometheus metrics:

```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

# Create a custom metric
custom_counter = metrics.counter(
    'custom_counter', 'Description of the metric',
    labels={'label1': 'value1', 'label2': 'value2'}
)

@app.route('/endpoint')
@custom_counter
def endpoint():
    # This endpoint will increment the custom counter
    return "OK"
```

## Testing

### Unit Testing

Run unit tests for a specific service:
```bash
cd service_name
python -m pytest
```

### Integration Testing

Run integration tests that verify cross-service functionality:
```bash
python -m pytest e2e_tests/
```

### Chaos Testing

Run chaos experiments to test resilience:
```bash
python run_chaos_tests.py --experiment service_resilience_experiment.json
```

## Test Data Management
- All tests use fixtures and factories for isolation
- Global test data seeding/cleanup scripts are in `scripts/`
- Multi-tenant and RBAC scenarios are parameterized

## Advanced Testing
- Run `make contract-test` for contract tests (Schemathesis/Dredd)
- Run `make security-scan` for Bandit/Trivy
- Run `make chaos-test` for chaos/fault injection

## CI/CD
- All tests, security scans, and contract tests run in CI
- Coverage and security badges are in the README

## Deployment

### Kubernetes Deployment

1. Build and push service images:
```bash
docker build -t your-registry/service-name:version service_name/
docker push your-registry/service-name:version
```

2. Update the image tag in the Kubernetes manifest:
```yaml
containers:
- name: service-name
  image: your-registry/service-name:version
```

3. Apply the updated manifest:
```bash
kubectl apply -f k8s/service-name.yaml
```

### Rolling Updates

Kubernetes handles rolling updates automatically. To trigger one:
```bash
kubectl rollout restart deployment/service-name -n reqarchitect
```

## Troubleshooting

### Checking Service Health

```bash
kubectl exec -it pod-name -n reqarchitect -- curl localhost:port/health
```

### Viewing Service Logs

```bash
kubectl logs -f deployment/service-name -n reqarchitect
```

### Distributed Tracing for Debugging

1. Access the Jaeger UI (http://localhost:16686)
2. Search for traces by:
   - Service
   - Operation
   - Duration
   - Tags

### Common Issues

- **Service Cannot Connect to Database**: Check database credentials and connection string
- **Service Not Registering with Consul**: Verify Consul is running and accessible
- **Tracing Not Working**: Ensure JAEGER_HOST and JAEGER_PORT environment variables are correctly set

## API Reference

### Common API Patterns

All APIs should follow these conventions:

1. Base URL: `/api/v{version}/{resource}`
2. Response format:
```json
{
  "data": {...},
  "metadata": {
    "version": "v1",
    "timestamp": "2023-01-01T12:00:00Z"
  }
}
```
3. Error format:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {...}
  }
}
```

### HTTP Status Codes

- 200: Success
- 201: Created
- 204: No Content
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 409: Conflict
- 500: Internal Server Error
