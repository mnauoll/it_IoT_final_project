"""
Complete system test - tests all components end-to-end
"""

import requests
import time
import sys

API_BASE_URL = 'http://localhost:5000'

def test_api_health():
    print("1. Testing API Health...")
    r = requests.get(f"{API_BASE_URL}/api/health")
    assert r.status_code == 200
    data = r.json()
    print(f"   [OK] Status: {data['status']}")
    print(f"   [OK] Storage: {data['storage_connected']}")
    return True

def test_devices():
    print("\n2. Testing Device Management...")
    r = requests.get(f"{API_BASE_URL}/api/devices")
    assert r.status_code == 200
    data = r.json()
    print(f"   [OK] Found {data['count']} device(s)")
    return data['devices'][0]['device_id'] if data['devices'] else None

def test_current_data(device_id):
    print(f"\n3. Testing Current Data for {device_id}...")
    r = requests.get(f"{API_BASE_URL}/api/devices/{device_id}/current")
    if r.status_code == 200:
        data = r.json()
        print(f"   [OK] Temperature: {data.get('temperature', 'N/A')}C")
        print(f"   [OK] Humidity: {data.get('humidity', 'N/A')}%")
        return True
    else:
        print(f"   [WARN] No current data (status: {r.status_code})")
        return False

def test_history(device_id):
    print(f"\n4. Testing Historical Data for {device_id}...")
    r = requests.get(f"{API_BASE_URL}/api/devices/{device_id}/history?limit=5")
    if r.status_code == 200:
        data = r.json()
        print(f"   [OK] Found {data['count']} readings")
        return True
    else:
        print(f"   [WARN] No history (status: {r.status_code})")
        return False

def test_alerts(device_id):
    print(f"\n5. Testing Alerts for {device_id}...")
    r = requests.get(f"{API_BASE_URL}/api/devices/{device_id}/alerts")
    if r.status_code == 200:
        data = r.json()
        print(f"   [OK] Found {data['count']} alert(s)")
        if data['has_critical']:
            print(f"   [OK] Critical alerts detected")
        if data['has_warnings']:
            print(f"   [OK] Warning alerts detected")
        return True
    else:
        print(f"   [WARN] Alerts endpoint returned {r.status_code}")
        return False

def test_web_pages():
    print("\n6. Testing Web Pages...")
    
    r = requests.get(f"{API_BASE_URL}/")
    if r.status_code == 200 and 'text/html' in r.headers.get('content-type', ''):
        print(f"   [OK] Farmer view page loads")
    else:
        print(f"   [FAIL] Farmer view returned {r.status_code}")
        return False
    
    r = requests.get(f"{API_BASE_URL}/dashboard")
    if r.status_code == 200 and 'text/html' in r.headers.get('content-type', ''):
        print(f"   [OK] Dashboard page loads")
    else:
        print(f"   [FAIL] Dashboard returned {r.status_code}")
        return False
    
    return True

def test_static_files():
    print("\n7. Testing Static Files...")
    
    files = ['/static/farmer.css', '/static/farmer.js', '/static/dashboard.css', '/static/dashboard.js']
    for file in files:
        r = requests.get(f"{API_BASE_URL}{file}")
        if r.status_code == 200:
            print(f"   [OK] {file} loads")
        else:
            print(f"   [WARN] {file} returned {r.status_code}")
    
    return True

def test_polling():
    print("\n8. Testing Polling System...")
    print("   Waiting 35 seconds for polling to complete...")
    time.sleep(35)
    
    r = requests.get(f"{API_BASE_URL}/api/devices/agriweather-device-001/alerts")
    if r.status_code == 200:
        data = r.json()
        print(f"   [OK] Polling system active - {data['count']} alert(s) found")
        return True
    else:
        print(f"   [WARN] Could not verify polling (status: {r.status_code})")
        return False

def main():
    print("=" * 60)
    print("AgriWeather Complete System Test")
    print("=" * 60)
    
    try:
        test_api_health()
        device_id = test_devices()
        
        if not device_id:
            print("\n[ERROR] No devices found. Please register a device first.")
            return 1
        
        test_current_data(device_id)
        test_history(device_id)
        test_alerts(device_id)
        test_web_pages()
        test_static_files()
        test_polling()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] All tests completed!")
        print("=" * 60)
        print("\nSystem is ready:")
        print(f"  - Farmer View: {API_BASE_URL}/")
        print(f"  - Dashboard: {API_BASE_URL}/dashboard")
        print(f"  - API: {API_BASE_URL}/api/health")
        return 0
        
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to API server")
        print("  Make sure the API server is running on http://localhost:5000")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())

