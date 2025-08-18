import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy.orm import Session
from database.connection import SessionLocal  # ✅ Added so run_scraper works alone
from database.db_utils import upsert_product_price

# ========== SETUP LOGGING ==========
log_dir = os.path.join(os.path.dirname(__file__), "../../logs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, "pricepally_scraper.log"),
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
)
# ===================================

def scroll_to_bottom(driver, pause_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def clean_price(price_str):
    return price_str.replace("₦", "").replace(",", "").strip()

def scrape_pricepally(session: Session):
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")

    driver_path = os.path.join(os.path.dirname(__file__), "../../msedgedriver.exe")
    service = Service(executable_path=driver_path)
    driver = webdriver.Edge(service=service, options=options)

    seen_names = set()
    MAX_PAGES = 30

    for page in range(1, MAX_PAGES + 1):
        url = f"https://www.pricepally.com/shop?page={page}"
        print(f"\n🌐 Visiting {url}")
        logging.info(f"Visiting {url}")
        driver.get(url)
        time.sleep(3)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.product-grid li"))
            )
        except Exception as e:
            msg = "[!] Timeout or no products found. Stopping."
            print(msg)
            logging.warning(msg + f" Error: {e}")
            break

        product_cards = driver.find_elements(By.CSS_SELECTOR, "ul.product-grid li")
        if not product_cards:
            msg = "[!] No products on this page. Ending scrape."
            print(msg)
            logging.warning(msg)
            break

        print(f"[ℹ️] Found {len(product_cards)} products on page {page}")
        logging.info(f"Found {len(product_cards)} products on page {page}")

        for i, card in enumerate(product_cards):
            try:
                time.sleep(0.5)

                name_elem = card.find_element(By.CSS_SELECTOR, "p.text-base-dark.font-semibold")
                name = name_elem.text.strip()

                if name in seen_names:
                    continue
                seen_names.add(name)

                price_div = card.find_element(By.CSS_SELECTOR, "div.flex.items-center.gap-x-2.mt-2")
                full_price_text = price_div.text.strip()

                if not full_price_text or "₦" not in full_price_text:
                    msg = f"[!] Skipped {name} — price not found"
                    print(msg)
                    logging.warning(msg)
                    continue

                if "-" in full_price_text:
                    low_raw, high_raw = full_price_text.split("-")
                    low = clean_price(low_raw)
                    high = clean_price(high_raw)
                    price_value = float(low) if low.replace(".", "").isdigit() else None
                    price_text = f"₦{low} - ₦{high}"
                else:
                    low = clean_price(full_price_text)
                    price_value = float(low) if low.replace(".", "").isdigit() else None
                    price_text = f"₦{low}"

                if not price_value:
                    msg = f"[!] Skipped {name} — invalid price format"
                    print(msg)
                    logging.warning(msg)
                    continue

                upsert_product_price(
                    session,
                    product_name=name,
                    source="PricePally",
                    price=price_value,
                    detail=price_text
                )

                msg = f"[✔] Upserted {name} — {price_text}"
                print(msg)
                logging.info(msg)

            except Exception as e:
                msg = f"[!] Error scraping product {i + 1}: {e}"
                print(msg)
                logging.error(msg)
                continue

    driver.quit()
    print("\n✅ Done scraping all PricePally pages.")
    logging.info("Done scraping all PricePally pages.")

# ✅ New wrapper function
def run_scraper():
    session = SessionLocal()
    try:
        scrape_pricepally(session)
    finally:
        session.close()

if __name__ == "__main__":
    run_scraper()
