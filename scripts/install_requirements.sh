#!/bin/bash

# Install or update all requirements in the virtual environment
# Run this script to ensure all dependencies are installed

set -e

echo "=========================================="
echo "Installing Requirements"
echo "=========================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "[OK] Virtual environment created"
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing requirements..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Installed packages:"
pip list

echo ""
echo "To activate the virtual environment in the future:"
echo "  source venv/bin/activate"
echo ""
