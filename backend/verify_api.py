import requests

API_URL = "http://127.0.0.1:8008"

def verify_flow():
    session = requests.Session()
    username = "verify_user"
    password = "verify_password"
    
    # 1. Register
    print("Testing /register...")
    reg_data = {
        "username": username,
        "email": "verify@example.com",
        "password": password,
        "phone": "0000000000"
    }
    r = requests.post(f"{API_URL}/register", json=reg_data)
    try:
        print(f"Register status: {r.status_code}, Response: {r.json()}")
    except:
        print(f"Register status: {r.status_code}, Response Text: {r.text[:500]}")
    
    # Allow for user already existing
    if r.status_code != 200 and "already registered" not in r.text.lower():
        return False

    # 2. Login
    print("\nTesting /login...")
    login_data = {"username": username, "password": password}
    r = session.post(f"{API_URL}/login", json=login_data)
    try:
        print(f"Login status: {r.status_code}, Response: {r.json()}")
    except:
        print(f"Login status: {r.status_code}, Response Text: {r.text[:500]}")
    print(f"Cookie received: {session.cookies.get('access_token')}")
    
    if r.status_code != 200:
        return False

    # 3. Balance
    print("\nTesting /balance...")
    r = session.get(f"{API_URL}/balance")
    try:
        print(f"Balance status: {r.status_code}, Response: {r.json()}")
    except:
        print(f"Balance status: {r.status_code}, Response Text: {r.text[:500]}")
    
    if r.status_code == 200 and r.json().get("balance") == 100000.0:
        print("\nFULL FLOW VERIFIED SUCCESSFULLY!")
        return True
    else:
        print("\nVerification FAILED!")
        return False

if __name__ == "__main__":
    verify_flow()
