from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey, Float, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class Fixture(Base):
    __tablename__ = "fixtures"

    id = Column(Integer, primary_key=True)  # API-Football fixture ID
    league_id = Column(Integer, ForeignKey("leagues.id"), index=True)
    season = Column(Integer, nullable=False)
    round = Column(String(50), index=True)
    match_date = Column(DateTime, nullable=False, index=True)
    timestamp = Column(BigInteger, nullable=False)
    home_team_id = Column(Integer, ForeignKey("teams.id"), index=True)
    away_team_id = Column(Integer, ForeignKey("teams.id"), index=True)
    status = Column(String(20), index=True)  # 'NS', 'LIVE', 'FT', etc.
    elapsed_time = Column(Integer)
    venue = Column(String(255))
    referee = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Composite indexes for common query patterns
    __table_args__ = (
        # Most common: Get fixtures by league, season, and status
        Index('ix_fixture_league_season_status', 'league_id', 'season', 'status'),
        # Upcoming fixtures query: match_date + status
        Index('ix_fixture_date_status', 'match_date', 'status'),
        # Team-specific queries
        Index('ix_fixture_teams', 'home_team_id', 'away_team_id'),
        # League + date range queries
        Index('ix_fixture_league_date', 'league_id', 'match_date'),
    )

    # Relationships
    odds = relationship("FixtureOdds", back_populates="fixture", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Fixture {self.id}: {self.home_team_id} vs {self.away_team_id}>"


class FixtureStat(Base):
    __tablename__ = "fixture_stats"

    id = Column(String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    fixture_id = Column(Integer, ForeignKey("fixtures.id"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    shots_on_goal = Column(Integer)
    shots_off_goal = Column(Integer)
    total_shots = Column(Integer)
    blocked_shots = Column(Integer)
    shots_inside_box = Column(Integer)
    shots_outside_box = Column(Integer)
    fouls = Column(Integer)
    corners = Column(Integer)
    offsides = Column(Integer)
    ball_possession = Column(Integer)
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)
    goalkeeper_saves = Column(Integer)
    total_passes = Column(Integer)
    passes_accurate = Column(Integer)
    passes_percentage = Column(Integer)
    expected_goals = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Composite index for most common query: get stats for fixture + team
    __table_args__ = (
        Index('ix_fixture_stat_fixture_team', 'fixture_id', 'team_id'),
        # Team-specific stats queries
        Index('ix_fixture_stat_team_created', 'team_id', 'created_at'),
    )

    def __repr__(self):
        return f"<FixtureStat fixture={self.fixture_id} team={self.team_id}>"


class FixtureScore(Base):
    __tablename__ = "fixture_scores"

    id = Column(String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    fixture_id = Column(Integer, ForeignKey("fixtures.id"), nullable=False, unique=True, index=True)
    home_halftime = Column(Integer)
    away_halftime = Column(Integer)
    home_fulltime = Column(Integer)
    away_fulltime = Column(Integer)
    home_extratime = Column(Integer)
    away_extratime = Column(Integer)
    home_penalty = Column(Integer)
    away_penalty = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<FixtureScore fixture={self.fixture_id}>"
