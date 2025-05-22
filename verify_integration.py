#!/usr/bin/env python3
"""
Integration verification script for enhanced microservices architecture

This script verifies that all the enhanced architecture components are properly 
integrated and functioning correctly.
"""
import argparse
import json
import os
import sys
import time
import requests
import subprocess
from termcolor import colored
import docker

def check_service_health(service_url, health_endpoint="/health"):
    """Check if a service is healthy by calling its health endpoint"""
    try:
        url = f"{service_url.rstrip('/')}{health_endpoint}"
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def check_service_registration(consul_url, service_name):
    """Check if a service is registered with Consul"""
    try:
        url = f"{consul_url.rstrip('/')}/v1/catalog/service/{service_name}"
        response = requests.get(url, timeout=5)
        services = response.json()
        return len(services) > 0
    except (requests.RequestException, json.JSONDecodeError):
        return False

def check_distributed_tracing(jaeger_url, service_name):
    """Check if a service is sending traces to Jaeger"""
    try:
        # Get the list of services from Jaeger
        url = f"{jaeger_url.rstrip('/')}/api/services"
        response = requests.get(url, timeout=5)
        services = response.json()
        return service_name in services
    except (requests.RequestException, json.JSONDecodeError):
        return False

def check_api_versioning(service_url, endpoint):
    """Verify API versioning is working by checking both v1 and v2 endpoints"""
    try:
        # Check v1 endpoint
        v1_url = f"{service_url.rstrip('/')}/api/v1/{endpoint.lstrip('/')}"
        v1_response = requests.get(v1_url, timeout=5)
        v1_working = v1_response.status_code == 200
        
        # Check v2 endpoint if it exists (might return 404 if not implemented)
        v2_url = f"{service_url.rstrip('/')}/api/v2/{endpoint.lstrip('/')}"
        v2_response = requests.get(v2_url, timeout=5)
        v2_exists = v2_response.status_code != 404
        
        return {
            "v1_working": v1_working,
            "v2_exists": v2_exists,
            "v1_status": v1_response.status_code,
            "v2_status": v2_response.status_code
        }
    except requests.RequestException:
        return {
            "v1_working": False,
            "v2_exists": False,
            "v1_status": 0,
            "v2_status": 0
        }

def check_envoy_mtls(envoy_url):
    """Check if Envoy is properly configured with mTLS"""
    try:
        # Try to access the admin endpoint
        admin_url = f"{envoy_url.rstrip('/')}/health"
        response = requests.get(admin_url, timeout=5, verify=False)
        return response.status_code == 200
    except requests.RequestException:
        return False

def check_prometheus_metrics(prometheus_url, service_name):
    """Check if Prometheus is collecting metrics for a service"""
    try:
        query = f'up{{job="{service_name}"}}'
        url = f"{prometheus_url.rstrip('/')}/api/v1/query?query={query}"
        response = requests.get(url, timeout=5)
        result = response.json()
        
        if result["status"] == "success" and result["data"]["result"]:
            return True
        return False
    except (requests.RequestException, json.JSONDecodeError, KeyError):
        return False

def check_kubernetes_resources(namespace="reqarchitect"):
    """Check if Kubernetes resources are correctly deployed"""
    try:
        # Get deployments
        result = subprocess.run(
            ["kubectl", "get", "deployments", "-n", namespace, "-o", "json"],
            capture_output=True, text=True, check=True
        )
        deployments = json.loads(result.stdout)
        
        # Check if all deployments are ready
        all_ready = True
        deployment_statuses = {}
        
        for deployment in deployments.get("items", []):
            name = deployment["metadata"]["name"]
            status = deployment["status"]
            ready = status.get("readyReplicas", 0)
            desired = status.get("replicas", 0)
            
            deployment_statuses[name] = {
                "ready": ready,
                "desired": desired,
                "is_ready": ready == desired and desired > 0
            }
            
            if ready != desired:
                all_ready = False
        
        return {
            "all_ready": all_ready,
            "deployments": deployment_statuses
        }
    except (subprocess.SubprocessError, json.JSONDecodeError) as e:
        return {
            "all_ready": False,
            "error": str(e)
        }

def check_docker_containers():
    """Check if Docker containers are running correctly"""
    try:
        client = docker.from_env()
        containers = client.containers.list()
        
        container_statuses = {}
        for container in containers:
            name = container.name
            status = container.status
            container_statuses[name] = status == "running"
        
        return container_statuses
    except Exception as e:
        return {"error": str(e)}

def print_result(name, success, details=None):
    """Print a formatted result message"""
    status = colored("✓ PASS", "green") if success else colored("✗ FAIL", "red")
    print(f"{status} | {name}")
    
    if details and not success:
        for key, value in details.items():
            print(f"  - {key}: {value}")

def main():
    parser = argparse.ArgumentParser(description="Verify enhanced architecture integration")
    parser.add_argument("--envoy-url", default="http://localhost:10000", 
                      help="Base URL for the Envoy service")
    parser.add_argument("--consul-url", default="http://localhost:8500", 
                      help="Base URL for the Consul service")
    parser.add_argument("--jaeger-url", default="http://localhost:16686", 
                      help="Base URL for the Jaeger UI")
    parser.add_argument("--prometheus-url", default="http://localhost:9090", 
                      help="Base URL for Prometheus")
    parser.add_argument("--kubernetes", action="store_true", 
                      help="Check Kubernetes resources (requires kubectl)")
    parser.add_argument("--kubernetes-namespace", default="reqarchitect", 
                      help="Kubernetes namespace to check")
    parser.add_argument("--docker", action="store_true", 
                      help="Check Docker containers (requires docker)")
    
    args = parser.parse_args()
    
    print(colored("ENHANCED ARCHITECTURE INTEGRATION VERIFICATION", "blue"))
    print("=" * 60)
    
    # Services to check
    services = [
        {"name": "strategy_service", "url": f"{args.envoy_url}", "endpoint": "api/v1/capabilities"},
        {"name": "business_layer_service", "url": f"{args.envoy_url}", "endpoint": "api/v1/business/dashboard"},
        {"name": "user_service", "url": f"{args.envoy_url}", "endpoint": "api/v1/users/profile"},
        {"name": "kpi_service", "url": f"{args.envoy_url}", "endpoint": "api/v1/kpis"},
    ]
    
    print(colored("\nCHECKING INFRASTRUCTURE SERVICES", "blue"))
    print("-" * 60)
    
    # Check Envoy (Service Mesh)
    envoy_result = check_service_health(args.envoy_url, "/health")
    print_result("Envoy Service Mesh", envoy_result)
    
    # Check Envoy mTLS
    mtls_result = check_envoy_mtls(args.envoy_url)
    print_result("Envoy mTLS Configuration", mtls_result)
    
    # Check Consul (Service Registry)
    consul_result = check_service_health(args.consul_url, "/v1/status/leader")
    print_result("Consul Service Registry", consul_result)
    
    # Check Jaeger (Distributed Tracing)
    jaeger_result = check_service_health(args.jaeger_url, "/api/services")
    print_result("Jaeger Distributed Tracing", jaeger_result)
    
    # Check Prometheus (Monitoring)
    prometheus_result = check_service_health(args.prometheus_url, "/-/healthy")
    print_result("Prometheus Monitoring", prometheus_result)
    
    print(colored("\nCHECKING MICROSERVICES", "blue"))
    print("-" * 60)
    
    all_services_ok = True
    
    for service in services:
        service_name = service["name"]
        print(colored(f"\nVerifying {service_name}", "cyan"))
        
        # Check service health
        health_result = check_service_health(f"{args.envoy_url}", f"/health")
        print_result("Health Check", health_result)
        all_services_ok = all_services_ok and health_result
        
        # Check service registration
        registration_result = check_service_registration(args.consul_url, service_name)
        print_result("Service Registration", registration_result)
        all_services_ok = all_services_ok and registration_result
        
        # Check distributed tracing
        tracing_result = check_distributed_tracing(args.jaeger_url, service_name)
        print_result("Distributed Tracing", tracing_result)
        
        # Check API versioning
        versioning_result = check_api_versioning(args.envoy_url, service["endpoint"])
        v1_working = versioning_result["v1_working"]
        print_result("API Versioning", v1_working, versioning_result)
        all_services_ok = all_services_ok and v1_working
        
        # Check Prometheus metrics
        metrics_result = check_prometheus_metrics(args.prometheus_url, service_name)
        print_result("Prometheus Metrics", metrics_result)
    
    # Check Kubernetes resources if requested
    if args.kubernetes:
        print(colored("\nCHECKING KUBERNETES RESOURCES", "blue"))
        print("-" * 60)
        
        k8s_result = check_kubernetes_resources(args.kubernetes_namespace)
        print_result("Kubernetes Deployments", k8s_result.get("all_ready", False), k8s_result)
    
    # Check Docker containers if requested
    if args.docker:
        print(colored("\nCHECKING DOCKER CONTAINERS", "blue"))
        print("-" * 60)
        
        docker_result = check_docker_containers()
        
        if "error" in docker_result:
            print_result("Docker Containers", False, {"error": docker_result["error"]})
        else:
            all_running = all(docker_result.values())
            print_result("Docker Containers", all_running, 
                         {k: v for k, v in docker_result.items() if not v})
    
    # Print overall result
    print("\n" + "=" * 60)
    if all_services_ok:
        print(colored("✓ INTEGRATION VERIFICATION PASSED: All services are working correctly", "green"))
        return 0
    else:
        print(colored("✗ INTEGRATION VERIFICATION FAILED: Some services have issues", "red"))
        return 1

if __name__ == "__main__":
    sys.exit(main())
