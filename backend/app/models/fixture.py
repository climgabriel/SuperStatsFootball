from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey, Float, Text
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

    # Relationships
    league = relationship("League", backref="fixtures")
    home_team = relationship("Team", foreign_keys=[home_team_id], backref="home_fixtures")
    away_team = relationship("Team", foreign_keys=[away_team_id], backref="away_fixtures")
    stats = relationship("FixtureStat", back_populates="fixture", cascade="all, delete-orphan")
    score = relationship("FixtureScore", back_populates="fixture", cascade="all, delete-orphan", uselist=False)
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

    fixture = relationship("Fixture", back_populates="stats")
    team = relationship("Team")

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

    fixture = relationship("Fixture", back_populates="score")

    def __repr__(self):
        return f"<FixtureScore fixture={self.fixture_id}>"
