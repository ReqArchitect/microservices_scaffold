import os
import subprocess
import sys

VENV_PYTHON = os.path.join('venv', 'Scripts', 'python.exe')


def find_services():
    return [d for d in os.listdir('.') if d.endswith('_service') and os.path.isdir(d)]

def install_requirements(service_dir):
    req_path = os.path.join(service_dir, 'requirements.txt')
    if os.path.exists(req_path):
        print(f"📦 Installing requirements for {service_dir}...")
        result = subprocess.run([VENV_PYTHON, '-m', 'pip', 'install', '-r', req_path])
        if result.returncode == 0:
            print(f"✅ Installed requirements for {service_dir}")
        else:
            print(f"❌ Failed to install requirements for {service_dir}")
    else:
        print(f"⚠️ No requirements.txt found in {service_dir}")

def main():
    services = find_services()
    print(f"🔍 Found services: {services}")
    for service in services:
        install_requirements(service)
    print("\n✅ All done! If you see any errors above, check the requirements.txt for that service.")

if __name__ == "__main__":
    main() 