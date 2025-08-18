from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from server.database.connection import Base  # ⬅️ import Base from connection
from datetime import datetime


class ProductPrice(Base):
    __tablename__ = "product_prices"

    id = Column(Integer, primary_key=True)
    product_name = Column(String, nullable=False)
    source = Column(String, nullable=False)
    price = Column(Float, nullable=True)  # price is temporarily nullable until we start extracting it from detail
    # unit = Column(String, default="unit")
    detail = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('product_name', 'source', name='uq_product_source'),
    )
