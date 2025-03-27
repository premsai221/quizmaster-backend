import requests
import json
import time
import datetime
import random
from pprint import pprint

# Configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_USER_EMAIL = f"test{int(time.time())}@example.com"
TEST_USER_PASSWORD = "Password123!"

# For admin testing, use an existing admin user's credentials
# or create one first using the database directly
TEST_ADMIN_EMAIL = "admin@example.com"  # Replace with a valid admin email
TEST_ADMIN_PASSWORD = "AdminPass123!"    # Replace with the correct password

# Session to maintain cookies
session = requests.Session()
admin_session = requests.Session()

def print_separator(title):
    print("\n" + "="*50)
    print(f" {title} ".center(50, "="))
    print("="*50 + "\n")

def test_user_registration():
    print_separator("Testing User Registration")
    
    payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "full_name": "Test User",
        "dob": "2000-01-01",
        "qualification": "Test Qualification"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=payload)
    print(f"Registration: Status Code {response.status_code}")
    print(f"Response text: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("Registration successful!")
    else:
        print(f"Registration failed with status code: {response.status_code}")
    
    return response.status_code == 201

def test_user_login():
    print_separator("Testing User Login")
    
    payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    response = session.post(f"{BASE_URL}/auth/login", json=payload)
    print(f"Login: Status Code {response.status_code}")
    print(f"Response text: {json.dumps(response.json(), indent=2)}")
    
    # Check cookies after login
    print("Cookies received:", [cookie for cookie in session.cookies])
    
    if response.status_code == 200:
        print("Login successful! JWT cookie set in session.")
        # Print cookie details for debugging
        print("Cookie details:")
        for cookie in session.cookies:
            print(f"  {cookie.name}: {cookie.value[:10]}... (Domain: {cookie.domain}, Path: {cookie.path})")
    else:
        print(f"Login failed with status code: {response.status_code}")
    
    return response.status_code == 200

def create_admin_account():
    """Create an admin account for testing if it doesn't exist"""
    print_separator("Creating Admin Account")
    
    # First register a normal account
    admin_payload = {
        "email": TEST_ADMIN_EMAIL,
        "password": TEST_ADMIN_PASSWORD,
        "full_name": "Admin User",
        "dob": "1990-01-01",
        "qualification": "Admin Qualification"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=admin_payload)
    print(f"Admin Registration Status: {response.status_code}")
    
    if response.status_code == 201:
        print("Admin registered successfully! You need to manually update the role to 'admin' in the database.")
        print("Run this SQL command: UPDATE user SET role='admin' WHERE email='admin@example.com';")
        return True
    elif response.status_code == 400 and "already exists" in response.text:
        print("Admin account already exists")
        return True
    else:
        print(f"Failed to create admin account: {response.text}")
        return False

def test_admin_login():
    print_separator("Testing Admin Login")
    
    create_admin_account()
    
    payload = {
        "email": TEST_ADMIN_EMAIL,
        "password": TEST_ADMIN_PASSWORD
    }
    
    response = admin_session.post(f"{BASE_URL}/auth/login", json=payload)
    print(f"Admin Login: Status Code {response.status_code}")
    
    if response.status_code == 200:
        print("Admin login successful!")
        print("Cookies received:", [cookie for cookie in admin_session.cookies])
    else:
        print(f"Admin login failed with status code: {response.status_code}")
        print(f"Response: {response.text}")
    
    return response.status_code == 200

def test_get_profile():
    print_separator("Testing User Profile")
    
    # Inspect cookies before making request
    print("Cookies before request:", [cookie for cookie in session.cookies])
    
    response = session.get(f"{BASE_URL}/user/profile")
    print(f"Get Profile: Status Code {response.status_code}")
    
    if response.status_code == 200:
        print(f"Profile data retrieved successfully!")
        print(f"Response text: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Failed to get profile with status code: {response.status_code}")
        print(f"Response text: {response.text}")
    
    return response.status_code == 200

# The rest of the functions remain the same




def test_create_subject():
    print_separator("Testing Subject Creation")
    
    subject_name = f"Test Subject {int(time.time())}"
    payload = {
        "name": subject_name,
        "description": "This is a test subject created by the API test script"
    }
    
    response = admin_session.post(f"{BASE_URL}/admin/subjects", json=payload)
    print(f"Create Subject: Status Code {response.status_code}")
    print(f"Response text: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("Subject created successfully!")
        return response.json().get("subject")  # Return subject ID
    else:
        print(f"Subject creation failed with status code: {response.status_code}")
        return None

def test_create_complete_chapter(subject_id):
    print_separator("Testing Complete Chapter Creation")
    
    # Generate a timestamp for unique names
    timestamp = int(time.time())
    
    # Create test data
    payload = {
        "chapter": {
            "name": f"Test Chapter {timestamp}",
            "description": "This is a test chapter with integrated quiz and questions"
        },
        "quiz": {
            "date_of_quiz": (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"),
            "time_duration": 60,
            "remarks": "Test quiz created via API test"
        },
        "questions": [
            {
                "question_statement": "What is 2 + 2?",
                "option1": "3",
                "option2": "4",
                "option3": "5",
                "option4": "6",
                "correct_option": 2
            },
            {
                "question_statement": "Which color is the sky?",
                "option1": "Red",
                "option2": "Green",
                "option3": "Blue",
                "option4": "Yellow",
                "correct_option": 3
            },
            {
                "question_statement": "What is the capital of France?",
                "option1": "London",
                "option2": "Berlin",
                "option3": "Madrid",
                "option4": "Paris",
                "correct_option": 4
            }
        ]
    }
    
    response = admin_session.post(f"{BASE_URL}/admin/subjects/{subject_id}/complete-chapter", json=payload)
    print(f"Create Complete Chapter: Status Code {response.status_code}")
    print(f"Response text: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("Chapter with quiz and questions created successfully!")
        return response.json()
    else:
        print(f"Chapter creation failed with status code: {response.status_code}")
        return None

def test_get_subjects():
    print_separator("Testing Get Subjects")
    
    response = session.get(f"{BASE_URL}/quiz/subjects")
    print(f"Get Subjects: Status Code {response.status_code}")
    
    if response.status_code == 200:
        subjects = response.json().get("subjects", [])
        print(f"Retrieved {len(subjects)} subjects")
        if subjects:
            print("Sample subject:")
            pprint(subjects[0])
        return subjects
    else:
        print(f"Failed to get subjects with status code: {response.status_code}")
        return []

def test_get_chapters(subject_id):
    print_separator(f"Testing Get Chapters for Subject {subject_id}")
    
    response = session.get(f"{BASE_URL}/quiz/subjects/{subject_id}/chapters")
    print(f"Get Chapters: Status Code {response.status_code}")
    
    if response.status_code == 200:
        chapters = response.json().get("chapters", [])
        print(f"Retrieved {len(chapters)} chapters")
        if chapters:
            print("Sample chapter:")
            pprint(chapters[0])
        return chapters
    else:
        print(f"Failed to get chapters with status code: {response.status_code}")
        return []

def test_get_user_scores():
    print_separator("Testing Get User Scores")
    
    response = session.get(f"{BASE_URL}/user/scores")
    print(f"Get User Scores: Status Code {response.status_code}")
    
    if response.status_code == 200:
        print(f"Response text: {json.dumps(response.json(), indent=2)}")
        return response.json()
    else:
        print(f"Failed to get scores with status code: {response.status_code}")
        return None

def test_get_admin_users_list():
    print_separator("Testing Admin Users List")
    
    response = admin_session.get(f"{BASE_URL}/admin/users")
    print(f"Get Users List: Status Code {response.status_code}")
    
    if response.status_code == 200:
        users = response.json().get("users", [])
        print(f"Retrieved {len(users)} users")
        if users:
            print("Sample users (up to 3):")
            for user in users[:3]:
                pprint(user)
        return users
    else:
        print(f"Failed to get users list with status code: {response.status_code}")
        return []

def test_admin_scores_endpoint():
    print_separator("Testing Admin Scores Endpoint")
    
    # First, get a subject
    subjects = test_get_subjects()
    if not subjects:
        print("No subjects available for testing scores endpoint")
        return
    
    subject_id = subjects[0]['id']
    
    # Get chapters for the subject
    chapters = test_get_chapters(subject_id)
    if not chapters:
        print("No chapters available for testing scores endpoint")
        return
    
    chapter_id = chapters[0]['id']
    
    # Test scores by chapter
    response = admin_session.get(f"{BASE_URL}/admin/scores?chapter_id={chapter_id}")
    print(f"Get Scores by Chapter: Status Code {response.status_code}")
    
    if response.status_code == 200:
        scores_data = response.json()
        print(f"Retrieved scores for chapter {chapter_id}")
        print(f"Total attempts: {scores_data.get('total_attempts', 0)}")
        print(f"Average percentage: {scores_data.get('average_percentage', 0)}%")
    else:
        print(f"Failed to get scores by chapter with status code: {response.status_code}")
def run_all_tests():
    print_separator("Starting API Testing")
    print(f"Base URL: {BASE_URL}")
    
    # Test registration and authentication
    registration_successful = test_user_registration()
    if not registration_successful:
        print("Registration failed, using existing user credentials for login.")
    
    login_successful = test_user_login()
    if not login_successful:
        print("Login failed. Cannot proceed with user tests.")
        return
    
    # Test profile retrieval
    test_get_profile()
    
    # Test admin functionality
    admin_login_successful = test_admin_login()
    if not admin_login_successful:
        print("Admin login failed. Cannot proceed with admin tests.")
        return
    # Test subject creation
    subject_id = test_create_subject()
    if subject_id:
        # Test the combined chapter creation endpoint
        chapter_result = test_create_complete_chapter(subject_id)
        
        # Test getting subjects and chapters
        subjects = test_get_subjects()
        if subjects:
            for subject in subjects[:2]:  # Test first 2 subjects
                test_get_chapters(subject['id'])
    
    # Test scores endpoints
    test_get_user_scores()
    test_admin_scores_endpoint()
    
    # Test admin users list
    test_get_admin_users_list()
    
    print_separator("API Testing Complete")

if __name__ == "__main__":
    run_all_tests()