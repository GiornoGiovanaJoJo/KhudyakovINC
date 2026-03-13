import urllib.request
import urllib.error
import sys
import time

def check_health(url, name, expected_status=200, timeout=10):
    print(f"Checking {name} at {url}...")
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            if response.status == expected_status:
                print(f"✅ {name} is healthy (Status {response.status})")
                return True
            else:
                print(f"❌ {name} returned unexpected status {response.status}")
                return False
    except urllib.error.HTTPError as e:
        if e.code == expected_status:
            print(f"✅ {name} is healthy (Status {e.code})")
            return True
        print(f"❌ {name} returned HTTP error {e.code}")
        return False
    except Exception as e:
        print(f"❌ {name} health check failed: {e}")
        return False

def main():
    # We wait a bit for containers to start up
    print("Waiting 15 seconds for services to settle...")
    time.sleep(15)
    
    # In Docker environment, we check via localhost since we are on the host box
    # mappings: backend:8000, frontend:3000
    backend_url = "http://localhost:8000/api/health"
    frontend_url = "http://localhost:3000/"
    
    success = True
    if not check_health(backend_url, "Backend API"):
        success = False
    if not check_health(frontend_url, "Frontend"):
        success = False
        
    if not success:
        print("FAIL: One or more services are unhealthy.")
        sys.exit(1)
    
    print("SUCCESS: All services are healthy.")

if __name__ == "__main__":
    main()
