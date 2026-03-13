import httpx
import sys
import time

def check_health(url, name, expected_status=200, timeout=10):
    print(f"Checking {name} at {url}...")
    try:
        with httpx.Client(timeout=timeout) as client:
            res = client.get(url)
            if res.status_code == expected_status:
                print(f"✅ {name} is healthy (Status {res.status_code})")
                return True
            else:
                print(f"❌ {name} returned unexpected status {res.status_code}")
                return False
    except Exception as e:
        print(f"❌ {name} health check failed: {e}")
        return False

def main():
    # We wait a bit for containers to start up
    print("Waiting for services to settle...")
    time.sleep(10)
    
    # Check internal backend health (running in bridge network)
    # Note: In CI we might be checking the public URL or local port
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
