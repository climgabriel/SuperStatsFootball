"""
API Football Predictions Model
Stores predictions from API-Football's AI/Mathematical models
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class APIFootballPrediction(Base):
    """Predictions from API-Football's own prediction system."""

    __tablename__ = "api_predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fixture_id = Column(Integer, ForeignKey("fixtures.id"), nullable=False, unique=True, index=True)

    # Winner prediction
    winner_id = Column(Integer)  # Team ID or null for draw
    winner_name = Column(String(100))
    winner_comment = Column(String(255))

    # Win or Draw (boolean)
    win_or_draw = Column(Boolean)

    # Under/Over prediction
    under_over = Column(String(20))  # e.g., "Over 2.5"

    # Goals prediction
    goals_home = Column(String(10))  # e.g., "1-2"
    goals_away = Column(String(10))

    # Advice
    advice = Column(String(255))  # Overall betting advice

    # Winning percentages (from API's comparison data)
    percent_home = Column(String(10))  # e.g., "45%"
    percent_draw = Column(String(10))
    percent_away = Column(String(10))

    # Team comparison (JSON structure)
    # Structure: {"form": {"home": "80%", "away": "60%"}, "att": {...}, "def": {...}, ...}
    comparison = Column(JSON)

    # H2H last matches (JSON)
    h2h = Column(JSON)

    # League statistics (JSON)
    # Structure: {"form": {...}, "fixtures": {...}, "goals": {...}, ...}
    league_stats = Column(JSON)

    # Teams statistics (JSON)
    # Structure: {"home": {...}, "away": {...}}
    teams_stats = Column(JSON)

    # Metadata
    fetched_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    fixture = relationship("Fixture")

    def __repr__(self):
        return f"<APIFootballPrediction Fixture {self.fixture_id} - Advice: {self.advice}>"
