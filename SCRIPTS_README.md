# Enhanced Architecture Implementation Scripts

This directory contains scripts to implement the enhanced microservices architecture across all services in the ReqArchitect system.

## Prerequisites

Before using these scripts, install the required Python packages:

```powershell
pip install pyyaml pathlib
```

## Available Scripts

### 1. Implement Enhanced Architecture

The `implement_enhanced_architecture.py` script automates the implementation of enhanced architecture components in your microservices.

**Features:**
- Adds service registry integration (Consul)
- Sets up distributed tracing (Jaeger)
- Implements API versioning
- Adds the Outbox pattern for data consistency
- Updates configuration files
- Adds metrics collection
- Runs database migrations

**Usage:**
```powershell
# Run a dry-run to see what changes would be made
python implement_enhanced_architecture.py --dry-run

# Implement in all services
python implement_enhanced_architecture.py

# Implement in a specific service
python implement_enhanced_architecture.py --service strategy_service

# Skip creating backups
python implement_enhanced_architecture.py --skip-backup
```

### 2. Update Docker Compose

The `update_docker_compose.py` script updates your docker-compose.yml to include the enhanced architecture components.

**Features:**
- Adds Consul, Jaeger, and Envoy services
- Updates service configurations with necessary environment variables
- Fixes port conflicts
- Adds persistent volumes for databases
- Updates service dependencies

**Usage:**
```powershell
# Create an enhanced docker-compose file
python update_docker_compose.py

# Create a backup of the original file
python update_docker_compose.py --backup

# Specify a different output filename
python update_docker_compose.py --output my-docker-compose.yml
```

## Implementation Steps

1. **Update Docker Compose Configuration**:
   ```powershell
   python update_docker_compose.py --backup
   ```

2. **Implement the Enhanced Architecture**:
   ```powershell
   # Optional: Run a dry-run first
   python implement_enhanced_architecture.py --dry-run
   
   # Apply the changes
   python implement_enhanced_architecture.py
   ```

3. **Start the Infrastructure Services**:
   ```powershell
   docker-compose -f docker-compose-enhanced.yml up -d consul jaeger envoy
   ```

4. **Start Your Services**:
   ```powershell
   docker-compose -f docker-compose-enhanced.yml up --build
   ```

## Verifying the Implementation

1. **Service Registry**:
   - Open Consul UI at http://localhost:8500
   - Verify that your services are registered

2. **Distributed Tracing**:
   - Open Jaeger UI at http://localhost:16686
   - Search for traces from your services

3. **API Gateway**:
   - Access your APIs through Envoy: http://localhost:10000/api/v1/...

4. **API Versioning**:
   - Use versioned endpoints: `/api/v1/capabilities`
   - Verify that unversioned endpoints redirect: `/api/capabilities`

5. **Outbox Processing**:
   - Check service logs for outbox processing messages
   - Verify cross-service events are propagated

## Troubleshooting

If you encounter issues:

1. **Check Logs**:
   ```powershell
   docker-compose -f docker-compose-enhanced.yml logs <service_name>
   ```

2. **Restore from Backup**:
   - Backups are stored in the `backups` directory
   - Copy files back to restore to the original state

3. **Common Issues**:
   - Port conflicts: Check if ports are already in use
   - Database migrations: Run migrations manually if automatic migration fails
   - Environment variables: Ensure all required variables are set

4. **Manual Fixes**:
   - Follow the step-by-step guide in `IMPLEMENTATION_GUIDE.md`
   - Apply changes manually to specific files if needed
