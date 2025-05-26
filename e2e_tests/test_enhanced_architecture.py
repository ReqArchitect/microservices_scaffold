"""
Integration tests for enhanced architecture components.
Tests the complete flow through service mesh, service registry, and tracing.
"""
import unittest
import requests
import time
import os
import docker
import subprocess
import json
from datetime import datetime

class EnhancedArchitectureIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Start required services for testing"""
        print("Starting infrastructure services...")
        
        # Start Docker Compose services
        subprocess.run(
            ["docker-compose", "-f", "docker-compose-enhanced.yml", "up", "-d", 
             "consul", "jaeger", "envoy"],
            check=True
        )
        
        # Wait for services to be ready
        time.sleep(10)
        
        # Start test services
        subprocess.run(
            ["docker-compose", "-f", "docker-compose-enhanced.yml", "up", "-d", 
             "strategy_service", "business_layer_service", "user_service"],
            check=True
        )
        
        # Wait for services to be ready
        time.sleep(15)
        
        print("Services started successfully.")

    @classmethod
    def tearDownClass(cls):
        """Stop services after testing"""
        print("Stopping services...")
        subprocess.run(
            ["docker-compose", "-f", "docker-compose-enhanced.yml", "down"],
            check=True
        )

    def test_service_registration(self):
        """Test that services register with Consul"""
        # Query Consul API
        response = requests.get("http://localhost:8500/v1/catalog/services")
        self.assertEqual(response.status_code, 200)
        
        services = response.json()
        expected_services = ["strategy_service", "business_layer_service", "user_service"]
        
        for service in expected_services:
            self.assertIn(service, services, f"Service {service} not registered in Consul")
            
        print("Service registration test passed.")
    
    def test_api_versioning(self):
        """Test API versioning works correctly"""
        # Test with explicit version
        response = requests.get("http://localhost:10000/api/v1/health", 
                               headers={"Authorization": "Bearer test_token"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("X-API-Version"), "v1")
        
        # Test with unversioned endpoint (should redirect to latest version)
        response = requests.get("http://localhost:10000/api/health", 
                               headers={"Authorization": "Bearer test_token"})
        self.assertEqual(response.status_code, 200)
        
        print("API versioning test passed.")
    
    def test_distributed_tracing(self):
        """Test that distributed tracing works"""
        # Generate some traffic
        for _ in range(5):
            requests.get("http://localhost:10000/api/v1/health")
            time.sleep(1)
        
        # Query Jaeger for traces
        time.sleep(2)  # Wait for traces to be processed
        response = requests.get("http://localhost:16686/api/traces?service=strategy_service")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertGreater(len(data.get("data", [])), 0, "No traces found in Jaeger")
        
        print("Distributed tracing test passed.")
    
    def test_outbox_pattern(self):
        """Test the outbox pattern for cross-service communication"""
        # Create a test entity that will trigger an outbox event
        test_data = {
            "title": f"Test Capability {datetime.now().isoformat()}",
            "description": "Test description for integration testing"
        }
        
        response = requests.post(
            "http://localhost:10000/api/v1/capabilities",
            json=test_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        self.assertEqual(response.status_code, 201)
        
        # Wait for outbox processing
        time.sleep(5)
        
        # Verify the outbox event was processed
        # This would ideally check a downstream effect, but we'll just check the logs
        docker_client = docker.from_env()
        container = docker_client.containers.get("flask_microservices_scaffold_strategy_service_1")
        logs = container.logs().decode('utf-8')
        
        self.assertIn("Processed", logs, "No evidence of outbox processing in logs")
        
        print("Outbox pattern test passed.")

if __name__ == "__main__":
    unittest.main()
