import requests
import json
import time

base_url = "https://banking-app-u4dg.onrender.com"

print(f"Testing {base_url}...")

# 1. Health Check
try:
    r = requests.get(f"{base_url}/health")
    print(f"Health Check: {r.status_code} - {r.text}")
except Exception as e:
    print(f"Health Check Failed: {e}")

# 2. Registration
timestamp = int(time.time())
user_data = {
    "username": f"tester_{timestamp}",
    "email": f"test_{timestamp}@example.com",
    "password": "password123",
    "phone": "9999999999"
}

try:
    print(f"Attempting Registration for {user_data['username']}...")
    r = requests.post(f"{base_url}/register", json=user_data)
    print(f"Register: {r.status_code} - {r.text}")
except Exception as e:
    print(f"Register Failed: {e}")

# 3. Login
login_data = {
    "username": user_data["username"],
    "password": user_data["password"]
}

try:
    print("Attempting Login...")
    r = requests.post(f"{base_url}/login", json=login_data)
    print(f"Login: {r.status_code} - {r.text}")
except Exception as e:
    print(f"Login Failed: {e}")
