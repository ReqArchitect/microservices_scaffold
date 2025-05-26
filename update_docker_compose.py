#!/usr/bin/env python
"""
Script to update docker-compose.yml with enhanced architecture configurations.
This tool will convert your existing docker-compose.yml to the enhanced version
with Consul, Jaeger, and Envoy service mesh.
"""

import os
import sys
import shutil
import yaml
import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Update docker-compose.yml with enhanced architecture")
    parser.add_argument("--backup", action="store_true", help="Create a backup of the original file")
    parser.add_argument("--output", type=str, default="docker-compose-enhanced.yml", 
                      help="Output filename (default: docker-compose-enhanced.yml)")
    return parser.parse_args()

def load_yaml(filename):
    with open(filename, 'r') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"Error parsing {filename}: {e}")
            sys.exit(1)

def save_yaml(data, filename):
    with open(filename, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

def fix_port_conflicts(compose_data):
    """Fix any port conflicts in the services"""
    used_ports = set()
    
    for service_name, service_data in compose_data['services'].items():
        if service_name.endswith('_service') and 'ports' in service_data:
            ports = service_data['ports']
            for i, port_mapping in enumerate(ports):
                if isinstance(port_mapping, str):
                    host_port, container_port = port_mapping.split(':')
                    host_port = host_port.strip('"\'')
                    if host_port in used_ports:
                        # Find an available port
                        new_port = int(host_port) + 1000
                        while str(new_port) in used_ports:
                            new_port += 1
                        
                        print(f"⚠️ Port conflict: {service_name} using {host_port}, changing to {new_port}")
                        ports[i] = f"{new_port}:{container_port}"
                        
                        # Also update environment variables if present
                        if 'environment' in service_data:
                            for j, env_var in enumerate(service_data['environment']):
                                if isinstance(env_var, str) and 'SERVICE_PORT' in env_var:
                                    service_data['environment'][j] = f"SERVICE_PORT={container_port.split('/')[0]}"
                    
                    used_ports.add(host_port)
    
    return compose_data

def enhance_docker_compose(compose_data):
    """Add enhanced architecture components to docker-compose.yml"""
    
    # Add infrastructure services if not present
    services = compose_data['services']
    
    # Add Consul
    if 'consul' not in services:
        services['consul'] = {
            'image': 'consul:1.15',
            'ports': [
                '8500:8500',
                '8600:8600/udp'
            ],
            'command': 'agent -server -ui -node=server-1 -bootstrap-expect=1 -client=0.0.0.0',
            'volumes': [
                'consul_data:/consul/data'
            ],
            'networks': list(compose_data['networks'].keys())[0:1],
            'healthcheck': {
                'test': ['CMD', 'consul', 'members'],
                'interval': '10s',
                'timeout': '5s',
                'retries': 3
            }
        }
    
    # Add Jaeger
    if 'jaeger' not in services:
        services['jaeger'] = {
            'image': 'jaegertracing/all-in-one:1.40',
            'ports': [
                '5775:5775/udp',
                '6831:6831/udp',
                '6832:6832/udp',
                '5778:5778',
                '16686:16686',
                '14268:14268',
                '14250:14250'
            ],
            'environment': [
                'COLLECTOR_ZIPKIN_HOST_PORT=:9411'
            ],
            'networks': list(compose_data['networks'].keys())[0:1]
        }
    
    # Add Envoy
    if 'envoy' not in services:
        services['envoy'] = {
            'image': 'envoyproxy/envoy:v1.24-latest',
            'ports': [
                '9901:9901',
                '10000:10000'
            ],
            'volumes': [
                './service_mesh/envoy.yaml:/etc/envoy/envoy.yaml'
            ],
            'networks': list(compose_data['networks'].keys())[0:1],
            'depends_on': [
                'consul',
                'jaeger'
            ]
        }
    
    # Update service configurations
    for service_name, service_data in services.items():
        if service_name.endswith('_service'):
            # Update environment variables
            if 'environment' not in service_data:
                service_data['environment'] = []
            
            # Extract service port
            port = '5000'  # Default port
            if 'ports' in service_data:
                for port_mapping in service_data['ports']:
                    if isinstance(port_mapping, str):
                        _, container_port = port_mapping.split(':')
                        port = container_port.split('/')[0]
                        break
            
            # Add environment variables for enhanced architecture
            env_vars = service_data['environment']
            
            # Helper function to check if variable exists and add if not
            def add_env_var(name, value):
                var_exists = False
                for i, env_var in enumerate(env_vars):
                    if isinstance(env_var, str) and env_var.startswith(f"{name}="):
                        var_exists = True
                        break
                    elif isinstance(env_var, dict) and name in env_var:
                        var_exists = True
                        break
                
                if not var_exists:
                    env_vars.append(f"{name}={value}")
            
            add_env_var('SERVICE_NAME', service_name)
            add_env_var('SERVICE_PORT', port)
            add_env_var('CONSUL_HOST', 'consul')
            add_env_var('CONSUL_PORT', '8500')
            add_env_var('JAEGER_HOST', 'jaeger')
            add_env_var('JAEGER_PORT', '6831')
            add_env_var('TRACING_ENABLED', 'true')
            add_env_var('API_VERSION', 'v1')
            
            # Add dependencies
            if 'depends_on' not in service_data:
                service_data['depends_on'] = []
            
            # Make sure services depend on infrastructure
            if 'consul' not in service_data['depends_on']:
                service_data['depends_on'].append('consul')
            
            if 'jaeger' not in service_data['depends_on']:
                service_data['depends_on'].append('jaeger')
    
    # Add volumes if needed
    if 'volumes' not in compose_data:
        compose_data['volumes'] = {}
    
    if 'consul_data' not in compose_data['volumes']:
        compose_data['volumes']['consul_data'] = {}
    
    # Check if any database needs persistent volume
    for service_name in services:
        if service_name.endswith('_db'):
            volume_name = f"{service_name}_data"
            if volume_name not in compose_data['volumes']:
                compose_data['volumes'][volume_name] = {}
            
            # Add volume mount to the service if not present
            if 'volumes' not in services[service_name]:
                services[service_name]['volumes'] = []
            
            volume_mount = f"{volume_name}:/var/lib/postgresql/data"
            if volume_mount not in services[service_name]['volumes']:
                services[service_name]['volumes'].append(volume_mount)
    
    # Fix any port conflicts
    compose_data = fix_port_conflicts(compose_data)
    
    # Fix references to URLs in e2e_tests environment variables
    if 'e2e_tests' in services:
        if 'environment' in services['e2e_tests']:
            env_vars = services['e2e_tests']['environment']
            for i, env_var in enumerate(env_vars):
                if isinstance(env_var, str):
                    # Update URLs to include API versioning
                    for service_suffix in ['_URL', '_SERVICE_URL']:
                        if service_suffix in env_var and '=' in env_var:
                            name, value = env_var.split('=', 1)
                            if 'api/' in value and not 'api/v1/' in value:
                                new_value = value.replace('api/', 'api/v1/')
                                env_vars[i] = f"{name}={new_value}"
    
    return compose_data

def main():
    args = parse_args()
    
    # Input file is docker-compose.yml
    input_file = os.path.join(os.path.dirname(__file__), 'docker-compose.yml')
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    # Create backup if requested
    if args.backup:
        backup_file = f"{input_file}.bak"
        shutil.copy(input_file, backup_file)
        print(f"✅ Created backup: {backup_file}")
    
    # Load existing compose file
    compose_data = load_yaml(input_file)
    
    # Enhance it
    enhanced_data = enhance_docker_compose(compose_data)
    
    # Save to output file
    output_file = os.path.join(os.path.dirname(__file__), args.output)
    save_yaml(enhanced_data, output_file)
    print(f"✅ Enhanced docker-compose saved to {output_file}")
    
    print("\nNext steps:")
    print("1. Review the changes in the enhanced docker-compose file")
    print("2. Run the enhanced services with:")
    print(f"   docker-compose -f {args.output} up --build")
    print("3. Check the Consul UI at http://localhost:8500")
    print("4. Check the Jaeger UI at http://localhost:16686")
    print("5. Access your APIs through the Envoy gateway at http://localhost:10000/api/v1/...")

if __name__ == "__main__":
    main()
