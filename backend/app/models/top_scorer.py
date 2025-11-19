"""
Top Scorers/Assists Model
Stores top scorers and assists data from API-Football
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class TopScorer(Base):
    """Top scorers in a league/season."""

    __tablename__ = "top_scorers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False, index=True)
    season = Column(Integer, nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)

    # Player info
    player_id = Column(Integer, nullable=False, index=True)
    player_name = Column(String(100))
    player_firstname = Column(String(50))
    player_lastname = Column(String(50))
    player_age = Column(Integer)
    player_nationality = Column(String(50))
    player_height = Column(String(20))
    player_weight = Column(String(20))
    player_photo = Column(String(255))

    # Position
    player_position = Column(String(20))  # Attacker, Midfielder, etc.

    # Statistics
    games_appearances = Column(Integer, default=0)
    games_minutes = Column(Integer, default=0)
    games_lineups = Column(Integer, default=0)
    games_rating = Column(String(10))  # Average rating

    # Goals
    goals_total = Column(Integer, default=0)
    goals_assists = Column(Integer, default=0)
    goals_conceded = Column(Integer, default=0)  # For goalkeepers
    goals_saves = Column(Integer, default=0)  # For goalkeepers

    # Shots
    shots_total = Column(Integer, default=0)
    shots_on = Column(Integer, default=0)

    # Passes
    passes_total = Column(Integer, default=0)
    passes_key = Column(Integer, default=0)
    passes_accuracy = Column(Integer, default=0)

    # Tackles
    tackles_total = Column(Integer, default=0)
    tackles_blocks = Column(Integer, default=0)
    tackles_interceptions = Column(Integer, default=0)

    # Duels
    duels_total = Column(Integer, default=0)
    duels_won = Column(Integer, default=0)

    # Dribbles
    dribbles_attempts = Column(Integer, default=0)
    dribbles_success = Column(Integer, default=0)

    # Fouls
    fouls_drawn = Column(Integer, default=0)
    fouls_committed = Column(Integer, default=0)

    # Cards
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)

    # Penalty
    penalty_scored = Column(Integer, default=0)
    penalty_missed = Column(Integer, default=0)
    penalty_saved = Column(Integer, default=0)

    # Metadata
    last_update = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    league = relationship("League", foreign_keys=[league_id])
    team = relationship("Team")

    def __repr__(self):
        return f"<TopScorer {self.player_name} - {self.goals_total} goals>"
