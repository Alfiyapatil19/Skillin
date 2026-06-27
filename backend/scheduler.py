from apscheduler.schedulers.background import BackgroundScheduler
from fetch_all_opportunities import fetch_all_opportunities

scheduler = BackgroundScheduler()
scheduler.add_job(fetch_all_opportunities, "interval", hours=24)
scheduler.start()

print("🕒 Opportunity auto-fetch scheduler started")
