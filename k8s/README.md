# Kubernetes Deployment Guide

This guide explains how to deploy the ReqArchitect microservices to a Kubernetes cluster.

## Prerequisites

- Kubernetes cluster (local or cloud)
- kubectl installed and configured
- Docker installed
- Container registry access (Docker Hub, Azure Container Registry, etc.)

## Architecture Overview

The ReqArchitect microservices are deployed in Kubernetes with the following components:

- **Infrastructure Services:**
  - Consul (Service Registry)
  - Jaeger (Distributed Tracing)
  - Envoy (Service Mesh)
  - Prometheus/Grafana (Monitoring)

- **Application Services:**
  - User Service
  - Strategy Service
  - Business Layer Service
  - KPI Service
  - Initiative Service
  - Canvas Service
  - Business Case Service

## Deployment Steps

### 1. Build and Push Docker Images

First, build and push Docker images for all services:

```bash
# Set your registry/repo
export REGISTRY=yourregistry

# Build and push images for each service
for service in user_service strategy_service business_layer_service kpi_service initiative_service canvas_service business_case_service; do
  docker build -t $REGISTRY/reqarchitect/$service:latest ./$service
  docker push $REGISTRY/reqarchitect/$service:latest
done
```

Update the image name in each service's Kubernetes manifest if necessary.

### 2. Create Kubernetes Namespace

Apply the namespace configuration:

```bash
kubectl apply -f k8s/common-infrastructure.yaml
```

### 3. Deploy Infrastructure Services

```bash
# Apply infrastructure components (includes namespace creation)
kubectl apply -f k8s/common-infrastructure.yaml
```

### 4. Deploy Application Services

Deploy each microservice:

```bash
kubectl apply -f k8s/user-service.yaml
kubectl apply -f k8s/strategy-service.yaml
kubectl apply -f k8s/business-layer-service.yaml
kubectl apply -f k8s/kpi-service.yaml
kubectl apply -f k8s/initiative-service.yaml
kubectl apply -f k8s/canvas-service.yaml
kubectl apply -f k8s/business-case-service.yaml
```

### 5. Verify Deployment

Check that all pods are running:

```bash
kubectl get pods -n reqarchitect
```

Verify services:

```bash
kubectl get services -n reqarchitect
```

### 6. Access Services

#### Internal Access

Services communicate internally using their service names. For example:

- `user-service.reqarchitect.svc.cluster.local`
- `strategy-service.reqarchitect.svc.cluster.local`

#### External Access

To access the services externally, you'll need to:

1. Set up an Ingress controller (like NGINX or Traefik), or
2. Use a LoadBalancer service, or
3. Use port-forwarding for development purposes:

```bash
# Forward traffic to the Envoy proxy
kubectl port-forward service/envoy-service 10000:10000 -n reqarchitect
```

## Configuration Management

### Environment Variables

Each service's deployment includes environment variables for configuration. Update the ConfigMaps in each service YAML file to customize the configuration.

### Secrets Management

Database credentials and JWT secrets are stored as Kubernetes Secrets. In production, consider using a secure secrets management solution like HashiCorp Vault or cloud provider solutions (AWS Secrets Manager, Azure Key Vault, etc.).

## Scaling Services

Services can be scaled using the kubectl scale command:

```bash
kubectl scale deployment strategy-service --replicas=3 -n reqarchitect
```

For horizontal autoscaling based on CPU usage:

```bash
kubectl autoscale deployment strategy-service --min=2 --max=5 --cpu-percent=70 -n reqarchitect
```

## Health Monitoring

Each service includes readiness and liveness probes configured in the Kubernetes manifests. You can monitor the health and metrics through:

- Prometheus/Grafana dashboards
- Kubernetes Dashboard
- Consul UI
- Jaeger UI

## Troubleshooting

### Checking Logs

```bash
# View logs for a specific pod
kubectl logs <pod-name> -n reqarchitect

# Follow logs in real-time
kubectl logs -f <pod-name> -n reqarchitect
```

### Common Issues

1. **Database Connection Issues**
   - Check that database services are running
   - Verify database credentials in secrets
   - Check network policies if using network isolation

2. **Service Discovery Issues**
   - Check Consul service (port 8500)
   - Verify service registration in Consul UI

3. **Authorization Issues**
   - Verify JWT secret configuration
   - Check user service for token validation

## Production Considerations

For production deployments, consider:

1. **High Availability**
   - Deploy multiple replicas of each service
   - Use pod disruption budgets
   - Deploy across multiple availability zones

2. **Security**
   - Enable network policies
   - Use mTLS with service mesh
   - Implement proper RBAC
   - Scan container images for vulnerabilities

3. **Monitoring and Alerts**
   - Set up alerts for service health
   - Monitor resource usage
   - Set up log aggregation

## Cluster Management Scripts

For convenience, the following scripts are available:

- `k8s/deploy_all.sh`: Deploy all services with a single command
- `k8s/update_all.sh`: Update all service deployments
- `k8s/teardown.sh`: Remove all ReqArchitect resources from cluster
