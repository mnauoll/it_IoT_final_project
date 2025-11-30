# AgriWeather IoT Platform - Setup Guide

This guide will help you set up the complete AgriWeather IoT platform on Azure.

## Prerequisites

- Azure account (student account works)
- Azure CLI installed and configured
- Python 3.8 or higher
- PowerShell (for Windows) or Bash (for Linux/macOS)

## Step 1: Set Up Azure Infrastructure

Run the PowerShell script to create all Azure resources:

```powershell
.\scripts\setup_azure_infrastructure.ps1
```

This script will create:
- Resource Group
- IoT Hub
- Storage Account with Blob Container
- Virtual Machine for REST API
- IoT Device Identity

**Important**: Save the connection strings and keys displayed at the end!

## Step 2: Configure Device Simulator

1. Set environment variable with device connection string:

```powershell
# Windows PowerShell
$env:IOT_HUB_CONNECTION_STRING="HostName=...;DeviceId=...;SharedAccessKey=..."
```

Configuration is done via environment variables (recommended).

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Run the device simulator:

```bash
python src/device_simulator.py
```

The simulator will start sending weather data every 15 seconds (configurable via `SEND_INTERVAL` environment variable).

## Step 3: Deploy REST API to VM

1. Get the VM public IP from the setup script output or Azure Portal.

2. Copy files to VM using SCP:

```bash
scp -r src/*.py requirements.txt azureuser@<VM_IP>:/home/azureuser/agriweather-api/
```

Or use Git to clone the repository on the VM.

3. SSH into the VM:

```bash
ssh azureuser@<VM_IP>
```

4. Run the deployment script:

```bash
cd /home/azureuser/agriweather-api
chmod +x deploy_api_to_vm.sh
./deploy_api_to_vm.sh
```

5. Edit the systemd service file with your credentials:

```bash
sudo nano /etc/systemd/system/agriweather-api.service
```

Set the environment variables:
- `STORAGE_ACCOUNT_NAME`
- `STORAGE_ACCOUNT_KEY`
- `IOT_HUB_CONNECTION_STRING`

6. Start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable agriweather-api
sudo systemctl start agriweather-api
```

7. Check service status:

```bash
sudo systemctl status agriweather-api
```

8. View logs:

```bash
sudo journalctl -u agriweather-api -f
```

## Step 4: Configure CLI

1. Set environment variable for API URL:

```powershell
# Windows PowerShell
$env:AGRIWEATHER_API_URL="http://<VM_IP>:5000"
```

Or pass the URL directly:

```bash
python src/cli.py --api-url http://<VM_IP>:5000 health
```

2. Test the CLI:

```bash
python src/cli.py health
python src/cli.py devices list
```

## Step 5: Verify Everything Works

1. **Check device simulator** is sending data:
   - Look for "Data sent" messages in the console
   - Check Azure Portal -> IoT Hub -> Device to device messages

2. **Check data in Blob Storage**:
   - Azure Portal -> Storage Account -> Containers -> weather-data
   - You should see JSON files with device data

3. **Test REST API**:
   ```bash
   python src/cli.py health
   python src/cli.py data current --device-id agriweather-device-001
   ```

4. **Test CLI commands**:
   ```bash
   # List devices
   python src/cli.py devices list
   
   # Get current weather
   python src/cli.py data current --device-id agriweather-device-001
   
   # Get historical data
   python src/cli.py data history --device-id agriweather-device-001 --limit 5
   
   # Get irrigation recommendation
   python src/cli.py analytics irrigation --device-id agriweather-device-001
   ```

## Troubleshooting

### Device Simulator Issues

- **Connection Error**: Check the connection string is correct
- **No data sent**: Verify IoT Hub is running and device is registered
- **Permission Error**: Make sure the device has send permissions in IoT Hub

### API Server Issues

- **Can't connect to storage**: Verify storage account name and key
- **Can't connect to IoT Hub**: Check IoT Hub connection string
- **Port not accessible**: Verify NSG rule allows port 5000

### CLI Issues

- **Connection refused**: Check API server is running and URL is correct
- **404 errors**: Verify device ID exists

## Architecture Overview

The AgriWeather platform follows a cloud-based IoT architecture pattern. The system architecture is documented using C4 model diagrams:

### System Context Diagram
Shows the high-level view of the AgriWeather system and its interactions with external systems and users.

![System Context Diagram](../source/images/system-context-diagram.png)

### Container Diagram
Illustrates the internal structure of the AgriWeather platform, showing the main containers (applications, data stores) and their relationships.

![Container Diagram](../source/images/conteiner-diagram.png)

### Data Flow
```
Device Simulator → Azure IoT Hub → Blob Storage
                                      ↓
                              REST API (VM) ← CLI Application
```

## Next Steps

- Configure IoT Hub message routing (if not done automatically)
- Set up monitoring and alerts
- Add more devices
- Customize sensor ranges for your use case

## Support

For issues or questions, refer to the main README.md or BUSINESS_CONTEXT.md files.

