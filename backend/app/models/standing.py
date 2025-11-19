"""
League Standings/Table Model
Stores league standings data from API-Football
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Standing(Base):
    """League standings/table position."""

    __tablename__ = "standings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False, index=True)
    season = Column(Integer, nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)

    # Position
    rank = Column(Integer, nullable=False)
    points = Column(Integer, nullable=False)

    # Form and status
    form = Column(String(10))  # e.g., "WWDLL"
    status = Column(String(50))  # e.g., "Champions League", "Relegation"
    description = Column(String(255))  # Status description

    # Matches
    played = Column(Integer, default=0)
    win = Column(Integer, default=0)
    draw = Column(Integer, default=0)
    lose = Column(Integer, default=0)

    # Goals
    goals_for = Column(Integer, default=0)
    goals_against = Column(Integer, default=0)
    goal_diff = Column(Integer, default=0)

    # Home record
    home_played = Column(Integer, default=0)
    home_win = Column(Integer, default=0)
    home_draw = Column(Integer, default=0)
    home_lose = Column(Integer, default=0)
    home_goals_for = Column(Integer, default=0)
    home_goals_against = Column(Integer, default=0)

    # Away record
    away_played = Column(Integer, default=0)
    away_win = Column(Integer, default=0)
    away_draw = Column(Integer, default=0)
    away_lose = Column(Integer, default=0)
    away_goals_for = Column(Integer, default=0)
    away_goals_against = Column(Integer, default=0)

    # Metadata
    last_update = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    league = relationship("League", foreign_keys=[league_id])
    team = relationship("Team")

    def __repr__(self):
        return f"<Standing {self.rank}. Team {self.team_id} - {self.points} pts>"
