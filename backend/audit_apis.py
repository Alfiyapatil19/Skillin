import requests

BASE_URL = "http://127.0.0.1:8000/api"

print("Starting API Audit...")

# 1. Test Login
print("\n--- Test Login ---")
token = None
try:
    res = requests.post(f"{BASE_URL}/login", json={"email": "system@skillin.ai", "password": "system"})
    print(f"Status: {res.status_code}, Response: {res.json()}")
    if res.status_code == 200:
        token = res.json().get("access_token")
except Exception as e:
    print(f"Error: {e}")

# 2. Test Missions
print("\n--- Test /dashboard/missions ---")
try:
    res = requests.get(f"{BASE_URL}/dashboard/missions")
    print(f"Status: {res.status_code}")
    data = res.json()
    if data.get("missions"):
        print(f"Found {len(data['missions'])} missions.")
    else:
        print(f"Response: {data}")
except Exception as e:
    print(f"Error: {e}")

# 3. Test Opportunities
print("\n--- Test /opportunities/all ---")
try:
    res = requests.get(f"{BASE_URL}/opportunities/all")
    print(f"Status: {res.status_code}")
    data = res.json()
    if isinstance(data, list):
        print(f"Found {len(data)} opportunities.")
    else:
        print(f"Response: {data}")
except Exception as e:
    print(f"Error: {e}")

# 4. Test Profile
print("\n--- Test /profile/1 ---")
try:
    res = requests.get("http://127.0.0.1:8000/profile/1")
    print(f"Status: {res.status_code}")
    # Profile API might not be prefixed with /api? Let's print raw response just in case
    print(f"Response snippet: {str(res.json())[:100]}")
except Exception as e:
    print(f"Error: {e}")

# 5. Test Interview (this used to 500)
print("\n--- Test /interview flow ---")
try:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    res = requests.post(f"{BASE_URL}/interview/start", json={"skill_name": "Test", "difficulty": "beginner", "total_questions": 1}, headers=headers)
    print(f"Start Status: {res.status_code}")
    
    if res.status_code == 200:
        session_id = res.json().get("interview_id")
        print(f"Fetching question for session {session_id}...")
        res_q = requests.get(f"{BASE_URL}/interview/question/{session_id}", headers=headers)
        print(f"Question Status: {res_q.status_code}")
        if res_q.status_code == 200 or res_q.status_code == 500:
            print(f"Response: {res_q.json()}")
except Exception as e:
    print(f"Error: {e}")

print("\nAPI Audit Complete.")
