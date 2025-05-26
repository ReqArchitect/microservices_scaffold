<<<<<<< HEAD
[![CI](https://github.com/<your-org>/<your-repo>/actions/workflows/ci.yml/badge.svg)](https://github.com/<your-org>/<your-repo>/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/<your-org>/<your-repo>/branch/main/graph/badge.svg)](https://codecov.io/gh/<your-org>/<your-repo>)

=======
>>>>>>> c79de3895fdb976591eac782eb2c8461b8bbbfa3
# Flask Microservices Scaffold

## 🚀 Automated Local Setup Script

This project includes a powerful automation script, `setup_local_env.py`, to make local development and testing of all microservices fast and reliable.

### What does it do?
- **Scans for all microservice directories** (ending with `_service`).
- **Creates a PostgreSQL database** for each service (if it doesn't exist).
- **Installs dependencies** from each service's `requirements.txt`.
- **Warns if `.env` files are missing** in any service.
- **Starts each service** in a new PowerShell window, on its correct port (auto-detected from the code).
- **Prints a summary** of all actions.

### Prerequisites
- Python 3.8+
- [psycopg](https://pypi.org/project/psycopg/) (`pip install psycopg`)
- Local PostgreSQL running and accessible (default user: `postgres`)
- Windows (PowerShell; for Mac/Linux, see script for adaptation)

### Usage
1. **Install dependencies:**
   ```sh
   pip install psycopg
   ```
2. **Run the script:**
   ```sh
   python setup_local_env.py
   ```
   - Enter your local Postgres password when prompted.
3. **Watch your services start** in new PowerShell windows!

### Notes
- The script auto-detects ports from your service entrypoints. If a port is not specified, it defaults to 5000.
- No need to edit the script when adding new services—just follow the `_service` directory naming convention and specify the port in your entrypoint if needed.

---

## 📦 Install All Service Requirements

The `install_all_requirements.py` script will automatically install all Python dependencies for every microservice in your project.

### What does it do?
- **Scans for all `_service` directories** in your project.
- **Installs each service's `requirements.txt`** using your virtual environment.
- **Prints a summary** of what was installed and any missing requirements files.

### Usage
1. **Run the script:**
   ```sh
   python install_all_requirements.py
   ```
2. **Wait for all dependencies to be installed.**

### When to run it?
- After cloning the repo for the first time.
- Whenever a `requirements.txt` file changes in any service.
- Before running or developing any service to ensure all dependencies are present.

---

## 🖥️ Selective Service Runner Script

The `run_service.py` script allows you to interactively choose which microservices to start on your local machine.

### What does it do?
- **Lists all detected `_service` directories** in your project.
- **Prompts you to select** (by number or 'all') which services to start.
- **Finds the entrypoint and port** for each selected service.
- **Starts each service** in a new PowerShell window on its correct port.
- **Prints a summary** of what was started.

### Usage
1. **Run the script:**
   ```sh
   python run_service.py
   ```
2. **Follow the prompt** to select one, many, or all services to start.
3. **Check the new PowerShell windows** for service logs.

### Pros
- Start only the services you need for your current task.
- Reduces resource usage compared to running all services at once.
- No need to remember entrypoints or ports—it's all automated.

### Cons
- Windows/PowerShell only (for now).
- Does not handle database creation or requirements installation (use `setup_local_env.py` for full setup).

---

# Project Overview

(Continue with your existing project documentation below...) 