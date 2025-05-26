import subprocess

print("Running chaos/fault injection tests...")
subprocess.run(["pytest", "--chaos"]) 