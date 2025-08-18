# check_data.py
'''
from server.database.connection import SessionLocal
from server.database.models import ProductPrice

session = SessionLocal()

products = session.query(ProductPrice).order_by(ProductPrice.id.desc()).limit(50).all()

for product in products:
    print(f"{product.id}: {product.product_name} - ₦{product.price}  - {product.source}")
    '''

from server.database.connection import SessionLocal
from server.database.models import ProductPrice

def view_database_contents():
    session = SessionLocal()
    try:
        # Fetch all rows from the ProductPrice table
        products = session.query(ProductPrice).all()

        if not products:
            print("No data found in the ProductPrice table.")
            return

        print("--- Database Contents ---")
        # Print a header
        print(f"{'ID':<5} | {'Product Name':<40} | {'Source':<20} | {'Price':<20} | {'Detail':<30}")
        print("-" * 120)

        # Iterate and print each product's data
        for product in products:
            # Safely handle potential None values
            price_str = str(product.price) if product.price is not None else "N/A"
            source_str = str(product.source) if product.source is not None else "N/A"
            detail_str = str(product.detail) if product.detail is not None else "N/A"
            
            print(f"{product.id:<5} | {product.product_name:<40} | {source_str:<20} | {price_str:<20} | {detail_str:<30}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    view_database_contents()