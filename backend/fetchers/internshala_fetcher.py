# fetchers/internshala_fetcher.py
import requests
from datetime import datetime
from sqlalchemy.orm import Session
from models import Opportunity

ENGINEERING_KEYWORDS = [
    "software", "developer", "engineering", "data", "python",
    "machine learning", "ai", "backend", "frontend", "web",
    "cloud", "cyber", "devops", "robotics"
]

def is_engineering(title: str, desc: str = ""):
    text = f"{title} {desc}".lower()
    return any(keyword in text for keyword in ENGINEERING_KEYWORDS)

def fetch_from_internshala(db: Session):
    print("🔄 Fetching engineering opportunities from Internshala...")

    try:
        # Example: simulate fetching from an endpoint
        # url = "https://internshala.com/api/v1/internships?category=engineering"
        # response = requests.get(url)
        # data = response.json()
        
        # For now, simulated data
        data = [
            {"title": "Python Developer Intern", "company": "Tech Solutions", "type": "internship", "deadline": "2026-02-20", "description": "Backend APIs with FastAPI"},
            {"title": "Marketing Intern", "company": "Brand Corp", "type": "internship", "deadline": "2026-02-22", "description": "Non technical role"},
            {"title": "AI Intern", "company": "Innovate AI", "type": "internship", "deadline": "2026-03-05", "description": "Work on ML models and data pipelines"}
        ]

        saved = 0
        for opp in data:
            # Only engineering
            if not is_engineering(opp["title"], opp["description"]):
                continue

            # Skip duplicates
            exists = db.query(Opportunity).filter(
                Opportunity.title == opp["title"],
                Opportunity.company == opp["company"],
                Opportunity.platform == "internshala"
            ).first()

            if exists:
                continue

            new_opp = Opportunity(
                title=opp["title"],
                company=opp["company"],
                type=opp["type"],
                platform="internshala",
                deadline=opp.get("deadline"),
                description=opp.get("description"),
                stipend=opp.get("stipend", ""),
                source="api",
                created_at=datetime.utcnow()
            )
            db.add(new_opp)
            saved += 1

        db.commit()
        print(f"✅ {saved} engineering opportunities saved from Internshala")

    except Exception as e:
        print("❌ Error fetching Internshala opportunities:", str(e))
        db.rollback()
