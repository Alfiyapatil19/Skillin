from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models import User
import os
import shutil

router = APIRouter(prefix="/profile", tags=["Student Profile"])

UPLOAD_DIR = "uploads/profile_photos"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# 📌 Get student profile (LinkedIn style)
@router.get("/{user_id}")
def get_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "education": user.education,
        "college_name": user.college_name,
        "graduation_year": user.graduation_year,
        "photo": getattr(user, "photo", None)
    }


# 📌 Update student profile (like LinkedIn edit profile)
@router.put("/{user_id}")
def update_profile(user_id: int, data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}

    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)
    user.education = data.get("education", user.education)
    user.college_name = data.get("college_name", user.college_name)
    user.graduation_year = data.get("graduation_year", user.graduation_year)

    db.commit()
    return {"message": "Profile updated successfully"}


# 📌 Upload profile photo
@router.post("/upload-photo/{user_id}")
def upload_photo(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}

    filename = f"user_{user_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save photo path in DB
    user.photo = filepath
    db.commit()

    return {"message": "Photo uploaded", "photo_url": filepath}
