"""
Head-to-Head History Model
Stores historical match data between teams
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class H2HMatch(Base):
    """Head-to-head historical match between two teams."""

    __tablename__ = "h2h_matches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # This is essentially a reference to a fixture
    fixture_id = Column(Integer, ForeignKey("fixtures.id"), nullable=False, unique=True, index=True)

    # Teams involved (for quick lookup)
    team1_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    team2_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)

    # League and season
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    season = Column(Integer, nullable=False)

    # Match details
    match_date = Column(DateTime, nullable=False, index=True)
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)

    # Score
    home_score = Column(Integer)
    away_score = Column(Integer)

    # Status
    status = Column(String(20))  # FT, AET, PEN, etc.

    # Winner
    winner_id = Column(Integer, ForeignKey("teams.id"))  # NULL for draw

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    fixture = relationship("Fixture")
    team1 = relationship("Team", foreign_keys=[team1_id])
    team2 = relationship("Team", foreign_keys=[team2_id])
    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team = relationship("Team", foreign_keys=[away_team_id])
    winner = relationship("Team", foreign_keys=[winner_id])
    league = relationship("League", foreign_keys=[league_id])

    # Composite indexes for efficient lookups
    __table_args__ = (
        Index('ix_h2h_teams', 'team1_id', 'team2_id'),
        Index('ix_h2h_teams_reverse', 'team2_id', 'team1_id'),
        Index('ix_h2h_date', 'match_date'),
    )

    def __repr__(self):
        return f"<H2HMatch {self.home_team_id} vs {self.away_team_id} ({self.home_score}-{self.away_score})>"
