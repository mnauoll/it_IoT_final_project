"""
Script to generate and upload test weather data to Azure Blob Storage
"""

import os
import json
from datetime import datetime, timedelta, timezone
from azure.storage.blob import BlobServiceClient
import random


def generate_test_data(device_id, num_readings=50, start_hours_ago=24, device_variation=0):
    """
    Generate test weather data for a device with variation.
    
    Args:
        device_id: Device identifier
        num_readings: Number of readings to generate
        start_hours_ago: How many hours ago to start from
        device_variation: Variation factor for different devices (0-4)
    
    Returns:
        List of reading dictionaries
    """
    readings = []
    base_time = datetime.now(timezone.utc) - timedelta(hours=start_hours_ago)
    
    # Different base values for different devices to create variation
    base_temp = 15 + device_variation * 5  # 15-35°C range
    base_humidity = 40 + device_variation * 10  # 40-80% range
    base_soil = 30 + device_variation * 15  # 30-90% range
    
    temp = random.uniform(base_temp - 5, base_temp + 5)
    humidity = random.uniform(base_humidity - 10, base_humidity + 10)
    rainfall = 0.0
    soil_moisture = random.uniform(base_soil - 10, base_soil + 10)
    wind_speed = random.uniform(0, 15 + device_variation * 5)
    
    for i in range(num_readings):
        timestamp = base_time + timedelta(minutes=i * 15)
        
        # Temperature: more variation with daily cycle and occasional extremes
        temp_change = random.uniform(-2, 2)
        hour = timestamp.hour
        daily_adjustment = 8 * (0.5 - abs((hour - 12) / 12))
        temp = max(-5, min(45, temp + temp_change + daily_adjustment * 0.2))
        
        # Occasional extreme temperatures for testing alerts
        if random.random() < 0.1:  # 10% chance of extreme
            if random.random() < 0.5:
                temp = random.uniform(-2, 3)  # Low temp for frost warning
            else:
                temp = random.uniform(36, 42)  # High temp warning
        
        # Humidity: more variation
        humidity_change = random.uniform(-5, 5)
        humidity = max(15, min(100, humidity + humidity_change))
        
        # Occasional very low humidity
        if random.random() < 0.05:
            humidity = random.uniform(10, 20)
        
        # Rainfall: more frequent events
        if random.random() < 0.08:  # 8% chance
            rainfall = random.uniform(2, 20)
        else:
            rainfall = max(0, rainfall - random.uniform(0, 3))
        
        # Soil moisture: more variation, occasional low values for warnings
        if rainfall > 0:
            soil_moisture = min(100, soil_moisture + rainfall * 0.4)
        else:
            soil_moisture = max(0, soil_moisture - random.uniform(0, 2))
        
        # Occasional low soil moisture for irrigation warnings
        if random.random() < 0.1:
            soil_moisture = random.uniform(15, 30)
        
        # Wind speed: more variation, occasional high winds
        wind_change = random.uniform(-3, 3)
        wind_speed = max(0, min(60, wind_speed + wind_change))
        
        # Occasional high wind for warnings
        if random.random() < 0.05:
            wind_speed = random.uniform(42, 55)
        
        reading = {
            "device_id": device_id,
            "timestamp": timestamp.isoformat(),
            "location": {
                "latitude": 50.0,
                "longitude": 20.0
            },
            "temperature": round(temp, 2),
            "humidity": round(humidity, 2),
            "rainfall": round(rainfall, 2),
            "soil_moisture": round(soil_moisture, 2),
            "wind_speed": round(wind_speed, 2)
        }
        
        readings.append(reading)
    
    return readings


def upload_to_blob_storage(readings, storage_account_name, storage_account_key, container_name, device_id):
    """
    Upload readings to Blob Storage in the format expected by IoT Hub routing.
    
    Args:
        readings: List of reading dictionaries
        storage_account_name: Azure Storage account name
        storage_account_key: Azure Storage account key
        container_name: Container name
        device_id: Device ID (used in blob path)
    """
    # Create connection string
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={storage_account_name};AccountKey={storage_account_key};EndpointSuffix=core.windows.net"
    
    # Create blob service client
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    
    # Group readings by hour (similar to IoT Hub routing format)
    readings_by_hour = {}
    for reading in readings:
        timestamp = datetime.fromisoformat(reading['timestamp'].replace('Z', '+00:00'))
        hour_key = timestamp.strftime('%Y/%m/%d/%H')
        
        if hour_key not in readings_by_hour:
            readings_by_hour[hour_key] = []
        readings_by_hour[hour_key].append(reading)
    
    # Upload each hour's data as a separate blob
    uploaded_count = 0
    for hour_key, hour_readings in readings_by_hour.items():
        # Format: {iothub}/{partition}/{YYYY}/{MM}/{DD}/{HH}/{mm}
        # Using partition 0 and minute 00 for simplicity
        blob_name = f"{device_id}/0/{hour_key}/00"
        
        # Convert to JSON lines format (one JSON object per line)
        content = '\n'.join(json.dumps(reading) for reading in hour_readings)
        
        # Upload blob
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(content, overwrite=True)
        
        uploaded_count += len(hour_readings)
        print(f"Uploaded {len(hour_readings)} readings to {blob_name}")
    
    print(f"\nTotal: {uploaded_count} readings uploaded to {len(readings_by_hour)} blob(s)")


def main():
    """Main function."""
    # Get configuration from environment variables
    storage_account_name = os.getenv("STORAGE_ACCOUNT_NAME", "agriweather9207")
    storage_account_key = os.getenv("STORAGE_ACCOUNT_KEY", "")
    container_name = os.getenv("CONTAINER_NAME", "weather-data")
    
    if not storage_account_key:
        print("Error: STORAGE_ACCOUNT_KEY environment variable not set")
        print("Set it with: $env:STORAGE_ACCOUNT_KEY='your-key'")
        return
    
    # Generate data for 5 devices with different variations
    devices = [
        ("agriweather-device-001", "Field A Sensor", 0),
        ("agriweather-device-002", "Field B Sensor", 1),
        ("agriweather-device-003", "Field C Sensor", 2),
        ("agriweather-device-004", "Field D Sensor", 3),
        ("agriweather-device-005", "Field E Sensor", 4),
    ]
    
    print("Generating test data for 5 devices...")
    print(f"Storage Account: {storage_account_name}")
    print(f"Container: {container_name}\n")
    
    total_readings = 0
    for device_id, device_name, variation in devices:
        print(f"Generating data for {device_id} ({device_name})...")
        readings = generate_test_data(
            device_id, 
            num_readings=80, 
            start_hours_ago=48,
            device_variation=variation
        )
        print(f"  Generated {len(readings)} readings")
        
        upload_to_blob_storage(
            readings,
            storage_account_name,
            storage_account_key,
            container_name,
            device_id
        )
        total_readings += len(readings)
    
    print(f"\nTest data upload complete!")
    print(f"Total: {total_readings} readings uploaded for {len(devices)} devices")
    print("\nYou can now test the API with:")
    print("  python cli.py devices list")
    print("  python cli.py data current --device-id agriweather-device-001")
    print("  python cli.py data history --device-id agriweather-device-001 --limit 10")


if __name__ == "__main__":
    main()

