from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import get_db
from models import User
from schemas import (
    UserCreate,
    UserLogin,
    ForgotPassword,
    ResetPassword
)
from utils import (
    hash_password,
    verify_password,
    is_strong_password,
    generate_token,
    send_reset_email
)

router = APIRouter()

# ---------------- REGISTER ----------------
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    if not is_strong_password(user.password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain uppercase, lowercase, number & special character"
        )

    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        education=user.education,
        college_name=user.college_name,
        graduation_year=user.graduation_year
    )

    db.add(new_user)
    db.commit()

    return {"message": "User registered successfully"}

# ---------------- LOGIN ----------------
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    return {
        "message": "Login successful",
        "user_id": db_user.id,
        "username": db_user.username
    }

# ---------------- FORGOT PASSWORD ----------------
@router.post("/forgot-password")
def forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Email not found")

    token = generate_token()
    user.reset_token = token
    user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=30)

    db.commit()

    send_reset_email(user.email, token)

    return {"message": "Password reset email sent"}

# ---------------- RESET PASSWORD ----------------
@router.post("/reset-password")
def reset_password(data: ResetPassword, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.reset_token == data.token).first()

    if not user or user.reset_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expired or invalid")

    if not is_strong_password(data.new_password):
        raise HTTPException(status_code=400, detail="Weak password")

    user.password = hash_password(data.new_password)
    user.reset_token = None
    user.reset_token_expiry = None

    db.commit()

    return {"message": "Password reset successful"}
 