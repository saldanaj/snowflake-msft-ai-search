#!/bin/bash

# Setup script for Snowflake to Azure AI Search Demo
# This script sets up the Python virtual environment and installs dependencies

set -e

echo "=========================================="
echo "Snowflake to Azure AI Search Demo Setup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Detected Python version: $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   - Windows: venv\\Scripts\\activate"
echo "   - Linux/Mac: source venv/bin/activate"
echo ""
echo "2. Copy and configure environment files:"
echo "   cp config/.env.example config/.env"
echo "   cp config/config.yaml.example config/config.yaml"
echo ""
echo "3. Edit config/.env with your credentials"
echo ""
echo "4. (Optional) Deploy Azure infrastructure:"
echo "   ./scripts/deploy_infrastructure.sh"
echo ""
echo "5. Run the pipeline:"
echo "   python scripts/run_pipeline.py"
echo ""
