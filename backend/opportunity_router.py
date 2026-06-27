from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Opportunity
from schemas import OpportunityResponse

router = APIRouter(prefix="/api/opportunities", tags=["Opportunities"])


# 🔹 ALL Opportunities (Latest first)
@router.get("/all", response_model=List[OpportunityResponse])
def get_all_opportunities(db: Session = Depends(get_db)):
    return db.query(Opportunity).order_by(Opportunity.created_at.desc()).all()


# 🔹 JOBS
@router.get("/jobs", response_model=List[OpportunityResponse])
def get_jobs(db: Session = Depends(get_db)):
    return db.query(Opportunity)\
        .filter(Opportunity.type == "job")\
        .order_by(Opportunity.created_at.desc())\
        .all()


# 🔹 INTERNSHIPS
@router.get("/internships", response_model=List[OpportunityResponse])
def get_internships(db: Session = Depends(get_db)):
    return db.query(Opportunity)\
        .filter(Opportunity.type == "internship")\
        .order_by(Opportunity.created_at.desc())\
        .all()


# 🔹 HACKATHONS
@router.get("/hackathons", response_model=List[OpportunityResponse])
def get_hackathons(db: Session = Depends(get_db)):
    return db.query(Opportunity)\
        .filter(Opportunity.type == "hackathon")\
        .order_by(Opportunity.created_at.desc())\
        .all()


# 🔹 WORKSHOPS (optional but powerful)
@router.get("/workshops", response_model=List[OpportunityResponse])
def get_workshops(db: Session = Depends(get_db)):
    return db.query(Opportunity)\
        .filter(Opportunity.type == "workshop")\
        .order_by(Opportunity.created_at.desc())\
        .all()
