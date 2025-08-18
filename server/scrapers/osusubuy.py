'''
from server.database.connection import SessionLocal
from server.database.dbutils import upsert_product_price  # central upsert
from datetime import datetime
import os, time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException
)


def scrape_packnpaypro(session):
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")

    driver_path = os.path.join(os.path.dirname(__file__), "../../msedgedriver.exe")
    service = Service(executable_path=driver_path)
    driver = webdriver.Edge(service=service, options=options)

    print("Opening PacknPay...")
    driver.get("https://pro.packnpay.com.ng/shop/") 
    time.sleep(5)

    seen_names = set()

    try:
        while True:
            print("Scraping products...")
            products = driver.find_elements(By.CSS_SELECTOR, ".product-card")
            print(f"Found {len(products)} products on page.")

            for idx, product in enumerate(products, start=1):
                try:
                    name = product.find_element(By.CSS_SELECTOR, "h2.elementor-heading-title").text.strip()
                    price_text = product.find_element(By.CSS_SELECTOR, ".woocommerce-Price-amount bdi").text.strip()
                    price = clean_price(price_text)

                    if price is None or name in seen_names:
                        continue
                    seen_names.add(name)

                    print(f"{len(seen_names)}. {name} - {price_text} (stored as {price})")
                    upsert_product_price(session, name, "PacknPay", price)

                except StaleElementReferenceException:
                    print(f"Product {idx} became stale, skipping...")
                except Exception as e:
                    print(f"Error scraping product {idx}: {e}")

            try:
                load_more_btn = driver.find_element(By.CSS_SELECTOR, "div.e-loop__load-more a.elementor-button-link")
                if load_more_btn.is_displayed() and "load more" in load_more_btn.text.strip().lower():
                    driver.execute_script("arguments[0].click();", load_more_btn)
                    print("Clicked Load More, waiting for new products...")
                    time.sleep(8)
                else:
                    print("No more products.")
                    break
            except (NoSuchElementException, ElementClickInterceptedException):
                print("No Load More button found.")
                break
    finally:
        driver.quit()
        print("Done scraping PacknPay.")


def clean_price(price_str):
    return float(price_str.replace('₦', '').replace(',', '').strip())


def run_scraper():
    session = SessionLocal()
    try:
        scrape_packnpaypro(session)
        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    run_scraper()
'''
from server.database.connection import SessionLocal
from server.database.db_utils import upsert_product_price  # central upsert
from datetime import datetime
import os, time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException
)


def scrape_osusubuy(session):
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")

    driver_path = os.path.join(os.path.dirname(__file__), "../../msedgedriver.exe")
    service = Service(executable_path=driver_path)
    driver = webdriver.Edge(service=service, options=options)

    print("Opening Osusu Buy Now...")
    driver.get("https://pro.packnpay.com.ng/shop/")   # TODO: update this to Osusu’s real shop page
    time.sleep(5)

    seen_names = set()

    try:
        while True:
            print("Scraping products...")
            products = driver.find_elements(By.CSS_SELECTOR, ".product-card")
            print(f"Found {len(products)} products on page.")

            for idx, product in enumerate(products, start=1):
                try:
                    name = product.find_element(By.CSS_SELECTOR, "h2.elementor-heading-title").text.strip()
                    price_text = product.find_element(By.CSS_SELECTOR, ".woocommerce-Price-amount bdi").text.strip()
                    price = clean_price(price_text)

                    if price is None or name in seen_names:
                        continue
                    seen_names.add(name)

                    print(f"{len(seen_names)}. {name} - {price_text} (stored as {price})")
                    upsert_product_price(session, name, "Osusu Buy Now", price)

                except StaleElementReferenceException:
                    print(f"Product {idx} became stale, skipping...")
                except Exception as e:
                    print(f"Error scraping product {idx}: {e}")

            # Try clicking "Load More" if available
            try:
                load_more_btn = driver.find_element(By.CSS_SELECTOR, "div.e-loop__load-more a.elementor-button-link")
                if load_more_btn.is_displayed() and "load more" in load_more_btn.text.strip().lower():
                    driver.execute_script("arguments[0].click();", load_more_btn)
                    print("Clicked Load More, waiting for new products...")
                    time.sleep(8)
                else:
                    print("No more products.")
                    break
            except (NoSuchElementException, ElementClickInterceptedException):
                print("No Load More button found.")
                break
    finally:
        driver.quit()
        print("Done scraping Osusu Buy Now.")


def clean_price(price_str):
    return float(price_str.replace('₦', '').replace(',', '').strip())


def run_scraper():
    session = SessionLocal()
    try:
        scrape_osusubuy(session)
        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    run_scraper()
