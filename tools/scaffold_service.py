#!/usr/bin/env python
"""
Service scaffolding tool for ReqArchitect microservices.
"""
import argparse
import os
import shutil
from pathlib import Path
import jinja2

TEMPLATE_DIR = Path(__file__).parent / "templates"

def create_service(name: str, port: int, description: str):
    """Create a new microservice with standardized structure."""
    service_dir = Path(f"{name}_service")
    
    # Create directory structure
    directories = [
        service_dir,
        service_dir / "app",
        service_dir / "app" / "api",
        service_dir / "app" / "models",
        service_dir / "app" / "services",
        service_dir / "tests",
        service_dir / "config"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    # Load templates
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR))
    )

    # Generate files from templates
    templates = {
        "Dockerfile": service_dir / "Dockerfile",
        "requirements.txt": service_dir / "requirements.txt",
        "config.py": service_dir / "config" / "config.py",
        "app.py": service_dir / "app" / "app.py",
        "base_model.py": service_dir / "app" / "models" / "base_model.py",
        "routes.py": service_dir / "app" / "api" / "routes.py",
        "service.py": service_dir / "app" / "services" / "service.py",
        "test_service.py": service_dir / "tests" / "test_service.py",
        "docker-compose.yml": service_dir / "docker-compose.yml"
    }

    context = {
        "service_name": name,
        "port": port,
        "description": description
    }

    for template_name, output_path in templates.items():
        template = env.get_template(template_name + ".j2")
        content = template.render(**context)
        output_path.write_text(content)

def main():
    parser = argparse.ArgumentParser(description="Create a new ReqArchitect microservice")
    parser.add_argument("name", help="Name of the service")
    parser.add_argument("--port", type=int, required=True, help="Port number for the service")
    parser.add_argument("--description", help="Service description", default="")
    
    args = parser.parse_args()
    create_service(args.name, args.port, args.description)
    print(f"Service {args.name} created successfully!")

if __name__ == "__main__":
    main()
