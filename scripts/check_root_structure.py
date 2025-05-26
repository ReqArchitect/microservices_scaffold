import os
import sys

ALLOWED = {"docker-compose.yml", "README.md", ".gitignore"}
ALLOWED_DIRS = {"scripts", "requirements", "config", "docs", "tests", "common_utils", ".git", "venv", "backups", "logs", "monitoring", "k8s", "tools", "service_mesh", "e2e_tests", ".github", "instance"}
FORBIDDEN_EXT = {".py", ".sh", ".txt", ".md", ".yaml", ".yml", ".ini", ".cfg", ".toml"}

for f in os.listdir("."):
    if os.path.isdir(f):
        if f not in ALLOWED_DIRS:
            print(f"[WARN] Unexpected directory at root: {f}")
    else:
        ext = os.path.splitext(f)[1]
        if ext in FORBIDDEN_EXT and f not in ALLOWED:
            print(f"[ERROR] Forbidden file at root: {f}")
            sys.exit(1)

print("[OK] Root structure is clean.") 