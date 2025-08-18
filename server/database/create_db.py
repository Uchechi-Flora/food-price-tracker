'''FOR THIS CODE, I USED IT TO REMOVE DUPLICATES
from sqlalchemy.orm import Session
from server.database.connection import SessionLocal
from server.database.models import ProductPrice

session: Session = SessionLocal()

# --- 1. Remove duplicates ---
unique_keys = set()
duplicates = []

for row in session.query(ProductPrice).all():
    key = (row.product_name, row.source)
    if key in unique_keys:
        duplicates.append(row.id)
    else:
        unique_keys.add(key)

if duplicates:
    session.query(ProductPrice).filter(ProductPrice.id.in_(duplicates)).delete(synchronize_session=False)
    session.commit()
    print(f"Removed {len(duplicates)} duplicates.")

# --- 2. Replace PacknPayPro with PacknPay ---
session.query(ProductPrice).filter(ProductPrice.source == 'PacknPayPro').update({"source": "PacknPay"})
session.commit()
print("Replaced PacknPayPro with PacknPay.")

session.close()
'''
#THIS CODE BELOW, I USED IT TO REMOVE INVALID ENTRIES IN MY DB PRODUCTS THAT JUST HAVE ₦ ₦ or just a single naira symbol
from server.database.connection import SessionLocal
from server.database.models import ProductPrice

def delete_invalid_products():
    """
    Deletes all rows from the ProductPrice table where the 'detail' column
    contains the invalid strings "₦ ₦" or "₦".
    """
    session = SessionLocal()
    try:
        # Find the rows to be deleted, checking for both invalid strings
        products_to_delete = session.query(ProductPrice).filter(
            (ProductPrice.detail == '₦ ₦') | (ProductPrice.detail == '₦')
        ).all()
        
        if not products_to_delete:
            print("No invalid products found with '₦ ₦' or '₦' in the detail column. Database is clean!")
            return

        # Print the number of products to be deleted for confirmation
        print(f"Found {len(products_to_delete)} invalid products to delete.")
        
        # Delete the found products
        for product in products_to_delete:
            session.delete(product)

        # Commit the changes to the database
        session.commit()
        print("Successfully removed the invalid products from the database.")
        
    except Exception as e:
        # Rollback in case of any error
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        # Close the session
        session.close()

if __name__ == "__main__":
    delete_invalid_products()