from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=8)
    education: str
    college_name: str
    graduation_year: int

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str = Field(min_length=8)

from typing import List, Optional

# ----------------- Profile Schemas -----------------
class SkillBase(BaseModel):
    name: str
    level: Optional[str] = None
    score: Optional[int] = 0

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    github_link: Optional[str] = None
    live_demo_link: Optional[str] = None
    verified: bool = False

class Profile(BaseModel):
    username: str
    email: EmailStr
    education: Optional[str] = None
    college_name: Optional[str] = None
    graduation_year: Optional[int] = None
    profile_pic_url: Optional[str] = None
    skills: List[SkillBase] = []
    projects: List[ProjectBase] = []
    skillin_score: Optional[int] = 0
