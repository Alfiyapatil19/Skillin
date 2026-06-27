import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from database import SessionLocal
from models import User
from utils import hash_password

s = SessionLocal()
try:
    u = s.query(User).filter(User.email=='system@skillin.ai').first()
    if not u:
        print('system user not found')
    else:
        new = hash_password('system')
        u.password = new
        s.commit()
        print('updated password hash to:', new)
finally:
    s.close()
