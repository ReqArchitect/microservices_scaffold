#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}==>${NC} $1"
}

# Function to print error messages
print_error() {
    echo -e "${RED}Error:${NC} $1"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}Warning:${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip3 and try again."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment."
        exit 1
    fi
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    print_error "Failed to activate virtual environment."
    exit 1
fi

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    print_error "Failed to install dependencies."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs instance

# Run Flask setup_dev command
print_status "Setting up development environment..."
flask setup_dev
if [ $? -ne 0 ]; then
    print_error "Failed to setup development environment."
    exit 1
fi

# Create initial admin user if requested
read -p "Do you want to create an initial admin user? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Creating initial admin user..."
    flask create_admin
fi

print_status "Development environment setup complete!"
print_status "To activate the virtual environment, run: source venv/bin/activate"
print_status "To run the application, run: flask run --debug"
print_status "To run tests, run: flask test" 