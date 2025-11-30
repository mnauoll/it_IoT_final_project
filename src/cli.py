"""
AgriWeather CLI - Command-line interface for the AgriWeather IoT Platform
Professional CLI tool for device management and weather data access.
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import configparser


class AgriWeatherCLI:
    """Command-line interface for AgriWeather platform."""
    
    def __init__(self, api_base_url: Optional[str] = None, config_file: Optional[str] = None):
        """
        Initialize the CLI.
        
        Args:
            api_base_url: Base URL for the REST API (defaults to env var or config)
            config_file: Optional path to configuration file (deprecated, use env vars)
        """
        # Get API URL from environment variable or argument, default to localhost
        self.api_base_url = (
            api_base_url or
            os.getenv('AGRIWEATHER_API_URL') or
            'http://localhost:5000'
        )
        
        # Optional: support config file if provided
        if config_file and os.path.exists(config_file):
            self.config = configparser.ConfigParser()
            self.config.read(config_file)
            if not api_base_url and not os.getenv('AGRIWEATHER_API_URL'):
                self.api_base_url = self.config.get('api', 'base_url', fallback=self.api_base_url)
        
        # Remove trailing slash
        self.api_base_url = self.api_base_url.rstrip('/')
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        Make HTTP request to API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
            
        Returns:
            Response data as dictionary
        """
        url = f"{self.api_base_url}{endpoint}"
        
        try:
            response = requests.request(method, url, timeout=10, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to API at {self.api_base_url}")
            print("Make sure the API server is running and the URL is correct.")
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            try:
                error_data = response.json()
                print(f"Details: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"Response: {response.text}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    def health_check(self):
        """Check API health status."""
        data = self._make_request('GET', '/api/health')
        
        print("API Health Status:")
        print(f"  Status: {data.get('status', 'unknown')}")
        print(f"  Timestamp: {data.get('timestamp', 'N/A')}")
        print(f"  Storage Connected: {data.get('storage_connected', False)}")
        print(f"  IoT Hub Connected: {data.get('iot_hub_connected', False)}")
    
    def list_devices(self):
        """List all registered devices."""
        data = self._make_request('GET', '/api/devices')
        
        devices = data.get('devices', [])
        count = data.get('count', 0)
        
        print(f"\nRegistered Devices ({count}):")
        print("-" * 80)
        
        if not devices:
            print("No devices registered.")
            return
        
        for device in devices:
            print(f"\nDevice ID: {device.get('device_id')}")
            print(f"  Name: {device.get('name', 'N/A')}")
            location = device.get('location', {})
            print(f"  Location: {location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')}")
            print(f"  Status: {device.get('status', 'unknown')}")
            if 'last_reading' in device:
                print(f"  Last Reading: {device.get('last_reading', 'N/A')}")
    
    def register_device(self, device_id: str, name: Optional[str] = None, 
                       latitude: Optional[float] = None, longitude: Optional[float] = None):
        """Register a new device."""
        payload = {
            "device_id": device_id
        }
        
        if name:
            payload["name"] = name
        
        if latitude is not None and longitude is not None:
            payload["location"] = {"latitude": latitude, "longitude": longitude}
        
        data = self._make_request('POST', '/api/devices', json=payload)
        
        print("Device registered successfully:")
        print(f"  Device ID: {data.get('device_id')}")
        print(f"  Name: {data.get('name')}")
        print(f"  Registered At: {data.get('registered_at')}")
    
    def get_current(self, device_id: str, output_file: Optional[str] = None):
        """Get current weather readings for a device."""
        data = self._make_request('GET', f'/api/devices/{device_id}/current')
        
        # Format output
        print(f"\nCurrent Weather - Device: {device_id}")
        print("-" * 80)
        print(f"Timestamp: {data.get('timestamp', 'N/A')}")
        
        location = data.get('location', {})
        if location:
            print(f"Location: {location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')}")
        
        print(f"\nSensor Readings:")
        print(f"  Temperature: {data.get('temperature', 'N/A')} °C")
        print(f"  Humidity: {data.get('humidity', 'N/A')} %")
        print(f"  Rainfall: {data.get('rainfall', 'N/A')} mm/h")
        print(f"  Soil Moisture: {data.get('soil_moisture', 'N/A')} %")
        print(f"  Wind Speed: {data.get('wind_speed', 'N/A')} km/h")
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\nData saved to: {output_file}")
    
    def get_history(self, device_id: str, from_date: Optional[str] = None, 
                   to_date: Optional[str] = None, limit: int = 10, 
                   output_file: Optional[str] = None):
        """Get historical weather data."""
        params = {'limit': limit}
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        
        data = self._make_request('GET', f'/api/devices/{device_id}/history', params=params)
        
        readings = data.get('readings', [])
        count = data.get('count', 0)
        
        print(f"\nHistorical Data - Device: {device_id}")
        print(f"Total Readings: {count}")
        print("-" * 80)
        
        if not readings:
            print("No historical data found.")
            return
        
        # Show last N readings
        for reading in readings[-limit:]:
            print(f"\n{reading.get('timestamp', 'N/A')}")
            print(f"  Temperature: {reading.get('temperature', 'N/A')} °C")
            print(f"  Humidity: {reading.get('humidity', 'N/A')} %")
            print(f"  Rainfall: {reading.get('rainfall', 'N/A')} mm/h")
            print(f"  Soil Moisture: {reading.get('soil_moisture', 'N/A')} %")
            print(f"  Wind Speed: {reading.get('wind_speed', 'N/A')} km/h")
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\nData saved to: {output_file}")
    
    def get_aggregated(self, device_id: str, period: str = 'day'):
        """Get aggregated weather data."""
        params = {'device_id': device_id, 'period': period}
        data = self._make_request('GET', '/api/analytics/aggregated', params=params)
        
        print(f"\nAggregated Data - Device: {device_id} (Period: {period})")
        print("-" * 80)
        
        temp = data.get('temperature', {})
        print(f"\nTemperature:")
        print(f"  Min: {temp.get('min', 'N/A')} °C")
        print(f"  Max: {temp.get('max', 'N/A')} °C")
        print(f"  Avg: {temp.get('avg', 'N/A')} °C")
        
        humidity = data.get('humidity', {})
        print(f"\nHumidity:")
        print(f"  Min: {humidity.get('min', 'N/A')} %")
        print(f"  Max: {humidity.get('max', 'N/A')} %")
        print(f"  Avg: {humidity.get('avg', 'N/A')} %")
        
        rainfall = data.get('rainfall', {})
        print(f"\nRainfall:")
        print(f"  Total: {rainfall.get('total', 'N/A')} mm")
        print(f"  Avg: {rainfall.get('avg', 'N/A')} mm/h")
        
        print(f"\nTotal Readings: {data.get('readings_count', 0)}")
    
    def recommend_irrigation(self, device_id: str, crop_type: str = 'general'):
        """Get irrigation recommendation."""
        params = {'device_id': device_id, 'crop_type': crop_type}
        data = self._make_request('GET', '/api/analytics/irrigation', params=params)
        
        print(f"\nIrrigation Recommendation - Device: {device_id}")
        print(f"Crop Type: {crop_type}")
        print("-" * 80)
        
        conditions = data.get('current_conditions', {})
        print(f"\nCurrent Conditions:")
        print(f"  Soil Moisture: {conditions.get('soil_moisture', 'N/A')} %")
        print(f"  Temperature: {conditions.get('temperature', 'N/A')} °C")
        print(f"  Rainfall: {conditions.get('rainfall', 'N/A')} mm/h")
        print(f"  Humidity: {conditions.get('humidity', 'N/A')} %")
        
        print(f"\nRecommendation: {data.get('recommendation', 'N/A')}")
        print(f"Needs Irrigation: {'Yes' if data.get('needs_irrigation') else 'No'}")
        
        if data.get('needs_irrigation'):
            print(f"Suggested Water Amount: {data.get('suggested_water_amount_liters', 0)} liters")
    
    def get_device_status(self, device_id: str):
        """Get device connectivity status."""
        data = self._make_request('GET', f'/api/devices/{device_id}/status')
        
        print(f"\nDevice Status - {device_id}")
        print("-" * 80)
        print(f"Status: {data.get('status', 'unknown')}")
        print(f"Last Seen: {data.get('last_seen', 'Never')}")
        print(f"Registered: {data.get('registered', 'N/A')}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='AgriWeather CLI - IoT Weather Monitoring Platform',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check API health
  python cli.py health
  
  # List all devices
  python cli.py devices list
  
  # Register a new device
  python cli.py devices register --device-id device001 --name "Field A" --lat 50.0 --lon 20.0
  
  # Get current weather
  python cli.py data current --device-id device001
  
  # Get historical data
  python cli.py data history --device-id device001 --from 2025-01-01 --to 2025-01-31 --limit 20
  
  # Get irrigation recommendation
  python cli.py analytics irrigation --device-id device001 --crop-type wheat
        """
    )
    
    parser.add_argument('--api-url', help='API base URL (overrides config)')
    parser.add_argument('--config', help='Configuration file path (optional, prefer environment variables)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Health check
    health_parser = subparsers.add_parser('health', help='Check API health status')
    
    # Device management
    device_parser = subparsers.add_parser('devices', help='Device management')
    device_subparsers = device_parser.add_subparsers(dest='device_action')
    
    device_subparsers.add_parser('list', help='List all devices')
    
    register_parser = device_subparsers.add_parser('register', help='Register a new device')
    register_parser.add_argument('--device-id', required=True, help='Device ID')
    register_parser.add_argument('--name', help='Device name')
    register_parser.add_argument('--lat', type=float, help='Latitude')
    register_parser.add_argument('--lon', type=float, help='Longitude')
    
    # Data queries
    data_parser = subparsers.add_parser('data', help='Weather data queries')
    data_subparsers = data_parser.add_subparsers(dest='data_action')
    
    current_parser = data_subparsers.add_parser('current', help='Get current weather readings')
    current_parser.add_argument('--device-id', required=True, help='Device ID')
    current_parser.add_argument('--output', help='Save output to JSON file')
    
    history_parser = data_subparsers.add_parser('history', help='Get historical data')
    history_parser.add_argument('--device-id', required=True, help='Device ID')
    history_parser.add_argument('--from', dest='from_date', help='Start date (YYYY-MM-DD)')
    history_parser.add_argument('--to', dest='to_date', help='End date (YYYY-MM-DD)')
    history_parser.add_argument('--limit', type=int, default=10, help='Number of readings (default: 10)')
    history_parser.add_argument('--output', help='Save output to JSON file')
    
    # Analytics
    analytics_parser = subparsers.add_parser('analytics', help='Analytics and recommendations')
    analytics_subparsers = analytics_parser.add_subparsers(dest='analytics_action')
    
    aggregated_parser = analytics_subparsers.add_parser('aggregated', help='Get aggregated data')
    aggregated_parser.add_argument('--device-id', required=True, help='Device ID')
    aggregated_parser.add_argument('--period', choices=['day', 'week', 'month'], default='day', help='Aggregation period')
    
    irrigation_parser = analytics_subparsers.add_parser('irrigation', help='Get irrigation recommendation')
    irrigation_parser.add_argument('--device-id', required=True, help='Device ID')
    irrigation_parser.add_argument('--crop-type', default='general', help='Crop type')
    
    # Status
    status_parser = subparsers.add_parser('status', help='Get device status')
    status_parser.add_argument('--device-id', required=True, help='Device ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize CLI
    cli = AgriWeatherCLI(api_base_url=args.api_url, config_file=args.config)
    
    # Execute command
    try:
        if args.command == 'health':
            cli.health_check()
        
        elif args.command == 'devices':
            if args.device_action == 'list':
                cli.list_devices()
            elif args.device_action == 'register':
                cli.register_device(
                    args.device_id,
                    name=args.name,
                    latitude=args.lat,
                    longitude=args.lon
                )
            else:
                device_parser.print_help()
        
        elif args.command == 'data':
            if args.data_action == 'current':
                cli.get_current(args.device_id, output_file=args.output)
            elif args.data_action == 'history':
                cli.get_history(
                    args.device_id,
                    from_date=args.from_date,
                    to_date=args.to_date,
                    limit=args.limit,
                    output_file=args.output
                )
            else:
                data_parser.print_help()
        
        elif args.command == 'analytics':
            if args.analytics_action == 'aggregated':
                cli.get_aggregated(args.device_id, period=args.period)
            elif args.analytics_action == 'irrigation':
                cli.recommend_irrigation(args.device_id, crop_type=args.crop_type)
            else:
                analytics_parser.print_help()
        
        elif args.command == 'status':
            cli.get_device_status(args.device_id)
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

