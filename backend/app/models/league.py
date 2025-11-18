from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

from app.db.base import Base


class League(Base):
    __tablename__ = "leagues"

    # Composite primary key: (id, season) allows same league across multiple seasons
    id = Column(Integer, primary_key=True)  # API-Football league ID
    season = Column(Integer, primary_key=True)  # Season year
    name = Column(String(255), nullable=False)
    country = Column(String(100))
    logo = Column(String(500))
    tier_required = Column(String(20), default="free", index=True)
    is_active = Column(Boolean, default=True, index=True)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<League {self.name} ({self.season})>"
