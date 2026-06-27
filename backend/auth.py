from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import base64
import hashlib
import hmac
import json
import os
import time

from database import get_db
from models import User
from schemas import UserCreate, UserLogin, ForgotPassword, ResetPassword
from utils import hash_password, verify_password, is_strong_password, generate_token, send_reset_email

router = APIRouter()
TOKEN_SECRET = os.getenv("AUTH_TOKEN_SECRET", "skillin-dev-secret-change-me")
TOKEN_TTL_SECONDS = int(os.getenv("AUTH_TOKEN_TTL_SECONDS", "86400"))


# ---------------- UTILITY FUNCTIONS ----------------
def safe_commit(db: Session):
    """Commit changes safely, rollback on error."""
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e.orig))


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


def generate_access_token(user_id: int, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": int(time.time()) + TOKEN_TTL_SECONDS,
    }
    payload_json = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_b64 = _b64url_encode(payload_json)
    signature = hmac.new(
        TOKEN_SECRET.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    sig_b64 = _b64url_encode(signature)
    return f"{payload_b64}.{sig_b64}"


def decode_access_token(token: str) -> dict:
    try:
        payload_b64, sig_b64 = token.split(".", 1)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token format")

    expected_sig = hmac.new(
        TOKEN_SECRET.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    provided_sig = _b64url_decode(sig_b64)

    if not hmac.compare_digest(expected_sig, provided_sig):
        raise HTTPException(status_code=401, detail="Invalid token signature")

    payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
    if int(payload.get("exp", 0)) < int(time.time()):
        raise HTTPException(status_code=401, detail="Token expired")
    return payload


# ---------------- REGISTER ----------------
@router.post("/register")
def register(user: UserCreate = Body(...), db: Session = Depends(get_db)):
    """
    Register a new user.
    Validates password, checks email uniqueness, returns user_id on success.
    """

    # 1. Check required fields manually
    missing_fields = [f for f, v in user.dict().items() if v is None]
    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        )

    # 2. Validate password strength
    if not is_strong_password(user.password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain uppercase, lowercase, number & special character"
        )

    # 3. Check if email already exists (pre-check)
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # 4. Create new user
    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        education=user.education,
        college_name=user.college_name,
        graduation_year=user.graduation_year
    )

    db.add(new_user)
    safe_commit(db)
    db.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user.id}


# ---------------- LOGIN ----------------
@router.post("/login")
def login(user: UserLogin = Body(...), db: Session = Depends(get_db)):
    """
    Login a user using email and password.
    Returns user_id and username on success.
    """

    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = generate_access_token(db_user.id, db_user.email)
    return {
        "message": "Login successful",
        "user_id": db_user.id,
        "username": db_user.username,
        "access_token": access_token,
        "token_type": "bearer",
    }


# ---------------- FORGOT PASSWORD ----------------
@router.post("/forgot-password")
def forgot_password(data: ForgotPassword = Body(...), db: Session = Depends(get_db)):
    """
    Generate a password reset token and send email to user.
    """

    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Email not found")

    token = generate_token()
    user.reset_token = token
    user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=30)

    safe_commit(db)
    send_reset_email(user.email, token)

    return {"message": "Password reset email sent"}


# ---------------- RESET PASSWORD ----------------
@router.post("/reset-password")
def reset_password(data: ResetPassword = Body(...), db: Session = Depends(get_db)):
    """
    Reset a user's password using a valid reset token.
    """

    user = db.query(User).filter(User.reset_token == data.token).first()

    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expired or invalid")

    if not is_strong_password(data.new_password):
        raise HTTPException(status_code=400, detail="Weak password")

    user.password = hash_password(data.new_password)
    user.reset_token = None
    user.reset_token_expiry = None

    safe_commit(db)

    return {"message": "Password reset successful"}
