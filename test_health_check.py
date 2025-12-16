"""
Test script for health check endpoint.
This can be run locally or in CI/CD to verify the health check is working.
"""
import requests
import sys
import time

def test_health_endpoint(base_url="http://localhost:8080"):
    """Test the main health check endpoint."""
    print(f"Testing health endpoint: {base_url}/health")
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code in [200, 503]:
            print("✓ Health endpoint is accessible")
            return True
        else:
            print(f"✗ Unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Error accessing health endpoint: {e}")
        return False

def test_liveness_endpoint(base_url="http://localhost:8080"):
    """Test the liveness probe endpoint."""
    print(f"\nTesting liveness endpoint: {base_url}/health/live")
    
    try:
        response = requests.get(f"{base_url}/health/live", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✓ Liveness endpoint is accessible")
            return True
        else:
            print(f"✗ Unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Error accessing liveness endpoint: {e}")
        return False

def test_readiness_endpoint(base_url="http://localhost:8080"):
    """Test the readiness probe endpoint."""
    print(f"\nTesting readiness endpoint: {base_url}/health/ready")
    
    try:
        response = requests.get(f"{base_url}/health/ready", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code in [200, 503]:
            print("✓ Readiness endpoint is accessible")
            return True
        else:
            print(f"✗ Unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Error accessing readiness endpoint: {e}")
        return False

def main():
    """Run all health check tests."""
    print("=" * 60)
    print("Health Check Endpoint Tests")
    print("=" * 60)
    
    # Allow custom base URL from command line
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    
    results = []
    results.append(test_health_endpoint(base_url))
    results.append(test_liveness_endpoint(base_url))
    results.append(test_readiness_endpoint(base_url))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    if all(results):
        print("✓ All health check endpoints are working correctly")
        return 0
    else:
        print(f"✗ Some tests failed ({sum(results)}/{len(results)} passed)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
