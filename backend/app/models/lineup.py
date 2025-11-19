"""
Match Lineups Model
Stores player lineups and formations from API-Football
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Lineup(Base):
    """Match lineup for a team."""

    __tablename__ = "lineups"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fixture_id = Column(Integer, ForeignKey("fixtures.id"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)

    # Formation
    formation = Column(String(20))  # e.g., "4-4-2", "4-3-3"

    # Coach
    coach_id = Column(Integer)
    coach_name = Column(String(100))
    coach_photo = Column(String(255))

    # Players (stored as JSON)
    # Structure: [{"player_id": 123, "player_name": "Name", "number": 10, "pos": "G", "grid": "1:1"}, ...]
    starting_xi = Column(JSON)  # Starting 11 players
    substitutes = Column(JSON)  # Substitute players

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    fixture = relationship("Fixture")
    team = relationship("Team")

    def __repr__(self):
        return f"<Lineup Fixture {self.fixture_id} - Team {self.team_id} ({self.formation})>"


class PlayerStatistic(Base):
    """Player statistics for a match."""

    __tablename__ = "player_statistics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fixture_id = Column(Integer, ForeignKey("fixtures.id"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)

    # Player info
    player_id = Column(Integer, nullable=False, index=True)
    player_name = Column(String(100))
    player_number = Column(Integer)
    player_position = Column(String(20))  # G, D, M, F
    player_grid = Column(String(10))  # Grid position like "1:1"

    # Match statistics
    minutes_played = Column(Integer)
    rating = Column(String(10))  # Player rating (e.g., "7.3")
    captain = Column(Boolean, default=False)
    substitute = Column(Boolean, default=False)

    # Performance stats
    offsides = Column(Integer)
    shots_total = Column(Integer)
    shots_on = Column(Integer)
    goals_total = Column(Integer)
    goals_conceded = Column(Integer)
    goals_assists = Column(Integer)

    # Passing
    passes_total = Column(Integer)
    passes_key = Column(Integer)
    passes_accuracy = Column(Integer)  # Percentage

    # Dribbles
    dribbles_attempts = Column(Integer)
    dribbles_success = Column(Integer)
    dribbles_past = Column(Integer)

    # Duels
    duels_total = Column(Integer)
    duels_won = Column(Integer)

    # Tackles/Blocks
    tackles_total = Column(Integer)
    tackles_blocks = Column(Integer)
    tackles_interceptions = Column(Integer)

    # Cards
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)

    # Fouls
    fouls_drawn = Column(Integer)
    fouls_committed = Column(Integer)

    # Penalty
    penalty_won = Column(Integer)
    penalty_committed = Column(Integer)
    penalty_scored = Column(Integer)
    penalty_missed = Column(Integer)
    penalty_saved = Column(Integer)

    # Goalkeeper (if applicable)
    saves = Column(Integer)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    fixture = relationship("Fixture")
    team = relationship("Team")

    def __repr__(self):
        return f"<PlayerStatistic {self.player_name} - Fixture {self.fixture_id}>"
