from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.db.base import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)  # API-Football team ID
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(10))
    country = Column(String(100))
    logo = Column(String(500))
    founded = Column(Integer)
    venue_name = Column(String(255))
    venue_capacity = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Team {self.name}>"
