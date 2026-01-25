import requests

# Test single subject endpoint
try:
    response = requests.get("http://127.0.0.1:8001/subjects/CSE2101/periods-needed")
    print("Single subject endpoint:")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test bulk endpoint
try:
    response = requests.get("http://127.0.0.1:8001/subjects/periods-info")
    print("\nBulk endpoint:")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
