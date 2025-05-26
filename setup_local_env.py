import os
import re
import subprocess
import sys
import psycopg
from psycopg.errors import DuplicateDatabase
from getpass import getpass

# --- CONFIGURATION ---
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
ENTRYPOINTS = ["main.py", "run.py", "manage.py", "wsgi.py"]

# --- UTILS ---
def find_services():
    return [d for d in os.listdir('.') if d.endswith('_service') and os.path.isdir(d)]

def find_entrypoint(service_dir):
    for entry in ENTRYPOINTS:
        path = os.path.join(service_dir, entry)
        if os.path.exists(path):
            return entry
    return None

def parse_port(entrypoint_path):
    try:
        with open(entrypoint_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Look for app.run(..., port=XXXX)
        match = re.search(r'app\.run\([^)]*port\s*=\s*(\d+)', content)
        if match:
            return int(match.group(1))
        # Look for click.option("--port", default=XXXX)
        match = re.search(r'--port".*,\s*default=(\d+)', content)
        if match:
            return int(match.group(1))
    except Exception:
        pass
    return 5000  # Flask default

def create_database(db_name, password):
    conn = psycopg.connect(
        f"host={POSTGRES_HOST} user={POSTGRES_USER} password={password} dbname=postgres",
        autocommit=True
    )
    cur = conn.cursor()
    try:
        cur.execute(f"CREATE DATABASE {db_name};")
        print(f"✅ Database '{db_name}' created.")
    except DuplicateDatabase:
        print(f"ℹ️ Database '{db_name}' already exists.")
    finally:
        cur.close()
        conn.close()

def install_requirements(service_dir):
    req_path = os.path.join(service_dir, 'requirements.txt')
    if os.path.exists(req_path):
        print(f"📦 Installing requirements for {service_dir}...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', req_path])
    else:
        print(f"⚠️ No requirements.txt found in {service_dir}")

def check_env(service_dir):
    env_path = os.path.join(service_dir, '.env')
    if not os.path.exists(env_path):
        print(f"⚠️  WARNING: No .env file found in {service_dir}")

def start_service(service_dir, entrypoint, port):
    print(f"🚀 Starting {service_dir} using {entrypoint} on port {port}...")
    # Open a new PowerShell window for each service
    # If entrypoint is manage.py, use 'python manage.py run --port PORT'
    if entrypoint == 'manage.py':
        cmd = f"cd {os.path.abspath(service_dir)}; {sys.executable} manage.py run --port {port}"
    else:
        cmd = f"cd {os.path.abspath(service_dir)}; {sys.executable} {entrypoint}"
    subprocess.Popen([
        "start", "powershell",
        "-NoExit",
        cmd
    ], shell=True)

def main():
    global POSTGRES_PASSWORD
    if not POSTGRES_PASSWORD:
        POSTGRES_PASSWORD = getpass("Enter your local Postgres password: ")
    services = find_services()
    print(f"🔍 Found services: {services}")
    summary = []
    for service in services:
        db_name = service
        create_database(db_name, POSTGRES_PASSWORD)
        install_requirements(service)
        check_env(service)
        entrypoint = find_entrypoint(service)
        if entrypoint:
            entrypoint_path = os.path.join(service, entrypoint)
            port = parse_port(entrypoint_path)
            start_service(service, entrypoint, port)
            summary.append(f"{service}: {entrypoint} (port {port})")
        else:
            print(f"❌ No known entrypoint found in {service}")
            summary.append(f"{service}: No entrypoint found")
    print("\n✅ All done! Summary:")
    for line in summary:
        print("  -", line)
    print("\nCheck the new PowerShell windows for service logs.")

if __name__ == "__main__":
    main() 