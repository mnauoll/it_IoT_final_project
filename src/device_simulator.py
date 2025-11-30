"""
AgriWeather IoT Device Simulator
Simulates weather sensors collecting environmental data for agricultural monitoring.
"""

import random
import time
import json
import os
from datetime import datetime, timezone
from azure.iot.device import IoTHubDeviceClient, Message
from azure.storage.blob import BlobServiceClient


class WeatherDeviceSimulator:
    """Simulates an IoT weather monitoring device with multiple sensors."""
    
    def __init__(self, connection_string, device_id, location=None, storage_account_name=None, storage_account_key=None, container_name="weather-data"):
        """
        Initialize the device simulator.
        
        Args:
            connection_string: Azure IoT Hub device connection string
            device_id: Unique device identifier
            location: Optional location coordinates (latitude, longitude)
            storage_account_name: Optional Azure Storage account name for direct upload
            storage_account_key: Optional Azure Storage account key
            container_name: Blob container name
        """
        self.device_id = device_id
        self.location = location or (50.0, 20.0)  # Default location
        self.connection_string = connection_string
        self.device_client = None
        self.running = False
        
        # Blob Storage client for direct upload
        self.blob_service_client = None
        self.container_name = container_name
        if storage_account_name and storage_account_key:
            try:
                conn_str = f"DefaultEndpointsProtocol=https;AccountName={storage_account_name};AccountKey={storage_account_key};EndpointSuffix=core.windows.net"
                self.blob_service_client = BlobServiceClient.from_connection_string(conn_str)
                print(f"Blob Storage client initialized for direct upload")
            except Exception as e:
                print(f"Warning: Could not initialize Blob Storage client: {e}")
        
        # Sensor value ranges (realistic agricultural weather ranges)
        self.temp_range = (-10, 40)  # Celsius
        self.humidity_range = (20, 100)  # Percentage
        self.rainfall_range = (0, 50)  # mm per hour
        self.soil_moisture_range = (0, 100)  # Percentage
        self.wind_speed_range = (0, 50)  # km/h
        
        # Current sensor state (for gradual changes) - different starting values for realism
        hour = datetime.now().hour
        # Simulate daily temperature cycle
        base_temp = 20 + 8 * (0.5 - abs((hour - 12) / 12))  # Cooler at night, warmer during day
        self.current_temp = random.uniform(base_temp - 3, base_temp + 3)
        self.current_humidity = random.uniform(40, 70)
        self.current_rainfall = 0.0
        self.current_soil_moisture = random.uniform(30, 60)
        self.current_wind_speed = random.uniform(0, 15)
        
    def connect(self):
        """Connect to Azure IoT Hub."""
        try:
            self.device_client = IoTHubDeviceClient.create_from_connection_string(
                self.connection_string
            )
            self.device_client.connect()
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Device {self.device_id} connected to Azure IoT Hub")
            return True
        except Exception as e:
            print(f"Error connecting to IoT Hub: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Azure IoT Hub."""
        if self.device_client:
            self.device_client.disconnect()
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Device {self.device_id} disconnected")
    
    def generate_sensor_data(self):
        """
        Generate realistic sensor readings with gradual changes and daily cycles.
        
        Returns:
            dict: Sensor data with all weather parameters
        """
        now = datetime.now()
        hour = now.hour
        
        # Temperature: daily cycle + gradual changes
        # Cooler at night (0-6h), warmer during day (12-18h)
        daily_base = 20 + 10 * (0.5 - abs((hour - 12) / 12))
        temp_change = random.uniform(-1.5, 1.5)
        self.current_temp = max(
            self.temp_range[0],
            min(self.temp_range[1], daily_base + temp_change)
        )
        
        # Humidity: inversely related to temperature, higher at night
        humidity_base = 60 - (self.current_temp - 20) * 1.5
        if hour >= 0 and hour < 6:
            humidity_base += 15  # Higher humidity at night
        humidity_change = random.uniform(-3, 3)
        self.current_humidity = max(
            self.humidity_range[0],
            min(self.humidity_range[1], humidity_base + humidity_change)
        )
        
        # Rainfall: occasional rain events, more likely in afternoon
        rain_probability = 0.05
        if hour >= 14 and hour <= 18:
            rain_probability = 0.15  # More likely in afternoon
        
        if random.random() < rain_probability:
            self.current_rainfall = random.uniform(1, 15)
        else:
            self.current_rainfall = max(0, self.current_rainfall - random.uniform(0, 2))
        
        # Soil moisture: increases with rainfall, decreases over time
        if self.current_rainfall > 0:
            self.current_soil_moisture = min(
                self.soil_moisture_range[1],
                self.current_soil_moisture + self.current_rainfall * 0.4
            )
        else:
            # Evaporation rate depends on temperature
            evaporation = 0.5 + (self.current_temp - 20) * 0.1
            self.current_soil_moisture = max(
                self.soil_moisture_range[0],
                self.current_soil_moisture - random.uniform(0, evaporation)
            )
        
        # Wind speed: variable with some gusts, typically higher during day
        wind_base = 5 + (hour - 12) ** 2 * 0.1  # Slightly higher during day
        wind_change = random.uniform(-2, 2)
        # Occasional gusts
        if random.random() < 0.05:
            wind_change += random.uniform(5, 15)
        self.current_wind_speed = max(
            self.wind_speed_range[0],
            min(self.wind_speed_range[1], wind_base + wind_change)
        )
        
        return {
            "device_id": self.device_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "location": {
                "latitude": self.location[0],
                "longitude": self.location[1]
            },
            "temperature": round(self.current_temp, 2),  # Celsius
            "humidity": round(self.current_humidity, 2),  # Percentage
            "rainfall": round(self.current_rainfall, 2),  # mm per hour
            "soil_moisture": round(self.current_soil_moisture, 2),  # Percentage
            "wind_speed": round(self.current_wind_speed, 2)  # km/h
        }
    
    def send_data(self, data):
        """
        Send sensor data to Azure IoT Hub and optionally directly to Blob Storage.
        
        Args:
            data: Dictionary containing sensor readings
        """
        success = True
        
        # Send to IoT Hub
        if self.device_client:
            try:
                message = Message(json.dumps(data))
                message.content_type = "application/json"
                message.content_encoding = "utf-8"
                message.custom_properties["level"] = "storage"
                message.custom_properties["device_id"] = self.device_id
                
                self.device_client.send_message(message)
            except Exception as e:
                print(f"Error sending to IoT Hub: {e}")
                success = False
        
        # Also upload directly to Blob Storage for real-time simulation
        if self.blob_service_client:
            try:
                self.upload_to_blob_storage(data)
            except Exception as e:
                print(f"Error uploading to Blob Storage: {e}")
                success = False
        
        if success:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Data sent: "
                  f"Temp={data['temperature']}°C, "
                  f"Humidity={data['humidity']}%, "
                  f"Rainfall={data['rainfall']}mm/h, "
                  f"Soil={data['soil_moisture']}%, "
                  f"Wind={data['wind_speed']}km/h")
        
        return success
    
    def upload_to_blob_storage(self, data):
        """
        Upload sensor data directly to Blob Storage.
        Simulates real-time data collection by storing each reading immediately.
        
        Args:
            data: Dictionary containing sensor readings
        """
        if not self.blob_service_client:
            return
        
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            
            # Create blob name based on timestamp: device_id/0/YYYY/MM/DD/HH/mm
            timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            blob_name = f"{self.device_id}/0/{timestamp.strftime('%Y/%m/%d/%H')}/{timestamp.strftime('%M')}"
            
            # Get existing blob or create new
            blob_client = container_client.get_blob_client(blob_name)
            
            # Read existing data if blob exists
            existing_data = []
            try:
                if blob_client.exists():
                    blob_content = blob_client.download_blob().readall()
                    if isinstance(blob_content, bytes):
                        blob_content = blob_content.decode('utf-8')
                    for line in blob_content.strip().split('\n'):
                        if line.strip():
                            existing_data.append(json.loads(line))
            except:
                pass
            
            # Add new reading
            existing_data.append(data)
            
            # Upload updated blob
            content = '\n'.join(json.dumps(r) for r in existing_data)
            blob_client.upload_blob(content, overwrite=True)
            
        except Exception as e:
            raise Exception(f"Failed to upload to Blob Storage: {e}")
    
    def run(self, interval=15):
        """
        Run the device simulator continuously.
        
        Args:
            interval: Time interval between readings in seconds (default: 15 minutes = 900s)
        """
        if not self.device_client:
            if not self.connect():
                return
        
        self.running = True
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Device simulator started. Interval: {interval}s")
        
        try:
            while self.running:
                data = self.generate_sensor_data()
                self.send_data(data)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStopping device simulator...")
            self.running = False
            self.disconnect()


def main():
    """Main entry point for the device simulator."""
    # Get connection string from environment variable (required)
    conn_str = os.getenv("IOT_HUB_CONNECTION_STRING")
    if not conn_str:
        print("Error: IOT_HUB_CONNECTION_STRING environment variable is required")
        print("Please set it before running the device simulator:")
        print("  $env:IOT_HUB_CONNECTION_STRING='HostName=...;DeviceId=...;SharedAccessKey=...'")
        sys.exit(1)
    
    device_id = os.getenv("DEVICE_ID", "agriweather-device-001")
    location = (float(os.getenv("DEVICE_LAT", "50.0")), float(os.getenv("DEVICE_LON", "20.0")))
    interval = int(os.getenv("SEND_INTERVAL", "30"))  # seconds
    
    # Get Blob Storage credentials for direct upload (optional but recommended for real-time simulation)
    storage_account_name = os.getenv("STORAGE_ACCOUNT_NAME")
    storage_account_key = os.getenv("STORAGE_ACCOUNT_KEY")
    container_name = os.getenv("CONTAINER_NAME", "weather-data")
    
    simulator = WeatherDeviceSimulator(
        conn_str, 
        device_id, 
        location,
        storage_account_name=storage_account_name,
        storage_account_key=storage_account_key,
        container_name=container_name
    )
    simulator.run(interval)


if __name__ == "__main__":
    main()

