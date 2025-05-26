#!/usr/bin/env python3
"""
Performance profiling and optimization tool for microservices
"""
import argparse
import subprocess
import os
import sys
import time
import json
from datetime import datetime
import requests

def profile_service(service_name, endpoint, duration=60, workers=10, requests_per_second=50):
    """Profile a service using wrk HTTP benchmarking tool"""
    print(f"Profiling service: {service_name} at endpoint: {endpoint}")
    
    # Directory to store profile results
    profile_dir = f"./performance/profiles/{service_name}"
    os.makedirs(profile_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{profile_dir}/profile_{timestamp}.json"
    
    try:
        # Run the HTTP benchmark
        result = subprocess.run([
            "wrk", 
            "-t", str(workers),
            "-c", str(workers * 5),  # Number of connections
            "-d", f"{duration}s",
            "-R", str(requests_per_second),
            "--latency",
            endpoint
        ], capture_output=True, text=True, check=True)
        
        # Parse the output
        output = result.stdout
        
        # Basic parsing of wrk output
        lines = output.strip().split('\n')
        latency_line = next((l for l in lines if 'Latency' in l), None)
        req_sec_line = next((l for l in lines if 'Req/Sec' in l), None)
        
        latency_avg = latency_line.split()[1] if latency_line else "N/A"
        req_sec_avg = req_sec_line.split()[1] if req_sec_line else "N/A"
        
        # Save the results
        profile_result = {
            "service": service_name,
            "endpoint": endpoint,
            "timestamp": timestamp,
            "duration": duration,
            "workers": workers,
            "requests_per_second": requests_per_second,
            "average_latency": latency_avg,
            "average_requests_per_second": req_sec_avg,
            "raw_output": output
        }
        
        with open(output_file, 'w') as f:
            json.dump(profile_result, f, indent=2)
        
        print(f"Profile completed for {service_name}.")
        print(f"Average latency: {latency_avg}")
        print(f"Average requests/second: {req_sec_avg}")
        print(f"Full results saved to: {output_file}")
        
        return profile_result
    
    except subprocess.CalledProcessError as e:
        print(f"Error profiling service {service_name}: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return None

def generate_optimizations(profile_result):
    """Generate optimization suggestions based on profile results"""
    latency = profile_result.get("average_latency", "N/A")
    req_sec = profile_result.get("average_requests_per_second", "N/A")
    
    # Extract numeric latency value (removing units)
    numeric_latency = float(''.join(c for c in latency if c.isdigit() or c == '.'))
    latency_unit = ''.join(c for c in latency if not c.isdigit() and c != '.')
    
    suggestions = []
    
    if latency_unit == 'ms' and numeric_latency > 100:
        suggestions.append("High latency detected. Consider optimizing database queries.")
        suggestions.append("Implement caching for frequently accessed data.")
    
    if latency_unit == 's':
        suggestions.append("Very high latency detected. Consider asyncio for IO-bound operations.")
        suggestions.append("Check for potential deadlocks or resource contention.")
    
    # Add generic optimization suggestions
    suggestions.extend([
        "Optimize database indexes for common query patterns.",
        "Consider adding a Redis cache layer for frequently accessed data.",
        "Use connection pooling for database connections.",
        "Implement proper database connection handling and timeouts.",
        "Consider using async tasks for background processing.",
        "Review logging levels in production to reduce overhead.",
        "Ensure proper HTTP connection handling including keepalive settings."
    ])
    
    return suggestions

def profile_common_services():
    """Profile common services in the architecture"""
    services_to_profile = [
        {"name": "strategy_service", "endpoint": "http://localhost:10000/api/v1/capabilities"},
        {"name": "business_layer_service", "endpoint": "http://localhost:10000/api/v1/business/dashboard"},
        {"name": "user_service", "endpoint": "http://localhost:10000/api/v1/users/profile"},
        {"name": "kpi_service", "endpoint": "http://localhost:10000/api/v1/kpis"}
    ]
    
    results = {}
    
    for service in services_to_profile:
        try:
            # First check if the service is accessible
            requests.get(service["endpoint"], timeout=2)
            
            # Run the profile
            print(f"\nProfiling {service['name']}...")
            profile_result = profile_service(
                service["name"], 
                service["endpoint"],
                duration=30,  # 30 seconds by default
                workers=4,
                requests_per_second=20
            )
            
            if profile_result:
                results[service["name"]] = profile_result
                
                # Generate optimization suggestions
                suggestions = generate_optimizations(profile_result)
                print("\nOptimization suggestions:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"{i}. {suggestion}")
                
                print("\n" + "-"*50)
                
        except requests.RequestException:
            print(f"Service {service['name']} is not accessible. Skipping.")
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Performance testing and optimization tool")
    parser.add_argument("--service", type=str, help="Specific service to profile")
    parser.add_argument("--endpoint", type=str, help="Endpoint URL to profile")
    parser.add_argument("--duration", type=int, default=30, help="Duration of the profile in seconds")
    parser.add_argument("--workers", type=int, default=4, help="Number of workers to use")
    parser.add_argument("--rps", type=int, default=20, help="Target requests per second")
    parser.add_argument("--profile-all", action="store_true", help="Profile all common services")
    
    args = parser.parse_args()
    
    # Create directories
    os.makedirs("./performance/profiles", exist_ok=True)
    
    if args.profile_all:
        profile_common_services()
    elif args.service and args.endpoint:
        profile_result = profile_service(
            args.service, 
            args.endpoint,
            duration=args.duration,
            workers=args.workers,
            requests_per_second=args.rps
        )
        
        if profile_result:
            suggestions = generate_optimizations(profile_result)
            print("\nOptimization suggestions:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"{i}. {suggestion}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
