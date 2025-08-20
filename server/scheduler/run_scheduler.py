import os
import sys
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

# Ensure Python can find your scrapers folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Import your scrapers
from scrapers import osusubuy, pricepally, marketfoodshop


def run_all_scrapers():
    """Run all scrapers once."""
    print(f"\n=== Scheduler started at {datetime.utcnow()} UTC ===\n")

    try:
        print("Running OsusuBuy scraper...")
        osusubuy.run_scraper()
        print("✅ OsusuBuy scraper finished.\n")
    except Exception as e:
        print(f"❌ Error running OsusuBuy scraper: {e}")

    try:
        print("Running PricePally scraper...")
        pricepally.run_scraper()
        print("✅ PricePally scraper finished.\n")
    except Exception as e:
        print(f"❌ Error running PricePally scraper: {e}")
        
    try:
        print("Running Market Food Shop scraper...")
        marketfoodshop.run_scraper()
        print("✅ Market Food Shop scraper finished.\n")
    except Exception as e:
        print(f"❌ Error running Market Food Shop scraper: {e}")

    print(f"=== Scheduler finished at {datetime.utcnow()} UTC ===\n")


def start_scheduler():
    """Start APScheduler to run scrapers every 6 hours in the background."""
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(run_all_scrapers, "interval", hours=6)  # every 6 hours
    scheduler.start()
    print("✅ APScheduler started. Scrapers will run every 6 hours.")
    return scheduler
