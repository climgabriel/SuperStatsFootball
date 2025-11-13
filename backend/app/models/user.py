from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.db.base import Base


class TierEnum(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    PREMIUM = "premium"
    ULTIMATE = "ultimate"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    tier = Column(String(20), default="free", nullable=False, index=True)
    subscription_id = Column(String(255))
    subscription_status = Column(String(20), default="active")
    stripe_customer_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    def __repr__(self):
        return f"<User {self.email}>"
