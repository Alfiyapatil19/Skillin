import requests
r = requests.get('http://127.0.0.1:8000')
print('health', r.status_code, r.text)
r2 = requests.post('http://127.0.0.1:8000/api/login', json={'email':'system@skillin.ai','password':'system'})
print('login', r2.status_code, r2.text)
