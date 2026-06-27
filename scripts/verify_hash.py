from passlib.context import CryptContext
h = '$2b$12$RsdrbtsarK/w7p/LJsc7IuDR3BFo2tFuxsUvv8eNngI3dWFu851Wu'
ctx = CryptContext(schemes=['bcrypt'], deprecated='auto')
print('identify', ctx.identify(h))
print('verify', ctx.verify('system', h))
