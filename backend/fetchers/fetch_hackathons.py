# fetch_hackathons.py
import requests
from sqlalchemy.orm import Session
from models import Opportunity
from datetime import datetime

ENGINEERING_KEYWORDS = [
    "engineering", "developer", "software", "web", "ai", "ml",
    "data", "cloud", "python", "java", "hackathon", "coding"
]

def is_engineering_related(title: str, description: str = ""):
    text = f"{title} {description}".lower()
    return any(keyword in text for keyword in ENGINEERING_KEYWORDS)


def fetch_unstop_hackathons(db: Session):
    print("🔄 Fetching engineering hackathons from Unstop...")

    # ⚠️ Unstop doesn’t provide a free public API
    # So we simulate it first. Later we can replace with scraping/API.

    sample_hackathons = [
        {
            "title": "National AI Hackathon 2026",
            "company": "Unstop",
            "type": "hackathon",
            "platform": "unstop",
            "deadline": "2026-03-10",
            "description": "AI and ML based engineering hackathon",
            "stipend": "Prize Pool ₹5,00,000"
        },
        {
            "title": "Web3 Builders Challenge",
            "company": "Unstop",
            "type": "hackathon",
            "platform": "unstop",
            "deadline": "2026-03-15",
            "description": "Blockchain engineering hackathon",
            "stipend": "Prize Pool ₹3,00,000"
        }
    ]

    count = 0
    for hack in sample_hackathons:
        if not is_engineering_related(hack["title"], hack["description"]):
            continue

        exists = db.query(Opportunity).filter(
            Opportunity.title == hack["title"],
            Opportunity.company == hack["company"]
        ).first()

        if exists:
            continue

        new_opp = Opportunity(
            title=hack["title"],
            company=hack["company"],
            type="hackathon",
            platform="unstop",
            deadline=hack["deadline"],
            description=hack["description"],
            stipend=hack["stipend"],
            source="api",
            created_at=datetime.utcnow()
        )

        db.add(new_opp)
        count += 1

    db.commit()
    print(f"✅ {count} engineering hackathons saved from Unstop")
