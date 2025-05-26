import os
import re
import subprocess
import sys

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
        match = re.search(r'app\.run\([^)]*port\s*=\s*(\d+)', content)
        if match:
            return int(match.group(1))
        match = re.search(r'--port".*,\s*default=(\d+)', content)
        if match:
            return int(match.group(1))
    except Exception:
        pass
    return 5000

def start_service(service_dir, entrypoint, port):
    print(f"🚀 Starting {service_dir} using {entrypoint} on port {port}...")
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
    services = find_services()
    if not services:
        print("No *_service directories found.")
        return
    print("\nDetected services:")
    for idx, svc in enumerate(services, 1):
        print(f"  {idx}. {svc}")
    print("  all. (Start all services)")
    selection = input("\nEnter numbers of services to start (comma-separated, or 'all'): ").strip().lower()
    if selection == 'all':
        selected = services
    else:
        try:
            nums = [int(x) for x in selection.split(',') if x.strip().isdigit()]
            selected = [services[i-1] for i in nums if 1 <= i <= len(services)]
        except Exception:
            print("Invalid selection.")
            return
    summary = []
    for service in selected:
        entrypoint = find_entrypoint(service)
        if entrypoint:
            entrypoint_path = os.path.join(service, entrypoint)
            port = parse_port(entrypoint_path)
            start_service(service, entrypoint, port)
            summary.append(f"{service}: {entrypoint} (port {port})")
        else:
            print(f"❌ No known entrypoint found in {service}")
            summary.append(f"{service}: No entrypoint found")
    print("\n✅ Started services:")
    for line in summary:
        print("  -", line)
    print("\nCheck the new PowerShell windows for service logs.")

if __name__ == "__main__":
    main() 