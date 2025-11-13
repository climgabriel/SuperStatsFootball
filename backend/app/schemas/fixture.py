from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class FixtureScoreBase(BaseModel):
    home_halftime: Optional[int] = None
    away_halftime: Optional[int] = None
    home_fulltime: Optional[int] = None
    away_fulltime: Optional[int] = None
    home_extratime: Optional[int] = None
    away_extratime: Optional[int] = None
    home_penalty: Optional[int] = None
    away_penalty: Optional[int] = None


class FixtureStatBase(BaseModel):
    team_id: int
    shots_on_goal: Optional[int] = None
    shots_off_goal: Optional[int] = None
    total_shots: Optional[int] = None
    blocked_shots: Optional[int] = None
    shots_inside_box: Optional[int] = None
    shots_outside_box: Optional[int] = None
    fouls: Optional[int] = None
    corners: Optional[int] = None
    offsides: Optional[int] = None
    ball_possession: Optional[int] = None
    yellow_cards: Optional[int] = None
    red_cards: Optional[int] = None
    goalkeeper_saves: Optional[int] = None
    total_passes: Optional[int] = None
    passes_accurate: Optional[int] = None
    passes_percentage: Optional[int] = None
    expected_goals: Optional[float] = None


class FixtureBase(BaseModel):
    id: int
    league_id: int
    season: int
    round: Optional[str] = None
    match_date: datetime
    timestamp: int
    home_team_id: int
    away_team_id: int
    status: str
    elapsed_time: Optional[int] = None
    venue: Optional[str] = None
    referee: Optional[str] = None


class FixtureCreate(FixtureBase):
    pass


class FixtureResponse(FixtureBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FixtureDetailResponse(FixtureResponse):
    score: Optional[FixtureScoreBase] = None
    home_stats: Optional[FixtureStatBase] = None
    away_stats: Optional[FixtureStatBase] = None


class FixtureListQuery(BaseModel):
    league_id: Optional[int] = None
    season: Optional[int] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    team_id: Optional[int] = None
    status: Optional[str] = None
    next_round_only: bool = False
    limit: int = 20
    offset: int = 0
