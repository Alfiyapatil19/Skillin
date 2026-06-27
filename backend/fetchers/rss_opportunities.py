import feedparser
import requests
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from sqlalchemy.orm import Session
from models import Opportunity
import time
import random

ENGINEERING_KEYWORDS = [
    "python", "developer", "software", "engineer", "web", "data", 
    "ai", "ml", "backend", "frontend", "cloud", "devops", "hackathon"
]

def is_engineering_relevant(title: str, description: str = "") -> bool:
    text = f"{title} {description}".lower()
    return any(keyword in text for keyword in ENGINEERING_KEYWORDS)

def parse_date(date_str: str) -> str:
    """Convert various date formats to YYYY-MM-DD"""
    if not date_str:
        return (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    try:
        return date_parser.parse(date_str).strftime("%Y-%m-%d")
    except:
        return (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

def fetch_wellfound_jobs(db: Session):
    """Wellfound (ex-AngelList) RSS - Perfect for startups"""
    print("🔄 Fetching Wellfound jobs...")
    
    # Wellfound RSS feeds (tech/startup focused)
    rss_feeds = [
        "https://wellfound.com/jobs.rss?category=development",
        "https://wellfound.com/jobs.rss?location=Pune",
        "https://wellfound.com/jobs.rss?category=design"
    ]
    
    saved = 0
    for url in rss_feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:
                if is_engineering_relevant(entry.title, entry.get('summary', '')):
                    exists = db.query(Opportunity).filter(
                        Opportunity.title == entry.title,
                        Opportunity.platform == "wellfound"
                    ).first()
                    
                    if not exists:
                        opp = Opportunity(
                            title=entry.title[:200],
                            company=entry.get('author', 'Wellfound'),
                            type='job',
                            platform='wellfound',
                            deadline=parse_date(entry.get('published')),
                            description=entry.get('summary', '')[:500],
                            source='rss',
                            created_at=datetime.utcnow()
                        )
                        db.add(opp)
                        saved += 1
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            print(f"⚠️ Wellfound feed error: {e}")
            continue
    
    return saved

def fetch_devto_jobs(db: Session):
    """DEV Community Job Board RSS"""
    print("🔄 Fetching DEV.to jobs...")
    
    rss_url = "https://dev.to/feed/tag/jobs"
    try:
        feed = feedparser.parse(rss_url)
        saved = 0
        
        for entry in feed.entries[:10]:
            if is_engineering_relevant(entry.title, entry.summary):
                exists = db.query(Opportunity).filter(
                    Opportunity.title == entry.title,
                    Opportunity.platform == "devto"
                ).first()
                
                if not exists:
                    opp = Opportunity(
                        title=entry.title[:200],
                        company="DEV Community",
                        type='job',
                        platform='devto',
                        deadline=parse_date(entry.get('published')),
                        description=entry.summary[:500],
                        source='rss',
                        created_at=datetime.utcnow()
                    )
                    db.add(opp)
                    saved += 1
        
        return saved
    except Exception as e:
        print(f"⚠️ DEV.to error: {e}")
        return 0

def fetch_pune_startup_jobs(db: Session):
    """Pune-specific startup jobs"""
    print("🔄 Fetching Pune startup jobs...")
    
    # Pune job boards + startup RSS
    pune_sources = [
        "https://punejobboard.com/feed",
        "https://startuphrtoolkit.com/feed/",
        # Add more local feeds
    ]
    
    saved = 0
    for url in pune_sources:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:8]:
                if any(word in entry.title.lower() for word in ["pune", "intern", "developer"]):
                    exists = db.query(Opportunity).filter(
                        Opportunity.title == entry.title,
                        Opportunity.platform == "pune"
                    ).first()
                    
                    if not exists:
                        opp = Opportunity(
                            title=entry.title[:200],
                            company="Pune Startups",
                            type='job',
                            platform='pune',
                            deadline=parse_date(entry.get('published')),
                            description=entry.summary[:500],
                            source='rss',
                            created_at=datetime.utcnow()
                        )
                        db.add(opp)
                        saved += 1
        except:
            continue
    
    return saved

def fetch_github_jobs(db: Session):
    """GitHub Jobs Archive (legacy but still useful)"""
    print("🔄 Fetching GitHub engineering jobs...")
    
    # GitHub Jobs RSS (if available) or alternative
    github_rss = "https://jobs.github.com/positions.rss?description=python&location=india"
    try:
        feed = feedparser.parse(github_rss)
        saved = 0
        
        for entry in feed.entries[:10]:
            if is_engineering_relevant(entry.title):
                exists = db.query(Opportunity).filter(
                    Opportunity.title == entry.title,
                    Opportunity.platform == "github"
                ).first()
                
                if not exists:
                    opp = Opportunity(
                        title=entry.title[:200],
                        company=entry.author,
                        type='job',
                        platform='github',
                        deadline=parse_date(entry.get('published')),
                        description=entry.summary[:500],
                        source='rss',
                        created_at=datetime.utcnow()
                    )
                    db.add(opp)
                    saved += 1
        
        return saved
    except Exception as e:
        print(f"⚠️ GitHub jobs error: {e}")
        return 0

def fetch_all_opportunities(db: Session):
    """Master function - fetches from ALL sources"""
    print("🚀 Starting Skillin Opportunity Fetch...")
    
    total_saved = 0
    db.execute("DELETE FROM opportunity WHERE created_at < NOW() - INTERVAL '7 days'")  # Cleanup old
    
    # Run all fetchers
    total_saved += fetch_wellfound_jobs(db)
    time.sleep(2)
    total_saved += fetch_devto_jobs(db)
    time.sleep(2)
    total_saved += fetch_pune_startup_jobs(db)
    time.sleep(2)
    total_saved += fetch_github_jobs(db)
    
    db.commit()
    print(f"🎉 TOTAL: {total_saved} NEW opportunities saved!")
    return total_saved
