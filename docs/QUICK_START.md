# AgriWeather IoT Platform - Quick Start Guide

## ✅ What Works

### 1. Azure Infrastructure
- ✅ IoT Hub: `agriweather-hub-4323`
- ✅ Storage Account: `agriweather9207`
- ✅ Blob Container: `weather-data`
- ✅ VM for API: `20.19.181.153`
- ✅ Device: `agriweather-device-001`

### 2. Device Simulator
- ✅ Sends data every 15 seconds
- ✅ All sensors: temperature, humidity, rainfall, soil moisture, wind speed
- ✅ Data saved to Blob Storage

### 3. REST API (Flask)
All endpoints tested and working:
- ✅ `GET /api/health` - health check
- ✅ `GET /api/devices` - list devices
- ✅ `POST /api/devices` - register device
- ✅ `GET /api/devices/{id}` - device information
- ✅ `GET /api/devices/{id}/current` - current readings
- ✅ `GET /api/devices/{id}/history` - historical data
- ✅ `GET /api/analytics/aggregated` - aggregated statistics
- ✅ `GET /api/analytics/irrigation` - irrigation recommendations
- ✅ `GET /api/devices/{id}/status` - device status

### 4. CLI Application
All commands working:
- ✅ `python src/cli.py health` - API health check
- ✅ `python src/cli.py devices list` - list devices
- ✅ `python src/cli.py devices register` - register device
- ✅ `python src/cli.py data current` - current data
- ✅ `python src/cli.py data history` - historical data
- ✅ `python src/cli.py analytics aggregated` - statistics
- ✅ `python src/cli.py analytics irrigation` - recommendations
- ✅ `python src/cli.py status` - device status

### 5. Web UI
- ✅ Web interface available at `http://localhost:5000`
- ✅ Device display
- ✅ Current sensor readings
- ✅ Irrigation recommendations
- ✅ Historical data
- ✅ Auto-refresh every 30 seconds

## 🚀 How to Run

### 1. Start API Server:
```powershell
cd C:\Users\mikal\CDV\IOT\project\it_IoT_final_project
$env:STORAGE_ACCOUNT_NAME="agriweather9207"
$env:STORAGE_ACCOUNT_KEY="your-storage-key"
$env:CONTAINER_NAME="weather-data"
python src/api_server.py
```

### 2. Start Device Simulator (in another terminal):
```powershell
$env:IOT_HUB_CONNECTION_STRING="HostName=agriweather-hub-4323.azure-devices.net;DeviceId=agriweather-device-001;SharedAccessKey=your-key"
python src/device_simulator.py
```

### 3. Open Web Interface:
Open browser: `http://localhost:5000`

### 4. Use CLI:
```bash
# Check status
python src/cli.py health

# List devices
python src/cli.py devices list

# Current data
python src/cli.py data current --device-id agriweather-device-001

# Historical data
python src/cli.py data history --device-id agriweather-device-001 --limit 10

# Irrigation recommendations
python src/cli.py analytics irrigation --device-id agriweather-device-001
```

## 📊 Test Data

Test data is already uploaded to Blob Storage (100 readings for the last 48 hours).

To upload new test data:
```powershell
$env:STORAGE_ACCOUNT_NAME="agriweather9207"
$env:STORAGE_ACCOUNT_KEY="your-storage-key"
$env:CONTAINER_NAME="weather-data"
python tests/upload_test_data.py
```

## 🧪 Testing

Run all tests:
```bash
python tests/test_all_functions.py
python tests/test_complete_system.py
```

## 📁 Project Structure

```
it_IoT_final_project/
├── src/                    # Main application code
│   ├── device_simulator.py # Device simulator
│   ├── api_server.py       # REST API server
│   └── cli.py              # CLI application
├── tests/                   # Test scripts
│   ├── upload_test_data.py  # Test data upload
│   ├── test_all_functions.py # API tests
│   └── test_complete_system.py
├── scripts/                 # Infrastructure scripts
│   ├── setup_azure_infrastructure.ps1  # Create Azure resources
│   └── deploy_api_to_vm.sh  # Deploy to VM
├── templates/              # HTML templates
├── static/                 # Static assets
└── docs/                   # Documentation
```

## 🎯 Next Steps

1. Deploy API to Azure VM (see `docs/README_SETUP.md`)
2. Set up automatic deployment
3. Add authentication
4. Extend analytics
5. Add charts and visualization

## 📝 Notes

- API server runs on `http://localhost:5000`
- Device simulator sends data to Azure IoT Hub
- Data is stored in Azure Blob Storage
- Web interface auto-refreshes every 30 seconds
- All functions tested and working
