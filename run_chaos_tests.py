#!/usr/bin/env python3
"""
Run Chaos Experiments to test service resilience
"""
import argparse
import os
import subprocess
import sys
import time
from datetime import datetime

def setup_environment():
    """Install required dependencies for chaos testing"""
    print("Setting up chaos testing environment...")
    subprocess.run(["pip", "install", "-r", "requirements.txt"], 
                  cwd="./chaos_testing", check=True)

def run_experiment(experiment_file, namespace="reqarchitect"):
    """Run a specific chaos experiment"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"chaos_report_{timestamp}.json"
    
    print(f"Running chaos experiment: {experiment_file}")
    print(f"Results will be saved to: {report_file}")
    
    cmd = [
        "chaos", "run", 
        "--var", f"k8s_namespace={namespace}",
        experiment_file,
        "--journal-path", f"./chaos_testing/reports/{report_file}"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"Experiment completed with exit code: {result.returncode}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Experiment failed with exit code: {e.returncode}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run chaos experiments for microservices")
    parser.add_argument("--setup", action="store_true", help="Setup the chaos testing environment")
    parser.add_argument("--experiment", type=str, default="service_resilience_experiment.json", 
                        help="The experiment file to run")
    parser.add_argument("--namespace", type=str, default="reqarchitect",
                        help="Kubernetes namespace for the experiments")
    
    args = parser.parse_args()
    
    # Create reports directory if it doesn't exist
    os.makedirs("./chaos_testing/reports", exist_ok=True)
    
    if args.setup:
        setup_environment()
    
    # Path to the experiment file
    experiment_path = os.path.join("./chaos_testing", args.experiment)
    
    # Run the experiment
    success = run_experiment(experiment_path, args.namespace)
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
