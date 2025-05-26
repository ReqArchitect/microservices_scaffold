import subprocess

print("Running contract tests with Schemathesis...")
subprocess.run(["schemathesis", "run", "docs/api-spec.yaml", "--base-url=http://localhost:5000"])

print("Running contract tests with Dredd...")
subprocess.run(["dredd", "docs/api-spec.yaml", "http://localhost:5000"]) 