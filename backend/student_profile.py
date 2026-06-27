from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import sqlite3
import os
import shutil
import uuid

# Create router with prefix
router = APIRouter(prefix="/profile", tags=["Profile"])

# Create uploads directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Pydantic model matching your frontend
class StudentProfile(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    education: Optional[str] = None
    college_name: Optional[str] = None
    graduation_year: Optional[int] = None

# Database connection
def get_db():
    conn = sqlite3.connect('skillin.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize table on startup
@router.on_event("startup")
async def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            username TEXT DEFAULT '',
            email TEXT DEFAULT '',
            education TEXT DEFAULT '',
            college_name TEXT DEFAULT '',
            graduation_year INTEGER,
            photo TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(id)
        )
    ''')
    conn.commit()
    conn.close()

# GET /profile/1 - Fetch profile
@router.get("/{user_id}")
async def get_profile(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?", (user_id,))
    student = cursor.fetchone()
    conn.close()
    
    if not student:
        # Return empty profile instead of 404
        return {
            "id": user_id,
            "username": "",
            "email": "",
            "education": "",
            "college_name": "",
            "graduation_year": None,
            "photo": None
        }
    
    return dict(student)

# PUT /profile/1 - Update profile
@router.put("/{user_id}")
async def update_profile(user_id: int, profile: StudentProfile):
    conn = get_db()
    cursor = conn.cursor()
    
    # Create if not exists
    cursor.execute("SELECT id FROM students WHERE id = ?", (user_id,))
    exists = cursor.fetchone()
    
    if not exists:
        cursor.execute('''
            INSERT INTO students 
            (id, username, email, education, college_name, graduation_year)
            VALUES (?, COALESCE(?, ''), COALESCE(?, ''), COALESCE(?, ''), 
                   COALESCE(?, ''), ?)
        ''', (user_id, profile.username, profile.email, profile.education, 
              profile.college_name, profile.graduation_year))
    else:
        # Update only provided fields
        updates = ["updated_at = CURRENT_TIMESTAMP"]
        params = [user_id]
        
        if profile.username is not None:
            updates.append("username = ?")
            params.insert(0, profile.username)
        if profile.email is not None:
            updates.append("email = ?")
            params.insert(0, profile.email)
        if profile.education is not None:
            updates.append("education = ?")
            params.insert(0, profile.education)
        if profile.college_name is not None:
            updates.append("college_name = ?")
            params.insert(0, profile.college_name)
        if profile.graduation_year is not None:
            updates.append("graduation_year = ?")
            params.insert(0, profile.graduation_year)
        
        if len(updates) > 1:
            query = f"UPDATE students SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
    
    conn.commit()
    conn.close()
    return {"message": "Profile updated successfully"}

# POST /profile/1/photo - Upload photo
@router.post("/{user_id}/photo")
async def upload_photo(user_id: int, file: UploadFile = File(...)):
    # Validate image
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Only image files allowed")
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1].lower() if file.filename else 'jpg'
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Save to database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT OR REPLACE INTO students (id, photo, updated_at) 
           VALUES (?, ?, CURRENT_TIMESTAMP)""",
        (user_id, f"uploads/{unique_filename}")
    )
    conn.commit()
    conn.close()
    
    return {"photo_url": f"uploads/{unique_filename}"}

# Serve images - FIXED ROUTE
@router.get("/uploads/{filename:path}")
async def serve_photo(filename: str):
    """Serve profile photos"""
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(
            file_path, 
            media_type='image/jpeg',
            filename=filename
        )
    raise HTTPException(status_code=404, detail="Photo not found")
