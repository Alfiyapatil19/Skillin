import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apscheduler.schedulers.blocking import BlockingScheduler
from database import SessionLocal

from fetchers.unstop_fetcher import fetch_from_unstop
from fetchers.internshala_fetcher import fetch_from_internshala
from fetchers.government_fetcher import fetch_government_opportunities # pyright: ignore[reportMissingImports]
from fetchers.fetch_hackathons import fetch_unstop_hackathons


def fetch_all_opportunities():
    print("🚀 Starting automatic opportunity fetch process...")
    db = SessionLocal()
    try:
        fetch_from_unstop(db)
        fetch_from_internshala(db)
        fetch_government_opportunities(db)
        fetch_unstop_hackathons(db)
        print("🎯 All engineering opportunities fetched successfully!")
    except Exception as e:
        print(f"❌ Error while fetching opportunities: {e}")
    finally:
        db.close()
        print("🔒 Database session closed.")


scheduler = BlockingScheduler()

# Run every day at 2 AM
scheduler.add_job(fetch_all_opportunities, 'cron', hour=2, minute=0)

print("⏳ Scheduler started. Waiting for next run...")
scheduler.start()
