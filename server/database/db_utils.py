from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from .models import ProductPrice


def upsert_product_price(session: Session, product_name: str, source: str, price: float, detail: str = None):
    """
    Inserts or updates a product price record.
    Uses the unique constraint on (product_name, source) to avoid duplicates.
    """

    existing = session.query(ProductPrice).filter_by(product_name=product_name, source=source).first()

    if existing:
        # Update the existing row
        existing.price = price
        existing.detail = detail
        existing.timestamp = datetime.utcnow()
    else:
        # Insert a new row
        new_entry = ProductPrice(
            product_name=product_name,
            source=source,
            price=price,
            detail=detail
        )
        session.add(new_entry)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        print(f"IntegrityError: Could not upsert {product_name} from {source}")
