# routers/opportunities.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_, desc
from datetime import datetime, date
from database import get_db
from models import Opportunity

router = APIRouter(prefix="/api", tags=["opportunities"])

@router.get("/opportunities")
async def get_opportunities(
    skill: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Opportunity).filter(
        Opportunity.deadline > datetime.now()
    ).order_by(desc(Opportunity.created_at))
    
    if skill:
        query = query.filter(
            or_(
                Opportunity.title.ilike(f"%{skill}%"),
                Opportunity.description.ilike(f"%{skill}%")
            )
        )
    return query.limit(limit).all()

@router.get("/opportunities/count")
async def get_opportunity_count(db: Session = Depends(get_db)):
    today = db.query(Opportunity).filter(
        Opportunity.created_at >= datetime.now().replace(tzinfo=None).date()
    ).count()
    
    total = db.query(Opportunity).filter(
        Opportunity.deadline > datetime.now()
    ).count()
    
    return {"today": today, "total": total, "fresh": today > 0}
