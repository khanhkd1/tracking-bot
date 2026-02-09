from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Enum
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class TrackingOrder(Base):
    __tablename__ = "tracking_orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    order_name = Column(String(50), nullable=False)
    tracking_code = Column(String(50), nullable=False)
    last_order_code = Column(String(10), nullable=True)

    def __repr__(self):
        return f"<TrackingOrder(id={self.id}, user_id={self.user_id}, tracking_code={self.tracking_code}, last_spx_code={self.last_spx_code})>"
