import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from database.connection import SessionLocal
from scrapers.pricepally import scrape_pricepally

db: Session = SessionLocal()
scrape_pricepally(db)
db.close()
