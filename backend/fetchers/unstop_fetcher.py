# backend/fetchers/unstop_fetcher.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.orm import Session
from models import Opportunity

# Keywords to identify engineering opportunities
ENGINEERING_KEYWORDS = [
    "engineer", "developer", "software", "coding", "programming",
    "data", "machine learning", "ai", "ml", "web",
    "backend", "frontend", "python", "java",
    "cloud", "cyber", "iot", "robotics"
]

def is_engineering(title: str, description: str = ""):
    text = f"{title} {description}".lower()
    return any(word in text for word in ENGINEERING_KEYWORDS)

def fetch_from_unstop(db: Session):
    print("🔄 Fetching engineering opportunities from Unstop...")
    
    # URL for Unstop internships (can be changed for hackathons too)
    url = "https://unstop.com/internships?category=engineering"  # Example URL

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find all opportunity cards (adjust selector based on Unstop site)
        cards = soup.select(".opportunity-card")  # Example selector
        
        saved = 0
        for card in cards:
            title = card.select_one(".opportunity-title").text.strip()
            company = card.select_one(".opportunity-company").text.strip()
            deadline = card.select_one(".opportunity-deadline").text.strip()
            description = card.select_one(".opportunity-description").text.strip()
            opp_type = card.select_one(".opportunity-type").text.strip().lower()  # internship / hackathon

            if not is_engineering(title, description):
                continue

            # Skip duplicates
            exists = db.query(Opportunity).filter(
                Opportunity.title == title,
                Opportunity.company == company
            ).first()
            if exists:
                continue

            new_opp = Opportunity(
                title=title,
                company=company,
                type=opp_type,
                platform="unstop",
                deadline=deadline,
                description=description,
                source="api",
                created_at=datetime.utcnow()
            )
            db.add(new_opp)
            saved += 1

        db.commit()
        print(f"✅ {saved} engineering opportunities saved from Unstop")

    except Exception as e:
        print(f"❌ Error fetching Unstop opportunities: {e}")
