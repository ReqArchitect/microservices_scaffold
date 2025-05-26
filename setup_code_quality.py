#!/usr/bin/env python3
"""Script to set up code quality tools across all microservices."""

import os
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and handle errors."""
    try:
        # Use python -m pip for Windows compatibility
        if cmd.startswith('pip '):
            cmd = f'python -m {cmd}'
        print(f"Running: {cmd}")
        subprocess.run(cmd, shell=True, check=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{cmd}': {e}")
        raise

def setup_service_quality_tools(service_dir):
    """Set up code quality tools for a specific service."""
    if not os.path.exists(service_dir / "requirements.txt"):
        return

    print(f"\nSetting up code quality tools for {service_dir.name}...")
    
    # Add dev dependencies to requirements-dev.txt
    dev_requirements = [
        "black==23.11.0",
        "flake8==6.1.0",
        "mypy==1.6.1",
        "pytest==7.4.3",
        "pytest-cov==4.1.0",
        "isort==5.12.0",
        "pylint==3.0.2",
    ]
    
    with open(service_dir / "requirements-dev.txt", "w") as f:
        f.write("\n".join(dev_requirements))

    # Create symlinks to root config files
    config_files = [".pre-commit-config.yaml", "setup.cfg", "pyproject.toml"]
    for config in config_files:
        src = Path("..") / config
        dst = service_dir / config
        if not dst.exists():
            print(f"Creating symlink for {config}")
            if os.name == "nt":  # Windows
                run_command(f"mklink {dst} {src}", cwd=str(service_dir))
            else:  # Unix
                os.symlink(src, dst)

def main():
    """Main function to set up code quality tools."""
    # Install pre-commit hooks in root
    run_command("pip install pre-commit")
    run_command("pre-commit install")
    
    # Get all service directories
    workspace_root = Path(__file__).parent
    services = [
        d for d in workspace_root.iterdir() 
        if d.is_dir() and d.name.endswith("_service")
    ]
    
    # Set up each service
    for service_dir in services:
        setup_service_quality_tools(service_dir)
    
    print("\nCode quality tools setup complete!")
    print("Run 'pre-commit run --all-files' to check all files")

if __name__ == "__main__":
    main()
