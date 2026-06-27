# fetchers/linkedin_fetcher.py
import requests
from datetime import datetime
from sqlalchemy.orm import Session
from models import Opportunity

ENGINEERING_KEYWORDS = [
    "software", "developer", "engineering", "python", "java",
    "backend", "frontend", "full stack", "data", "machine learning",
    "ai", "ml", "web", "cloud", "cyber", "devops", "robotics"
]

def is_engineering(title: str, description: str = ""):
    text = f"{title} {description}".lower()
    return any(keyword in text for keyword in ENGINEERING_KEYWORDS)

def fetch_from_linkedin(db: Session):
    print("🔄 Fetching engineering opportunities from LinkedIn...")

    try:
        # Example: simulate fetching from LinkedIn API or feed
        # url = "https://linkedin.com/jobs/api/engineering"
        # response = requests.get(url, headers={"Authorization": "Bearer TOKEN"})
        # data = response.json()

        # Simulated data for now
        data = [
            {"title": "Backend Developer", "company": "Google", "type": "job", "deadline": "2026-02-28", "description": "Work on Python & Django backend services", "stipend": "₹30 LPA"},
            {"title": "HR Associate", "company": "Tech Corp", "type": "job", "deadline": "2026-03-05", "description": "Human Resources role", "stipend": "₹10 LPA"},
            {"title": "AI Engineer", "company": "Amazon", "type": "job", "deadline": "2026-03-10", "description": "Machine learning projects using Python and TensorFlow", "stipend": "₹40 LPA"}
        ]

        saved = 0
        for opp in data:
            if not is_engineering(opp["title"], opp["description"]):
                continue  # Skip non-engineering

            # Skip duplicates
            exists = db.query(Opportunity).filter(
                Opportunity.title == opp["title"],
                Opportunity.company == opp["company"],
                Opportunity.platform == "linkedin"
            ).first()

            if exists:
                continue

            new_opp = Opportunity(
                title=opp["title"],
                company=opp["company"],
                type=opp["type"],
                platform="linkedin",
                deadline=opp.get("deadline"),
                description=opp.get("description"),
                stipend=opp.get("stipend", ""),
                source="api",
                created_at=datetime.utcnow()
            )
            db.add(new_opp)
            saved += 1

        db.commit()
        print(f"✅ {saved} engineering opportunities saved from LinkedIn")

    except Exception as e:
        print("❌ Error fetching LinkedIn opportunities:", str(e))
        db.rollback()
