import requests
import json
from datetime import datetime

BASE_URL = 'http://127.0.0.1:5000'

def test_registration():
    print("Testing user registration...")
    # Use a unique email with timestamp to avoid conflicts
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    email = f"test{timestamp}@example.com"
    
    reg_data = {
        "email": email,
        "password": "test123",
        "full_name": "Test User",
        "qualification": "Test Qualification",
        "dob": "2000-01-01"  # This will be converted to date object in the API
    }
    
    try:
        response = requests.post(f'{BASE_URL}/auth/register', json=reg_data)
        print(f"Registration: Status Code {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.text:
            try:
                json_data = response.json()
                print(f"Registration JSON response: {json_data}")
                if response.status_code == 201:
                    print("Registration successful!")
                    return email, "test123"
                else:
                    print(f"Registration failed: {json_data.get('error', 'Unknown error')}")
                    return None, None
            except json.JSONDecodeError:
                print("Error: Response is not valid JSON")
                return None, None
    except requests.exceptions.ConnectionError:
        print(f"Connection error: Could not connect to {BASE_URL}")
        return None, None

def test_login(email, password):
    print(f"\nTesting login with {email}...")
    if not email or not password:
        print("No credentials available. Skipping login test.")
        return None
        
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
        print(f"Login: Status Code {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.text:
            try:
                json_response = response.json()
                print(f"Login response: {json_response}")
                if response.status_code == 200:
                    token = json_response.get('access_token')
                    print(f"Login successful! Token obtained.")
                    return token
                else:
                    print(f"Login failed: {json_response.get('error', 'Unknown error')}")
            except json.JSONDecodeError:
                print("Error: Response is not valid JSON")
    except requests.exceptions.ConnectionError:
        print(f"Connection error: Could not connect to {BASE_URL}")
    
    return None

def test_admin_login():
    print("\nTesting admin login...")
    login_data = {
        "email": "admin@quizmaster.com",
        "password": "admin123"  # Default admin password we set
    }
    
    try:
        response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
        print(f"Admin Login: Status Code {response.status_code}")
        
        if response.text:
            try:
                json_response = response.json()
                if response.status_code == 200:
                    token = json_response.get('access_token')
                    print("Admin login successful!")
                    return token
                else:
                    print(f"Admin login failed: {json_response.get('error', 'Unknown error')}")
            except json.JSONDecodeError:
                print("Error: Response is not valid JSON")
    except requests.exceptions.ConnectionError:
        print(f"Connection error: Could not connect to {BASE_URL}")
    
    return None

def test_subject_creation(admin_token):
    print("\nTesting subject creation...")
    if not admin_token:
        print("No admin token available. Skipping subject creation test.")
        return
        
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    # Create a unique subject name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    subject_data = {
        "name": f"Test Subject {timestamp}",
        "description": "A test subject for testing"
    }
    
    try:
        response = requests.post(f'{BASE_URL}/admin/subjects', json=subject_data, headers=headers)
        print(f"Create Subject: Status Code {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.text:
            try:
                json_response = response.json()
                print(f"Subject creation response: {json_response}")
                if response.status_code == 201:
                    print("Subject created successfully!")
                    return json_response.get('subject')
                else:
                    print(f"Subject creation failed: {json_response.get('error', 'Unknown error')}")
            except json.JSONDecodeError:
                print("Error: Response is not valid JSON")
    except requests.exceptions.ConnectionError:
        print(f"Connection error: Could not connect to {BASE_URL}")
    
    return None

def test_profile(token):
    print("\nTesting user profile...")
    if not token:
        print("No token available. Skipping profile test.")
        return
        
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(f'{BASE_URL}/user/profile', headers=headers)
        print(f"Get Profile: Status Code {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.text:
            try:
                json_response = response.json()
                print(f"Profile data: {json_response}")
            except json.JSONDecodeError:
                print("Error: Response is not valid JSON")
    except requests.exceptions.ConnectionError:
        print(f"Connection error: Could not connect to {BASE_URL}")

if __name__ == "__main__":
    print("Starting API testing...")
    print(f"Base URL: {BASE_URL}")
    
    # Test user registration and login
    email, password = test_registration()
    user_token = test_login(email, password)
    
    # Test admin login
    admin_token = test_admin_login()
    
    # Test profile endpoint with user token
    if user_token:
        test_profile(user_token)
    
    # Test subject creation with admin token
    if admin_token:
        subject_id = test_subject_creation(admin_token)