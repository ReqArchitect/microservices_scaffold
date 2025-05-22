#!/bin/bash
# Deploy all ReqArchitect services to Kubernetes

set -e  # Exit on error

echo "Starting deployment of ReqArchitect services..."

# Deploy common infrastructure
echo "Deploying infrastructure components..."
kubectl apply -f common-infrastructure.yaml

# Wait for infrastructure to be ready
echo "Waiting for infrastructure to be ready..."
kubectl wait --for=condition=ready pod -l app=consul --timeout=120s -n reqarchitect || true
kubectl wait --for=condition=ready pod -l app=jaeger --timeout=120s -n reqarchitect || true

# Deploy all application services
echo "Deploying application services..."
kubectl apply -f user-service.yaml
kubectl apply -f strategy-service.yaml
kubectl apply -f business-layer-service.yaml
kubectl apply -f kpi-service.yaml
kubectl apply -f initiative-service.yaml
kubectl apply -f canvas-service.yaml
kubectl apply -f business-case-service.yaml

# Wait for all pods to be ready
echo "Waiting for all pods to be ready..."
kubectl wait --for=condition=ready pod -l app=user-service --timeout=120s -n reqarchitect || true
kubectl wait --for=condition=ready pod -l app=strategy-service --timeout=120s -n reqarchitect || true
kubectl wait --for=condition=ready pod -l app=business-layer-service --timeout=120s -n reqarchitect || true
kubectl wait --for=condition=ready pod -l app=kpi-service --timeout=120s -n reqarchitect || true
kubectl wait --for=condition=ready pod -l app=initiative-service --timeout=120s -n reqarchitect || true
kubectl wait --for=condition=ready pod -l app=canvas-service --timeout=120s -n reqarchitect || true
kubectl wait --for=condition=ready pod -l app=business-case-service --timeout=120s -n reqarchitect || true

echo "Deployment completed successfully!"
echo "To access the services, run: kubectl port-forward service/envoy-service 10000:10000 -n reqarchitect"
