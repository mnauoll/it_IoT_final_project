"""
Test script to verify real-time data updates
Checks that new data is generated and available every 30 seconds
"""

import requests
import time
import sys

API_BASE_URL = "http://localhost:5000"
DEVICE_ID = "agriweather-device-001"

def get_current_data():
    """Get current data for device"""
    try:
        r = requests.get(f"{API_BASE_URL}/api/devices/{DEVICE_ID}/current", timeout=5)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("=" * 60)
    print("Real-time Data Update Test")
    print("=" * 60)
    print(f"Device: {DEVICE_ID}")
    print(f"API: {API_BASE_URL}")
    print()
    
    # Check API is running
    try:
        r = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if r.status_code != 200:
            print("ERROR: API server is not running or not accessible")
            return 1
    except Exception as e:
        print(f"ERROR: Cannot connect to API server: {e}")
        print("Make sure API server is running: python src/api_server.py")
        return 1
    
    print("API server is running")
    print()
    
    # Get initial reading
    print("Getting initial reading...")
    data1 = get_current_data()
    if not data1:
        print("ERROR: Could not get initial data")
        return 1
    
    temp1 = data1.get('temperature', 0)
    timestamp1 = data1.get('timestamp', '')[:19]
    print(f"  Temperature: {temp1}°C")
    print(f"  Timestamp: {timestamp1}")
    print()
    
    # Wait 35 seconds (polling interval is 30s)
    print("Waiting 35 seconds for polling to update data...")
    print("(Device simulator should be sending new data every 30 seconds)")
    for i in range(35, 0, -5):
        print(f"  Waiting... {i}s remaining", end='\r')
        time.sleep(5)
    print()
    print()
    
    # Get updated reading
    print("Getting updated reading...")
    data2 = get_current_data()
    if not data2:
        print("ERROR: Could not get updated data")
        return 1
    
    temp2 = data2.get('temperature', 0)
    timestamp2 = data2.get('timestamp', '')[:19]
    print(f"  Temperature: {temp2}°C")
    print(f"  Timestamp: {timestamp2}")
    print()
    
    # Compare
    print("=" * 60)
    if timestamp1 != timestamp2:
        print("[SUCCESS] Data timestamp changed - new data detected!")
        print(f"  Old timestamp: {timestamp1}")
        print(f"  New timestamp: {timestamp2}")
        if temp1 != temp2:
            print(f"[OK] Temperature changed: {temp1}C -> {temp2}C")
        else:
            print(f"  Temperature unchanged: {temp1}C (may be coincidental)")
        return 0
    else:
        print("[WARNING] Data timestamp unchanged")
        print(f"  Timestamp: {timestamp1}")
        print()
        print("Possible reasons:")
        print("  1. Device simulator is not running")
        print("  2. Data is not reaching Blob Storage")
        print("  3. Polling has not run yet (wait longer)")
        print()
        print("To fix:")
        print("  1. Start device simulator:")
        print("     $env:IOT_HUB_CONNECTION_STRING='...'")
        print("     $env:SEND_INTERVAL='30'")
        print("     python src/device_simulator.py")
        print()
        print("  2. Check API server logs for polling messages")
        return 1

if __name__ == "__main__":
    sys.exit(main())

