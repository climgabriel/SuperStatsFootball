from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Float, Text, Index
from datetime import datetime
import uuid

from app.db.base import Base
from app.core.constants import DEFAULT_ELO_RATING


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fixture_id = Column(Integer, ForeignKey("fixtures.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), index=True)
    model_type = Column(String(50), nullable=False, index=True)  # 'poisson', 'dixon_coles', 'elo', etc.
    prediction_data = Column(Text, nullable=False)  # JSON string
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_admin_model = Column(Boolean, default=False)

    # Composite indexes for common query patterns
    __table_args__ = (
        # Get predictions for a fixture by a user
        Index('ix_prediction_fixture_user', 'fixture_id', 'user_id'),
        # Get user's prediction history (sorted by date)
        Index('ix_prediction_user_created', 'user_id', 'created_at'),
        # Get predictions by model type
        Index('ix_prediction_model_created', 'model_type', 'created_at'),
    )

    def __repr__(self):
        return f"<Prediction {self.model_type} for fixture {self.fixture_id}>"


class TeamRating(Base):
    __tablename__ = "team_ratings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False, index=True)
    season = Column(Integer, nullable=False)
    elo_rating = Column(Float, default=DEFAULT_ELO_RATING)
    offensive_strength = Column(Float)
    defensive_strength = Column(Float)
    home_advantage = Column(Float)
    form_last_5 = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Composite index for most common lookup: team + league + season
    __table_args__ = (
        Index('ix_team_rating_lookup', 'team_id', 'league_id', 'season'),
        # League-specific ratings
        Index('ix_team_rating_league_season', 'league_id', 'season'),
    )

    def __repr__(self):
        return f"<TeamRating team={self.team_id} elo={self.elo_rating}>"


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False, index=True)
    favorite_leagues = Column(Text)  # JSON array
    favorite_teams = Column(Text)  # JSON array
    default_model = Column(String(50), default="poisson")
    timezone = Column(String(50), default="UTC")
    notifications = Column(Text)  # JSON object
    ui_preferences = Column(Text)  # JSON object
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserSettings user={self.user_id}>"
