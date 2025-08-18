import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from server.database.connection import SessionLocal
from server.database.dbutils import upsert_product_price  # ✅ Import here

# Logging setup
log_dir = os.path.join(os.path.dirname(__file__), "../../logs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, "marketfoodshop_scraper.log"),
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
)

def scroll_to_bottom(driver, pause_time=1.2):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def clean_price(price_str: str) -> str:
    return price_str.replace("₦", "").replace(",", "").strip()

def get_product_name(card):
    BADGES = {"sold out", "hot", "new", "sale", "out of stock"}
    candidates = card.find_elements(By.CSS_SELECTOR, 'a[href*="/product/"]')
    for a in candidates:
        txt = a.text.strip()
        if txt and len(txt) > 2 and txt.lower() not in BADGES and "add to cart" not in txt.lower():
            return txt
    sel_list = [
        "h2.woocommerce-loop-product__title",
        "h3.woocommerce-loop-product__title",
        "h3.product-title",
        ".product-title a",
        ".product-title",
    ]
    for sel in sel_list:
        try:
            el = card.find_element(By.CSS_SELECTOR, sel)
            txt = el.text.strip()
            if txt and txt.lower() not in BADGES:
                return txt
        except Exception:
            pass
    anchors = card.find_elements(By.CSS_SELECTOR, "a")
    best = ""
    for a in anchors:
        txt = a.text.strip()
        if txt and len(txt) > len(best) and txt.lower() not in BADGES and "add to cart" not in txt.lower():
            best = txt
    return best

def get_product_price(card):
    price_text_full = ""
    try:
        bdi = card.find_element(By.CSS_SELECTOR, "span.woocommerce-Price-amount bdi")
        price_text_full = bdi.text.strip()
    except Exception:
        try:
            price_container = card.find_element(By.CSS_SELECTOR, ".price")
            price_text_full = price_container.text.strip()
        except Exception:
            price_text_full = ""
    if not price_text_full:
        return ("", None)
    cleaned = clean_price(price_text_full)
    parts = [p.strip() for p in cleaned.replace("–", "-").split() if p.strip()]
    candidate = parts[0] if parts else cleaned
    if "-" in candidate:
        low = candidate.split("-")[0].strip()
        num = float(low) if low.replace(".", "").isdigit() else None
        return (price_text_full, num)
    num = float(candidate) if candidate.replace(".", "").isdigit() else None
    return (price_text_full, num)

# --- Replace scrape_marketfoodshop with this structure ---

def scrape_marketfoodshop(session):
    options = Options()
    driver_path = os.path.join(os.path.dirname(__file__), "../../msedgedriver.exe")
    service = Service(executable_path=driver_path)
    driver = webdriver.Edge(service=service, options=options)

    base_url = "https://www.themarketfoodshop.com/shop/"
    driver.get(base_url)

    saved_count = 0
    seen_names = set()

    while True:
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.product-grid-item"))
            )
        except Exception:
            break

        scroll_to_bottom(driver, pause_time=1.0)
        product_cards = driver.find_elements(By.CSS_SELECTOR, "div.product-grid-item")
        if not product_cards:
            break

        for card in product_cards:
            try:
                name = get_product_name(card)
                if not name or name in seen_names:
                    continue
                seen_names.add(name)

                price_text, price_val = get_product_price(card)
                if price_val is None:
                    continue

                upsert_product_price(
                    session,
                    product_name=name,
                    source="MarketFoodShop",
                    price=price_val,
                    detail=price_text
                )
                saved_count += 1

            except Exception:
                continue

        try:
            next_btns = driver.find_elements(By.CSS_SELECTOR, "a.next.page-numbers")
            if next_btns:
                first_card = product_cards[0]
                driver.execute_script("arguments[0].click();", next_btns[0])
                WebDriverWait(driver, 10).until(EC.staleness_of(first_card))
                continue
            else:
                break
        except Exception:
            break

    driver.quit()
    print(f"✅ Done scraping MarketFoodShop — saved {saved_count} products.")


# --- NEW: wrapper for scheduler/CLI use ---
def run_scraper():
    session = SessionLocal()
    try:
        scrape_marketfoodshop(session)
        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    run_scraper()

