# AgriWeather IoT Platform

## Overview

AgriWeather is an IoT-based weather monitoring platform designed for agricultural applications. The platform enables farmers and agricultural professionals to make data-driven decisions about crop planning, irrigation scheduling, and farm management through real-time weather data collection and analysis.

## Project Structure

```
it_IoT_final_project/
├── src/                    # Main application code
│   ├── api_server.py      # Flask REST API server
│   ├── cli.py             # Command-line interface
│   └── device_simulator.py # IoT device simulator
├── tests/                  # Test scripts
│   ├── test_all_functions.py
│   ├── test_complete_system.py
│   └── upload_test_data.py
├── scripts/                # Infrastructure scripts
│   ├── setup_azure_infrastructure.ps1
│   ├── teardown_azure_infrastructure.ps1
│   ├── quick_start.ps1
│   └── deploy_api_to_vm.sh
├── templates/              # HTML templates
│   ├── farmer.html
│   └── dashboard.html
├── static/                 # Static assets (CSS, JS)
│   ├── farmer.css
│   ├── farmer.js
│   ├── dashboard.css
│   └── dashboard.js
├── docs/                   # Documentation
│   ├── BUSINESS_CONTEXT.md
│   ├── README_SETUP.md
│   ├── QUICK_START.md
│   └── UI_README.md
├── source/                 # Architecture diagrams
│   └── images/
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Architecture

### System Components

- **IoT Device Simulator**: Simulates weather sensors collecting environmental data (temperature, humidity, rainfall, soil moisture, wind speed)
- **Azure IoT Hub**: Device connectivity and message routing
- **Azure Blob Storage**: Data persistence
- **REST API Backend**: Flask-based API with business logic and analytics
- **Web Interface**: Two views - Farmer View and System Dashboard
- **CLI Tool**: Command-line interface for platform management

### C4 Model Diagrams

The project includes C4 model architecture diagrams that visualize the system structure:

#### System Context Diagram
This diagram shows the high-level view of the AgriWeather system and its interactions with external systems and users.

![System Context Diagram](source/images/system-context-diagram.png)

#### Container Diagram
This diagram illustrates the internal structure of the AgriWeather platform, showing the main containers (applications, data stores) and their relationships.

![Container Diagram](source/images/conteiner-diagram.png)

> **Note**: If the diagrams don't display correctly, ensure the image files are present in the `source/images/` directory.

## Quick Start

### Prerequisites

- Azure account (student account works)
- Azure CLI installed and configured
- Python 3.8 or higher
- PowerShell (for Windows) or Bash (for Linux/macOS)

### 1. Setup Azure Infrastructure

Run the PowerShell script to create all Azure resources:

```powershell
.\scripts\setup_azure_infrastructure.ps1
```

This script creates:
- Resource Group
- IoT Hub (F1 SKU - Free tier)
- Storage Account with Blob Container
- Virtual Machine for REST API
- IoT Device Identity
- Network Security Group rules
- Message routing from IoT Hub to Blob Storage

**Important**: Save the connection strings and keys displayed at the end!

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Set the required environment variables:

```powershell
# Windows PowerShell
$env:IOT_HUB_CONNECTION_STRING="HostName=...;DeviceId=...;SharedAccessKey=..."
$env:STORAGE_ACCOUNT_NAME="your-storage-account"
$env:STORAGE_ACCOUNT_KEY="your-storage-key"
$env:CONTAINER_NAME="weather-data"
$env:POLLING_INTERVAL="30"  # Optional: polling interval in seconds (default: 30)
```

### 4. Run Device Simulator

```powershell
# Windows PowerShell
$env:IOT_HUB_CONNECTION_STRING="HostName=...;DeviceId=...;SharedAccessKey=..."
$env:STORAGE_ACCOUNT_NAME="your-storage-account"
$env:STORAGE_ACCOUNT_KEY="your-storage-key"
$env:CONTAINER_NAME="weather-data"
$env:SEND_INTERVAL="30"  # Send data every 30 seconds
python src/device_simulator.py
```

The simulator:
- Sends weather data to Azure IoT Hub
- **Directly uploads data to Blob Storage every 30 seconds** (simulates real-time sensor operation)
- Generates realistic data with daily cycles and variations
- Data changes every 30 seconds for real-time testing

### 5. Start REST API Server

```powershell
# Windows PowerShell
python src/api_server.py
```

The API server will:
- Start on `http://localhost:5000`
- Begin polling sensor data every 30 seconds (configurable via `POLLING_INTERVAL` env var)
- Check conditions and generate alerts automatically

### 6. Access Web Interface

Open your browser:
- **Farmer View**: `http://localhost:5000/`
- **System Dashboard**: `http://localhost:5000/dashboard`

## Using the CLI

The CLI tool provides a professional interface for managing devices and querying data.

### Basic Commands

```bash
# Check API health
python src/cli.py health

# List all devices
python src/cli.py devices list

# Register a new device
python src/cli.py devices register --device-id device001 --name "Field A" --lat 50.0 --lon 20.0

# Get current weather data
python src/cli.py data current --device-id device001

# Get historical data
python src/cli.py data history --device-id device001 --limit 20

# Get aggregated analytics
python src/cli.py analytics aggregated --device-id device001 --period day

# Get irrigation recommendation
python src/cli.py analytics irrigation --device-id device001 --crop-type wheat

# Get device status
python src/cli.py status --device-id device001
```

### CLI Configuration

The CLI uses environment variables for configuration:

```powershell
$env:AGRIWEATHER_API_URL="http://localhost:5000"
```

Or pass the API URL directly:

```bash
python src/cli.py --api-url http://localhost:5000 health
```

## Testing

### Run All Tests

```bash
# Test all API endpoints
python tests/test_all_functions.py

# Complete system test (includes polling and alerts)
python tests/test_complete_system.py
```

### Upload Test Data

To populate Blob Storage with test data for multiple devices:

```powershell
$env:STORAGE_ACCOUNT_NAME="your-storage-account"
$env:STORAGE_ACCOUNT_KEY="your-storage-key"
$env:CONTAINER_NAME="weather-data"
python tests/upload_test_data.py
```

This generates test data for 5 devices with realistic variations and conditions that trigger alerts.

## Alert System

The platform automatically monitors sensor data and generates alerts for dangerous conditions:

- **Critical Alerts**:
  - Frost warning (temperature < 0°C)
  
- **Warning Alerts**:
  - Low temperature (< 5°C)
  - High temperature (> 35°C)
  - Low soil moisture (< 30%)
  - High wind speed (> 40 km/h)
  
- **Info Alerts**:
  - Low humidity (< 20%)

The server polls data every 30 seconds (configurable) and generates alerts automatically.

### Viewing Alerts

```bash
# Via API
curl http://localhost:5000/api/devices/device001/alerts

# Via CLI (if endpoint added)
python src/cli.py alerts --device-id device001
```

## API Endpoints

### Health Check
- `GET /api/health` - Check API and storage connectivity

### Device Management
- `GET /api/devices` - List all registered devices
- `POST /api/devices` - Register a new device
- `GET /api/devices/<device_id>` - Get device information
- `GET /api/devices/<device_id>/status` - Get device status

### Weather Data
- `GET /api/devices/<device_id>/current` - Get current weather readings
- `GET /api/devices/<device_id>/history` - Get historical data
  - Query parameters: `from`, `to`, `limit`

### Analytics
- `GET /api/analytics/aggregated` - Get aggregated statistics
  - Query parameters: `device_id`, `period` (day/week/month)
- `GET /api/analytics/irrigation` - Get irrigation recommendations
  - Query parameters: `device_id`, `crop_type`

### Alerts
- `GET /api/devices/<device_id>/alerts` - Get alerts for a device
- `GET /api/alerts` - Get all alerts across all devices
  - Query parameters: `limit`

## Teardown

To remove all Azure resources and manage your budget:

```powershell
.\scripts\teardown_azure_infrastructure.ps1
```

This script will:
- List all resources in the resource group
- Ask for confirmation
- Delete the entire resource group (all resources)

## Documentation

Additional documentation is available in the `docs/` directory:

- `BUSINESS_CONTEXT.md` - Business logic and requirements
- `README_SETUP.md` - Detailed setup instructions
- `QUICK_START.md` - Quick start guide
- `UI_README.md` - Web interface documentation

## Technology Stack

- **Backend**: Python 3.8+, Flask
- **Cloud**: Azure IoT Hub, Azure Blob Storage, Azure Virtual Machines
- **Frontend**: HTML, CSS, JavaScript
- **Protocols**: MQTT (via Azure IoT SDK)
- **CLI**: Python argparse

## License

See LICENSE file for details.

## Support

For issues or questions, refer to the documentation in the `docs/` directory.
