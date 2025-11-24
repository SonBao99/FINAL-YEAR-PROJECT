"""
Quick test script to verify dashboard setup
"""
import requests
import sys

API_URL = "http://localhost:8000"

def test_api_connection():
    """Test if API is running"""
    try:
        response = requests.get(f"{API_URL}/api/sessions", timeout=3)
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("   Make sure the server is running:")
        print("   py -3 -m uvicorn attendance_api:app --reload --port 8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_endpoints():
    """Test key API endpoints"""
    endpoints = [
        "/api/sessions",
        "/api/students",
        "/api/courses"
    ]
    
    print("\n📡 Testing API endpoints...")
    all_ok = True
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_URL}{endpoint}", timeout=3)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint} - OK ({len(data)} items)")
            else:
                print(f"⚠️  {endpoint} - Status {response.status_code}")
                all_ok = False
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
            all_ok = False
    
    return all_ok

def test_websocket_endpoint():
    """Check if WebSocket endpoint exists (can't fully test without WS client)"""
    print("\n🔌 WebSocket endpoint:")
    print("   ws://localhost:8000/ws/attendance/{session_id}")
    print("   (Manual testing required)")

def main():
    print("=" * 50)
    print("Dashboard Setup Test")
    print("=" * 50)
    
    # Test API connection
    if not test_api_connection():
        sys.exit(1)
    
    # Test endpoints
    if not test_endpoints():
        print("\n⚠️  Some endpoints failed, but dashboard may still work")
    
    # WebSocket info
    test_websocket_endpoint()
    
    print("\n" + "=" * 50)
    print("✅ Setup check complete!")
    print("\nNext steps:")
    print("1. Open web_dashboard.html in your browser")
    print("2. Or navigate to http://localhost:8000/")
    print("3. Follow TESTING_GUIDE.md for detailed tests")
    print("=" * 50)

if __name__ == "__main__":
    main()


