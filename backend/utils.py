from passlib.context import CryptContext
import re
import secrets
import smtplib
import os
from email.message import EmailMessage

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------- PASSWORD ----------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def is_strong_password(password: str) -> bool:
    return (
        len(password) >= 8
        and re.search(r"[A-Z]", password)
        and re.search(r"[a-z]", password)
        and re.search(r"[0-9]", password)
        and re.search(r"[!@#$%^&*]", password)
    )

# ---------- TOKEN ----------
def generate_token():
    return secrets.token_urlsafe(32)

# ---------- EMAIL ----------
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5500")

def send_reset_email(to_email: str, token: str):
    # DEV MODE (no email configured)
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print(f"[DEV MODE] Reset token for {to_email}: {token}")
        return

    reset_link = f"{FRONTEND_URL}/reset-password.html?token={token}"

    msg = EmailMessage()
    msg["Subject"] = "Skillin - Reset Password"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    msg.set_content(
        f"""
Hello,

You requested to reset your Skillin password.

Click the link below to reset your password:
{reset_link}

This link will expire in 30 minutes.

If you did not request this, please ignore this email.

– Skillin Team
"""
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
