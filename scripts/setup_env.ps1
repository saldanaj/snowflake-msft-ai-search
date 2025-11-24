# Setup script for Snowflake to Azure AI Search Demo
# This script sets up the Python virtual environment and installs dependencies

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Snowflake to Azure AI Search Demo Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Detected Python version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed. Please install Python 3.10 or higher." -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Activate the virtual environment:"
Write-Host "   .\venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "2. Copy and configure environment files:"
Write-Host "   Copy-Item config\.env.example config\.env"
Write-Host "   Copy-Item config\config.yaml.example config\config.yaml"
Write-Host ""
Write-Host "3. Edit config\.env with your credentials"
Write-Host ""
Write-Host "4. (Optional) Deploy Azure infrastructure:"
Write-Host "   .\scripts\deploy_infrastructure.ps1"
Write-Host ""
Write-Host "5. Run the pipeline:"
Write-Host "   python scripts\run_pipeline.py"
Write-Host ""
