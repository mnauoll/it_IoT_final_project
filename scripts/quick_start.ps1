# AgriWeather Quick Start Script
# This script helps you get started quickly
# Run from project root: .\scripts\quick_start.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AgriWeather IoT Platform - Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8 or higher from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}
Write-Host "Python found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "Dependencies installed" -ForegroundColor Green
Write-Host ""

# Configuration is done via environment variables
Write-Host "Configuration via environment variables is recommended." -ForegroundColor Cyan
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Set up Azure infrastructure:" -ForegroundColor White
Write-Host "   .\scripts\setup_azure_infrastructure.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Configure environment variables:" -ForegroundColor White
Write-Host "   `$env:IOT_HUB_CONNECTION_STRING='your-connection-string'" -ForegroundColor Cyan
Write-Host "   `$env:STORAGE_ACCOUNT_NAME='your-storage-account'" -ForegroundColor Cyan
Write-Host "   `$env:STORAGE_ACCOUNT_KEY='your-storage-key'" -ForegroundColor Cyan
Write-Host "   `$env:CONTAINER_NAME='weather-data'" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Run device simulator:" -ForegroundColor White
Write-Host "   python src\device_simulator.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Start API server:" -ForegroundColor White
Write-Host "   python src\api_server.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Use CLI:" -ForegroundColor White
Write-Host "   python src\cli.py health" -ForegroundColor Cyan
Write-Host "   python src\cli.py devices list" -ForegroundColor Cyan
Write-Host ""
Write-Host "6. Access Web UI:" -ForegroundColor White
Write-Host "   http://localhost:5000/ (Farmer View)" -ForegroundColor Cyan
Write-Host "   http://localhost:5000/dashboard (Dashboard)" -ForegroundColor Cyan
Write-Host ""
