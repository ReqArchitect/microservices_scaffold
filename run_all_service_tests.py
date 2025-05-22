import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def find_services():
    return [d for d in os.listdir(ROOT) if d.endswith('_service') and os.path.isdir(d)]

def run_pytest(service_dir):
    venv_pytest = os.path.join(ROOT, service_dir, 'venv', 'Scripts', 'pytest.exe')
    tests_dir = os.path.join(ROOT, service_dir, 'tests')
    if not os.path.exists(venv_pytest):
        print(f"❌ No pytest found for {service_dir}, skipping.")
        return False
    if not os.path.exists(tests_dir):
        print(f"⚠️  No tests/ directory in {service_dir}, skipping.")
        return False
    print(f"\n▶️ Running tests for {service_dir}...")
    result = subprocess.run([venv_pytest, tests_dir, '--maxfail=1', '--disable-warnings', '-q'])
    if result.returncode == 0:
        print(f"✅ {service_dir} tests PASSED.")
        return True
    else:
        print(f"❌ {service_dir} tests FAILED.")
        return False

def main():
    services = find_services()
    print(f"🔍 Found services: {services}")
    passed = 0
    failed = 0
    for service in services:
        ok = run_pytest(service)
        if ok:
            passed += 1
        else:
            failed += 1
    print(f"\n=== Test Summary ===")
    print(f"Passed: {passed}")
    print(f"Failed/Skipped: {failed}")
    if failed == 0:
        print("\n🎉 All service tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some service tests failed or were skipped.")
        sys.exit(1)

if __name__ == "__main__":
    main() 