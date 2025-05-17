# Function to print status messages
function Write-Status {
    param([string]$Message)
    Write-Host "==> $Message" -ForegroundColor Green
}

# Function to print error messages
function Write-Error {
    param([string]$Message)
    Write-Host "Error: $Message" -ForegroundColor Red
}

# Function to print warning messages
function Write-Warning {
    param([string]$Message)
    Write-Host "Warning: $Message" -ForegroundColor Yellow
}

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed. Please install Python and try again."
    exit 1
}

# Check if pip is installed
if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
    Write-Error "pip is not installed. Please install pip and try again."
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Status "Creating virtual environment..."
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment."
        exit 1
    }
}

# Activate virtual environment
Write-Status "Activating virtual environment..."
.\venv\Scripts\Activate.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to activate virtual environment."
    exit 1
}

# Upgrade pip
Write-Status "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
Write-Status "Installing dependencies..."
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install dependencies."
    exit 1
}

# Create necessary directories
Write-Status "Creating necessary directories..."
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "instance" | Out-Null

# Run Flask setup_dev command
Write-Status "Setting up development environment..."
flask setup_dev
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to setup development environment."
    exit 1
}

# Create initial admin user if requested
$createAdmin = Read-Host "Do you want to create an initial admin user? (y/n)"
if ($createAdmin -eq "y" -or $createAdmin -eq "Y") {
    Write-Status "Creating initial admin user..."
    flask create_admin
}

Write-Status "Development environment setup complete!"
Write-Status "To activate the virtual environment, run: .\venv\Scripts\Activate.ps1"
Write-Status "To run the application, run: flask run --debug"
Write-Status "To run tests, run: flask test" 