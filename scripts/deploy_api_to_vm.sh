#!/bin/bash
# Deployment script for REST API to Azure VM
# Run this script on the Azure VM after SSH connection

echo "========================================"
echo "AgriWeather API Deployment"
echo "========================================"
echo ""

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and pip
echo "Installing Python and pip..."
sudo apt-get install -y python3 python3-pip python3-venv

# Install git (if needed)
sudo apt-get install -y git

# Create application directory
APP_DIR="/opt/agriweather-api"
echo "Creating application directory: $APP_DIR"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Copy application files (assuming they're uploaded via SCP or git)
# If using git:
# cd $APP_DIR
# git clone <your-repo-url> .

# Create virtual environment
echo "Creating Python virtual environment..."
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service file
echo "Creating systemd service..."
sudo tee /etc/systemd/system/agriweather-api.service > /dev/null <<EOF
[Unit]
Description=AgriWeather REST API
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
Environment="STORAGE_ACCOUNT_NAME=YOUR_STORAGE_ACCOUNT"
Environment="STORAGE_ACCOUNT_KEY=YOUR_STORAGE_KEY"
Environment="CONTAINER_NAME=weather-data"
Environment="IOT_HUB_CONNECTION_STRING=YOUR_IOT_HUB_CONN_STRING"
Environment="PORT=5000"
Environment="FLASK_DEBUG=False"
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/api_server.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "========================================"
echo "Deployment Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit /etc/systemd/system/agriweather-api.service"
echo "   - Set STORAGE_ACCOUNT_NAME"
echo "   - Set STORAGE_ACCOUNT_KEY"
echo "   - Set IOT_HUB_CONNECTION_STRING"
echo ""
echo "2. Start the service:"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable agriweather-api"
echo "   sudo systemctl start agriweather-api"
echo ""
echo "3. Check service status:"
echo "   sudo systemctl status agriweather-api"
echo ""
echo "4. View logs:"
echo "   sudo journalctl -u agriweather-api -f"
echo ""

