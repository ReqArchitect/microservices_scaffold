import subprocess
import sys
import os

def run(cmd, fail_msg=None):
    print(f"\n>>> {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"\n❌ {fail_msg or f'Check failed: {cmd}'}")
        sys.exit(result.returncode)

# 1. Linting
run('flake8 .', 'flake8 linting failed')
run('black --check .', 'black formatting failed')

# 2. Static analysis
run('bandit -r .', 'bandit security scan failed')
run('mypy .', 'mypy type checks failed')

# 3. Dependency audit
run('pip-audit', 'pip-audit found vulnerabilities')

# 4. Secrets scan
run('detect-secrets scan --all-files', 'detect-secrets found potential secrets')

# 5. Config/DB check
for config_file in ['auth_service/app/config.py', 'auth_service/config.py']:
    if os.path.exists(config_file):
        with open(config_file) as f:
            if 'sqlite' in f.read().lower():
                print(f'❌ SQLite reference found in {config_file}')
                sys.exit(1)

# 6. Test coverage
run('pytest --cov --cov-report=term-missing', 'pytest or coverage failed')

# 7. Docker & Compose
if os.path.exists('docker-compose.yml'):
    run('docker-compose config', 'docker-compose config invalid')
if os.path.exists('Dockerfile'):
    run('hadolint Dockerfile', 'Dockerfile lint failed')

print('\n✅ All code quality checks passed!') 