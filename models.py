from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    api_key = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)

    # --- NEW COLUMNS FOR BILLING & TRACKING ---
    subscription_plan = Column(String, default="free")
    api_call_count = Column(Integer, default=0)
    stripe_customer_id = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())