from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, StudentSkill, Project, Score
from schemas import Profile, SkillBase, ProjectBase

router = APIRouter()

# Dependency to get DB session
def get_db_session():
    db = next(get_db())
    return db

# ----------------- GET STUDENT PROFILE -----------------
@router.get("/{student_id}", response_model=Profile)
def get_profile(student_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == student_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Map skills
    skills = []
    for s in user.skills:
        skills.append(SkillBase(
            name=s.skill.name,
            level=s.level,
            score=s.score
        ))
    
    # Map projects
    projects = []
    for p in user.projects:
        projects.append(ProjectBase(
            title=p.title,
            description=p.description,
            github_link=p.github_link,
            live_demo_link=p.live_demo_link,
            verified=p.verified
        ))
    
    # Skillin score
    skillin_score = user.scores.total_score if user.scores else 0

    return Profile(
        username=user.name,
        email=user.email,
        education=user.education if hasattr(user, "education") else "",
        college_name=user.college if hasattr(user, "college") else "",
        graduation_year=user.year if hasattr(user, "year") else 0,
        profile_pic_url=user.profile_pic_url,
        skills=skills,
        projects=projects,
        skillin_score=skillin_score
    )
