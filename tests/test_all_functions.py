"""
Test script to verify all API endpoints and CLI functions
"""

import requests
import json
import sys

API_BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("Testing /api/health...")
    response = requests.get(f"{API_BASE_URL}/api/health")
    assert response.status_code == 200
    data = response.json()
    print(f"  [OK] Health: {data['status']}")
    print(f"  [OK] Storage: {data['storage_connected']}")
    return True

def test_list_devices():
    """Test list devices"""
    print("\nTesting /api/devices (GET)...")
    response = requests.get(f"{API_BASE_URL}/api/devices")
    assert response.status_code == 200
    data = response.json()
    print(f"  [OK] Found {data['count']} device(s)")
    for device in data['devices']:
        print(f"    - {device['device_id']}: {device.get('name', 'N/A')}")
    return True

def test_get_device():
    """Test get single device"""
    print("\nTesting /api/devices/<id> (GET)...")
    response = requests.get(f"{API_BASE_URL}/api/devices/agriweather-device-001")
    assert response.status_code == 200
    data = response.json()
    print(f"  [OK] Device: {data['device_id']}")
    print(f"  [OK] Name: {data.get('name', 'N/A')}")
    return True

def test_get_current():
    """Test get current readings"""
    print("\nTesting /api/devices/<id>/current (GET)...")
    response = requests.get(f"{API_BASE_URL}/api/devices/agriweather-device-001/current")
    assert response.status_code == 200
    data = response.json()
    print(f"  [OK] Temperature: {data.get('temperature', 'N/A')}C")
    print(f"  [OK] Humidity: {data.get('humidity', 'N/A')}%")
    print(f"  [OK] Soil Moisture: {data.get('soil_moisture', 'N/A')}%")
    return True

def test_get_history():
    """Test get historical data"""
    print("\nTesting /api/devices/<id>/history (GET)...")
    response = requests.get(f"{API_BASE_URL}/api/devices/agriweather-device-001/history?limit=3")
    assert response.status_code == 200
    data = response.json()
    print(f"  [OK] Found {data['count']} readings")
    return True

def test_get_aggregated():
    """Test aggregated data"""
    print("\nTesting /api/analytics/aggregated (GET)...")
    response = requests.get(f"{API_BASE_URL}/api/analytics/aggregated?device_id=agriweather-device-001&period=day")
    assert response.status_code == 200
    data = response.json()
    print(f"  [OK] Temperature avg: {data['temperature']['avg']}C")
    print(f"  [OK] Total rainfall: {data['rainfall']['total']}mm")
    return True

def test_irrigation():
    """Test irrigation recommendation"""
    print("\nTesting /api/analytics/irrigation (GET)...")
    response = requests.get(f"{API_BASE_URL}/api/analytics/irrigation?device_id=agriweather-device-001&crop_type=wheat")
    assert response.status_code == 200
    data = response.json()
    print(f"  [OK] Recommendation: {data['recommendation']}")
    print(f"  [OK] Needs irrigation: {data['needs_irrigation']}")
    return True

def test_device_status():
    """Test device status"""
    print("\nTesting /api/devices/<id>/status (GET)...")
    response = requests.get(f"{API_BASE_URL}/api/devices/agriweather-device-001/status")
    assert response.status_code == 200
    data = response.json()
    print(f"  [OK] Status: {data['status']}")
    return True

def test_register_device():
    """Test register device"""
    print("\nTesting /api/devices (POST)...")
    new_device = {
        "device_id": "test-device-001",
        "name": "Test Device",
        "location": {"latitude": 52.0, "longitude": 21.0}
    }
    response = requests.post(f"{API_BASE_URL}/api/devices", json=new_device)
    assert response.status_code == 201
    data = response.json()
    print(f"  [OK] Registered: {data['device_id']}")
    return True

def test_alerts_endpoint():
    """Test alerts endpoint"""
    device_id = "agriweather-device-001"
    print(f"\nTesting /api/devices/<id>/alerts (GET)...")
    response = requests.get(f"{API_BASE_URL}/api/devices/{device_id}/alerts")
    assert response.status_code == 200
    data = response.json()
    print(f"  [OK] Found {data['count']} alert(s)")
    print(f"  [OK] Has critical: {data['has_critical']}")
    print(f"  [OK] Has warnings: {data['has_warnings']}")
    if data['alerts']:
        latest = data['alerts'][-1]
        print(f"  [OK] Latest alert: {latest.get('severity', 'N/A')} - {latest.get('message', 'N/A')[:50]}...")
    return True

def test_all_alerts():
    """Test all alerts endpoint"""
    print("\nTesting /api/alerts (GET)...")
    response = requests.get(f"{API_BASE_URL}/api/alerts?limit=10")
    assert response.status_code == 200
    data = response.json()
    print(f"  [OK] Found {data['count']} total alert(s)")
    if data['alerts']:
        print(f"  [OK] Sample alerts:")
        for alert in data['alerts'][:3]:
            print(f"    - {alert.get('severity', 'N/A')}: {alert.get('message', 'N/A')[:40]}...")
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("AgriWeather API - Functionality Test")
    print("=" * 60)
    
    try:
        test_health()
        test_list_devices()
        test_get_device()
        test_get_current()
        test_get_history()
        test_get_aggregated()
        test_irrigation()
        test_device_status()
        test_register_device()
        test_alerts_endpoint()
        test_all_alerts()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] All tests passed!")
        print("=" * 60)
        return 0
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to API server")
        print("  Make sure the API server is running on http://localhost:5000")
        return 1
    except AssertionError as e:
        print(f"\n[FAILED] Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

