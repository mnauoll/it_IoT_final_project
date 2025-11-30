"""
AgriWeather REST API Server
Flask-based REST API for weather data access and device management.
"""

import os
import json
import threading
import time
from datetime import datetime, timedelta, timezone
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from azure.storage.blob import BlobServiceClient

# Optional IoT Hub import (may not be available if uamqp failed to install)
try:
    from azure.iot.hub import IoTHubRegistryManager
    from azure.iot.hub.models import CloudToDeviceMethod
    IOT_HUB_AVAILABLE = True
except ImportError:
    IOT_HUB_AVAILABLE = False
    print("Warning: azure-iot-hub not available. Some features may be limited.")

# Get project root directory (parent of src/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, 
            static_folder=os.path.join(project_root, 'static'), 
            template_folder=os.path.join(project_root, 'templates'))
CORS(app)

# Configuration from environment variables
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME", "")
STORAGE_ACCOUNT_KEY = os.getenv("STORAGE_ACCOUNT_KEY", "")
CONTAINER_NAME = os.getenv("CONTAINER_NAME", "weather-data")
IOT_HUB_CONNECTION_STRING = os.getenv("IOT_HUB_CONNECTION_STRING", "")

# Initialize Azure clients
blob_service_client = None
iot_hub_manager = None

if STORAGE_ACCOUNT_NAME and STORAGE_ACCOUNT_KEY:
    try:
        connection_string = f"DefaultEndpointsProtocol=https;AccountName={STORAGE_ACCOUNT_NAME};AccountKey={STORAGE_ACCOUNT_KEY};EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        print("Connected to Azure Blob Storage")
    except Exception as e:
        print(f"Warning: Could not connect to Blob Storage: {e}")

if IOT_HUB_CONNECTION_STRING and IOT_HUB_AVAILABLE:
    try:
        iot_hub_manager = IoTHubRegistryManager(IOT_HUB_CONNECTION_STRING)
        print("Connected to Azure IoT Hub")
    except Exception as e:
        print(f"Warning: Could not connect to IoT Hub: {e}")
elif IOT_HUB_CONNECTION_STRING and not IOT_HUB_AVAILABLE:
    print("Warning: IoT Hub connection string provided but azure-iot-hub not installed")


# Device registry
devices_registry = {
    "agriweather-device-001": {
        "device_id": "agriweather-device-001",
        "name": "Field A Sensor",
        "location": {"latitude": 50.0, "longitude": 20.0},
        "registered_at": datetime.now(timezone.utc).isoformat(),
        "status": "online"
    }
}

# Latest readings cache
latest_readings = {}

# Alerts/warnings storage
alerts = {}  # device_id -> list of alerts

# Polling configuration - 30 seconds for testing, 300 seconds (5 min) for production
POLLING_INTERVAL = int(os.getenv('POLLING_INTERVAL', 30))
polling_active = False
polling_thread = None


def parse_blob_data(blob_content):
    """Parse JSON data from blob storage."""
    try:
        if isinstance(blob_content, bytes):
            blob_content = blob_content.decode('utf-8')
        lines = blob_content.strip().split('\n')
        data = []
        for line in lines:
            if line.strip():
                data.append(json.loads(line))
        return data
    except Exception as e:
        print(f"Error parsing blob data: {e}")
        return []


def check_conditions_and_generate_alerts(device_id, reading):
    """
    Check weather conditions and generate alerts for dangerous situations.
    
    Args:
        device_id: Device identifier
        reading: Current sensor reading dictionary
    """
    if not reading:
        return
    
    alerts_list = alerts.get(device_id, [])
    new_alerts = []
    timestamp = datetime.now(timezone.utc).isoformat()
    
    temperature = reading.get('temperature', 0)
    soil_moisture = reading.get('soil_moisture', 50)
    wind_speed = reading.get('wind_speed', 0)
    humidity = reading.get('humidity', 50)
    
    # Frost alert (temperature < 0°C)
    if temperature < 0:
        alert = {
            "type": "frost",
            "severity": "critical",
            "message": f"Frost warning! Temperature is {temperature:.1f}°C. Protect your crops immediately.",
            "timestamp": timestamp,
            "value": temperature,
            "threshold": 0
        }
        new_alerts.append(alert)
    
    # Low temperature warning (< 5°C)
    elif temperature < 5:
        alert = {
            "type": "low_temperature",
            "severity": "warning",
            "message": f"Low temperature alert: {temperature:.1f}°C. Monitor for frost risk.",
            "timestamp": timestamp,
            "value": temperature,
            "threshold": 5
        }
        new_alerts.append(alert)
    
    # High temperature warning (> 35°C)
    if temperature > 35:
        alert = {
            "type": "high_temperature",
            "severity": "warning",
            "message": f"High temperature warning: {temperature:.1f}°C. Crops may experience heat stress.",
            "timestamp": timestamp,
            "value": temperature,
            "threshold": 35
        }
        new_alerts.append(alert)
    
    # Low soil moisture (< 30%)
    if soil_moisture < 30:
        alert = {
            "type": "low_soil_moisture",
            "severity": "warning",
            "message": f"Low soil moisture: {soil_moisture:.1f}%. Irrigation recommended.",
            "timestamp": timestamp,
            "value": soil_moisture,
            "threshold": 30
        }
        new_alerts.append(alert)
    
    # High wind speed (> 40 km/h)
    if wind_speed > 40:
        alert = {
            "type": "high_wind",
            "severity": "warning",
            "message": f"High wind warning: {wind_speed:.1f} km/h. Potential crop damage risk.",
            "timestamp": timestamp,
            "value": wind_speed,
            "threshold": 40
        }
        new_alerts.append(alert)
    
    # Very low humidity (< 20%)
    if humidity < 20:
        alert = {
            "type": "low_humidity",
            "severity": "info",
            "message": f"Low humidity: {humidity:.1f}%. Increased water loss risk.",
            "timestamp": timestamp,
            "value": humidity,
            "threshold": 20
        }
        new_alerts.append(alert)
    
    alerts_list.extend(new_alerts)
    alerts[device_id] = alerts_list[-50:]
    
    for alert in new_alerts:
        print(f"[ALERT] {device_id}: {alert['message']}")


def poll_sensor_data():
    """
    Poll sensor data from blob storage and check for alerts.
    Runs in a background thread.
    Gets the most recent data by checking all blobs and finding the latest timestamp.
    """
    global polling_active
    
    polling_active = True
    print(f"Starting sensor data polling (interval: {POLLING_INTERVAL}s)")
    
    while polling_active:
        try:
            if not blob_service_client:
                time.sleep(POLLING_INTERVAL)
                continue
            
            container_client = blob_service_client.get_container_client(CONTAINER_NAME)
            
            for device_id in devices_registry.keys():
                try:
                    blobs = list(container_client.list_blobs(name_starts_with=f"{device_id}/"))
                    if not blobs:
                        continue
                    
                    # Get all readings from all blobs and find the most recent by timestamp
                    all_readings = []
                    for blob in blobs:
                        try:
                            blob_client = blob_service_client.get_blob_client(
                                container=CONTAINER_NAME,
                                blob=blob.name
                            )
                            blob_data = blob_client.download_blob().readall()
                            readings = parse_blob_data(blob_data)
                            all_readings.extend(readings)
                        except Exception as e:
                            continue
                    
                    if all_readings:
                        # Sort by timestamp and get the latest
                        all_readings.sort(key=lambda x: x.get('timestamp', ''))
                        latest = all_readings[-1]
                        
                        # Only update if this is newer than what we have
                        current_timestamp = latest_readings.get(device_id, {}).get('timestamp', '')
                        new_timestamp = latest.get('timestamp', '')
                        
                        if new_timestamp > current_timestamp or not current_timestamp:
                            latest_readings[device_id] = latest
                            check_conditions_and_generate_alerts(device_id, latest)
                            print(f"[POLL] Updated data for {device_id}: Temp={latest.get('temperature', 'N/A')}°C")
                        
                except Exception as e:
                    print(f"Error polling device {device_id}: {e}")
            
            time.sleep(POLLING_INTERVAL)
            
        except Exception as e:
            print(f"Error in polling thread: {e}")
            time.sleep(POLLING_INTERVAL)
    
    print("Polling stopped")


def start_polling():
    """Start the background polling thread."""
    global polling_thread, polling_active
    
    if polling_thread is None or not polling_thread.is_alive():
        polling_active = True
        polling_thread = threading.Thread(target=poll_sensor_data, daemon=True)
        polling_thread.start()
        print("Sensor polling started")


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "storage_connected": blob_service_client is not None,
        "iot_hub_connected": iot_hub_manager is not None
    }), 200


@app.route('/api/devices', methods=['GET'])
def list_devices():
    """List all registered devices."""
    return jsonify({
        "devices": list(devices_registry.values()),
        "count": len(devices_registry)
    }), 200


@app.route('/api/devices', methods=['POST'])
def register_device():
    """Register a new device."""
    data = request.get_json()
    
    if not data or 'device_id' not in data:
        return jsonify({"error": "device_id is required"}), 400
    
    device_id = data['device_id']
    device_info = {
        "device_id": device_id,
        "name": data.get("name", f"Device {device_id}"),
        "location": data.get("location", {"latitude": 50.0, "longitude": 20.0}),
        "registered_at": datetime.now(timezone.utc).isoformat(),
        "status": "online"
    }
    
    devices_registry[device_id] = device_info
    
    return jsonify(device_info), 201


@app.route('/api/devices/<device_id>', methods=['GET'])
def get_device(device_id):
    """Get device information."""
    if device_id not in devices_registry:
        return jsonify({"error": "Device not found"}), 404
    
    device = devices_registry[device_id].copy()
    
    if device_id in latest_readings:
        device["last_reading"] = latest_readings[device_id].get("timestamp")
    
    return jsonify(device), 200


@app.route('/api/devices/<device_id>/current', methods=['GET'])
def get_current_reading(device_id):
    """Get current weather readings for a device."""
    if device_id in latest_readings:
        return jsonify(latest_readings[device_id]), 200
    if not blob_service_client:
        return jsonify({"error": "Storage not configured"}), 503
    
    try:
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        
        # List blobs for this device, get the most recent
        blobs = list(container_client.list_blobs(name_starts_with=f"{device_id}/"))
        if not blobs:
            return jsonify({"error": "No data found for device"}), 404
        
        latest_blob = max(blobs, key=lambda b: b.last_modified)
        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_NAME,
            blob=latest_blob.name
        )
        
        blob_data = blob_client.download_blob().readall()
        readings = parse_blob_data(blob_data)
        
        if readings:
            latest = readings[-1]
            latest_readings[device_id] = latest
            return jsonify(latest), 200
        
        return jsonify({"error": "No readings found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/devices/<device_id>/history', methods=['GET'])
def get_history(device_id):
    """Get historical weather data for a device."""
    if not blob_service_client:
        return jsonify({"error": "Storage not configured"}), 503
    
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    limit = int(request.args.get('limit', 100))
    
    try:
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        
        prefix = f"{device_id}/"
        if from_date:
            prefix += from_date[:10].replace('-', '/') + "/"
        
        blobs = list(container_client.list_blobs(name_starts_with=prefix))
        
        all_readings = []
        for blob in blobs:
            blob_client = blob_service_client.get_blob_client(
                container=CONTAINER_NAME,
                blob=blob.name
            )
            blob_data = blob_client.download_blob().readall()
            readings = parse_blob_data(blob_data)
            
            if from_date or to_date:
                filtered = []
                for reading in readings:
                    reading_time = reading.get('timestamp', '')
                    if from_date and reading_time < from_date:
                        continue
                    if to_date and reading_time > to_date:
                        continue
                    filtered.append(reading)
                readings = filtered
            
            all_readings.extend(readings)
        
        all_readings.sort(key=lambda x: x.get('timestamp', ''))
        all_readings = all_readings[-limit:]
        
        return jsonify({
            "device_id": device_id,
            "readings": all_readings,
            "count": len(all_readings)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/analytics/aggregated', methods=['GET'])
def get_aggregated_data():
    """Get aggregated weather data (daily/weekly/monthly averages)."""
    device_id = request.args.get('device_id')
    period = request.args.get('period', 'day')  # day, week, month
    
    if not device_id:
        return jsonify({"error": "device_id parameter required"}), 400
    
    if not blob_service_client:
        return jsonify({"error": "Storage not configured"}), 503
    
    try:
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        blobs = list(container_client.list_blobs(name_starts_with=f"{device_id}/"))
        
        all_readings = []
        for blob in blobs:
            blob_client = blob_service_client.get_blob_client(
                container=CONTAINER_NAME,
                blob=blob.name
            )
            blob_data = blob_client.download_blob().readall()
            readings = parse_blob_data(blob_data)
            all_readings.extend(readings)
        
        if not all_readings:
            return jsonify({"error": "No data found"}), 404
        
        temps = [r.get('temperature', 0) for r in all_readings if 'temperature' in r]
        humidities = [r.get('humidity', 0) for r in all_readings if 'humidity' in r]
        rainfalls = [r.get('rainfall', 0) for r in all_readings if 'rainfall' in r]
        
        aggregated = {
            "device_id": device_id,
            "period": period,
            "temperature": {
                "min": round(min(temps), 2) if temps else 0,
                "max": round(max(temps), 2) if temps else 0,
                "avg": round(sum(temps) / len(temps), 2) if temps else 0
            },
            "humidity": {
                "min": round(min(humidities), 2) if humidities else 0,
                "max": round(max(humidities), 2) if humidities else 0,
                "avg": round(sum(humidities) / len(humidities), 2) if humidities else 0
            },
            "rainfall": {
                "total": round(sum(rainfalls), 2),
                "avg": round(sum(rainfalls) / len(rainfalls), 2) if rainfalls else 0
            },
            "readings_count": len(all_readings)
        }
        
        return jsonify(aggregated), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/analytics/irrigation', methods=['GET'])
def get_irrigation_recommendation():
    """Get irrigation recommendation based on current weather data."""
    device_id = request.args.get('device_id')
    crop_type = request.args.get('crop_type', 'general')
    
    if not device_id:
        return jsonify({"error": "device_id parameter required"}), 400
    
    if device_id not in latest_readings:
        response = get_current_reading(device_id)
        if response[1] != 200:
            return jsonify({"error": "Could not retrieve current data"}), 404
    
    current = latest_readings.get(device_id, {})
    
    soil_moisture = current.get('soil_moisture', 50)
    temperature = current.get('temperature', 20)
    rainfall = current.get('rainfall', 0)
    humidity = current.get('humidity', 50)
    
    needs_irrigation = False
    recommendation = "No irrigation needed"
    water_amount = 0
    
    if soil_moisture < 30:
        needs_irrigation = True
        recommendation = "Irrigation recommended - soil moisture is low"
        water_amount = 10 + (30 - soil_moisture) * 0.5
    elif soil_moisture < 40 and temperature > 25:
        needs_irrigation = True
        recommendation = "Light irrigation recommended - high temperature and moderate soil moisture"
        water_amount = 5
    elif rainfall > 5:
        recommendation = "Recent rainfall detected - no irrigation needed"
    else:
        recommendation = "Soil moisture levels are adequate"
    
    return jsonify({
        "device_id": device_id,
        "crop_type": crop_type,
        "current_conditions": {
            "soil_moisture": soil_moisture,
            "temperature": temperature,
            "rainfall": rainfall,
            "humidity": humidity
        },
        "recommendation": recommendation,
        "needs_irrigation": needs_irrigation,
        "suggested_water_amount_liters": round(water_amount, 2),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200


@app.route('/api/devices/<device_id>/status', methods=['GET'])
def get_device_status(device_id):
    """Get device connectivity status."""
    if device_id not in devices_registry:
        return jsonify({"error": "Device not found"}), 404
    
    status = "unknown"
    last_seen = None
    
    if device_id in latest_readings:
        last_seen = latest_readings[device_id].get('timestamp')
        try:
            last_time = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
            time_diff = datetime.now(timezone.utc).replace(tzinfo=last_time.tzinfo) - last_time
            if time_diff < timedelta(hours=1):
                status = "online"
            else:
                status = "offline"
        except:
            status = "unknown"
    
    return jsonify({
        "device_id": device_id,
        "status": status,
        "last_seen": last_seen,
        "registered": devices_registry[device_id].get("registered_at")
    }), 200


@app.route('/api/devices/<device_id>/alerts', methods=['GET'])
def get_device_alerts(device_id):
    """Get alerts/warnings for a device."""
    if device_id not in devices_registry:
        return jsonify({"error": "Device not found"}), 404
    
    device_alerts = alerts.get(device_id, [])
    
    severity = request.args.get('severity')
    if severity:
        device_alerts = [a for a in device_alerts if a.get('severity') == severity]
    
    limit = int(request.args.get('limit', 20))
    device_alerts = device_alerts[-limit:]
    
    return jsonify({
        "device_id": device_id,
        "alerts": device_alerts,
        "count": len(device_alerts),
        "has_critical": any(a.get('severity') == 'critical' for a in device_alerts),
        "has_warnings": any(a.get('severity') == 'warning' for a in device_alerts)
    }), 200


@app.route('/api/alerts', methods=['GET'])
def get_all_alerts():
    """Get all alerts across all devices."""
    all_alerts = []
    for device_id, device_alerts in alerts.items():
        for alert in device_alerts:
            alert_with_device = alert.copy()
            alert_with_device['device_id'] = device_id
            all_alerts.append(alert_with_device)
    
    all_alerts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    limit = int(request.args.get('limit', 50))
    all_alerts = all_alerts[:limit]
    
    return jsonify({
        "alerts": all_alerts,
        "count": len(all_alerts)
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Serve the farmer view interface."""
    return render_template('farmer.html')


@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Serve the system dashboard interface."""
    return render_template('dashboard.html')


@app.route('/device/<device_id>', methods=['GET'])
def device_page(device_id):
    """Serve the device details page."""
    return render_template('device.html')


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    start_polling()
    
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)

