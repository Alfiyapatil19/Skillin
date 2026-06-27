import requests

BASE_URL = "http://127.0.0.1:8000/api"
failures = []
passed = 0

def api_test(name, method, url, **kwargs):
    global passed
    try:
        if method == "GET":
            res = requests.get(url, **kwargs)
        else:
            res = requests.post(url, **kwargs)
            
        if res.status_code == 200:
            print(f"✅ {name} - OK")
            passed += 1
            return res.json()
        else:
            print(f"❌ {name} - FAILED ({res.status_code}): {res.text}")
            failures.append(name)
            return None
    except Exception as e:
        print(f"❌ {name} - ERRORED: {e}")
        failures.append(name)
        return None

# 1. Login
data = api_test("Login API", "POST", f"{BASE_URL}/login", json={"email": "system@skillin.ai", "password": "system"})
auth_headers = {}
if data and data.get("access_token"):
    auth_headers = {"Authorization": f"Bearer {data['access_token']}"}

# 2. Dashboard APIs
api_test("Get Missions", "GET", f"{BASE_URL}/dashboard/missions")
api_test("Get Courses", "GET", f"{BASE_URL}/dashboard/courses/python")

# 3. AI Interview
interview = api_test(
    "Start Interview",
    "POST",
    f"{BASE_URL}/interview/start",
    json={"skill_name": "python", "difficulty": "beginner", "total_questions": 2},
    headers=auth_headers
)

if interview:
    i_id = interview["interview_id"]
    # Get question (with our new timeout fixes making it faster or falling back safely)
    q1 = api_test("Get Interview Question 1", "GET", f"{BASE_URL}/interview/question/{i_id}", headers=auth_headers)
    if q1:
        # Submit answer
        a1 = api_test(
            "Submit Answer 1",
            "POST",
            f"{BASE_URL}/interview/answer/{i_id}/{q1['question_id']}",
            json={"answer": "Object oriented programming is amazing."},
            headers=auth_headers
        )
        
        # End interview
        api_test("End Interview", "POST", f"{BASE_URL}/interview/end/{i_id}", headers=auth_headers)

print("\n----------------")
if len(failures) == 0:
    print(f"ALL {passed} APIs TESTED SUCCESSFULLY! 🎉")
else:
    print(f"{len(failures)} APIs FAILED. Check logs above.")
