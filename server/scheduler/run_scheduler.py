import os
import sys
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

# Ensure Python can find your scrapers folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Import your scrapers
from scrapers import packnpaypro, pricepally, marketfoodshop 

def run_all_scrapers():
    print(f"\n=== Scheduler started at {datetime.utcnow()} UTC ===\n")

    try:
        print("Running PacknPay scraper...")
        packnpaypro.run_scraper()
        print("✅ PacknPayPro scraper finished.\n")
    except Exception as e:
        print(f"❌ Error running PacknPay scraper: {e}")

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
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(run_all_scrapers, "interval", hours=6)  # every 6 hours
    scheduler.start()
    print("APScheduler started. Scrapers will run every 6 hours.")

    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler stopped.")


if __name__ == "__main__":
    # Change between one-time run or continuous scheduler
    MODE = "scheduler"  # "once" or "scheduler"

    if MODE == "once":
        run_all_scrapers()
    else:
        start_scheduler()
