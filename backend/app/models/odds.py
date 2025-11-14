from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base_class import Base


class FixtureOdds(Base):
    """
    Model for storing bookmaker odds for fixtures.
    Currently stores Superbet.ro odds only.
    Supports: 1X2, Halftime/Fulltime, Over/Under 2.5 goals.
    """
    __tablename__ = "fixture_odds"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    fixture_id = Column(Integer, ForeignKey("fixtures.id"), nullable=False, index=True)

    # Bookmaker information
    bookmaker_id = Column(Integer, nullable=False)  # API-Football bookmaker ID
    bookmaker_name = Column(String, nullable=False, index=True)  # "Superbet"

    # 1X2 Full Time Odds
    home_win_odds = Column(Float, nullable=True)  # 1
    draw_odds = Column(Float, nullable=True)       # X
    away_win_odds = Column(Float, nullable=True)   # 2

    # Halftime Odds
    ht_home_win_odds = Column(Float, nullable=True)  # HT 1
    ht_draw_odds = Column(Float, nullable=True)      # HT X
    ht_away_win_odds = Column(Float, nullable=True)  # HT 2

    # Fulltime Odds (separate from 1X2 if different bet type)
    ft_home_win_odds = Column(Float, nullable=True)  # FT 1
    ft_draw_odds = Column(Float, nullable=True)      # FT X
    ft_away_win_odds = Column(Float, nullable=True)  # FT 2

    # Over/Under 2.5 Goals
    over_2_5_odds = Column(Float, nullable=True)   # Over 2.5
    under_2_5_odds = Column(Float, nullable=True)  # Under 2.5

    # Metadata
    is_live = Column(Boolean, default=False, index=True)  # False = pre-match, True = live
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship
    fixture = relationship("Fixture", back_populates="odds")

    def __repr__(self):
        return f"<FixtureOdds(fixture_id={self.fixture_id}, bookmaker={self.bookmaker_name}, live={self.is_live})>"
