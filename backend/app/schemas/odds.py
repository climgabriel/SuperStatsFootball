from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class OddsBase(BaseModel):
    """Base schema for bookmaker odds."""

    bookmaker_id: int
    bookmaker_name: str
    home_win_odds: Optional[float] = None
    draw_odds: Optional[float] = None
    away_win_odds: Optional[float] = None
    ht_home_win_odds: Optional[float] = None
    ht_draw_odds: Optional[float] = None
    ht_away_win_odds: Optional[float] = None
    ft_home_win_odds: Optional[float] = None
    ft_draw_odds: Optional[float] = None
    ft_away_win_odds: Optional[float] = None
    over_2_5_odds: Optional[float] = None
    under_2_5_odds: Optional[float] = None
    is_live: bool = False


class OddsCreate(OddsBase):
    """Schema for creating odds."""
    fixture_id: int


class OddsUpdate(BaseModel):
    """Schema for updating odds."""
    home_win_odds: Optional[float] = None
    draw_odds: Optional[float] = None
    away_win_odds: Optional[float] = None
    ht_home_win_odds: Optional[float] = None
    ht_draw_odds: Optional[float] = None
    ht_away_win_odds: Optional[float] = None
    ft_home_win_odds: Optional[float] = None
    ft_draw_odds: Optional[float] = None
    ft_away_win_odds: Optional[float] = None
    over_2_5_odds: Optional[float] = None
    under_2_5_odds: Optional[float] = None
    is_live: Optional[bool] = None
    fetched_at: Optional[datetime] = None


class OddsResponse(OddsBase):
    """Schema for odds response."""

    id: str
    fixture_id: int
    fetched_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Odds1X2(BaseModel):
    """Simplified 1X2 odds for display."""
    home: Optional[float] = Field(None, alias="1")
    draw: Optional[float] = Field(None, alias="X")
    away: Optional[float] = Field(None, alias="2")

    class Config:
        populate_by_name = True


class OddsHalfTime(BaseModel):
    """Halftime odds."""
    home: Optional[float] = None
    draw: Optional[float] = None
    away: Optional[float] = None


class OddsOverUnder(BaseModel):
    """Over/Under 2.5 goals odds."""
    over: Optional[float] = None
    under: Optional[float] = None


class FixtureWithOdds(BaseModel):
    """Fixture combined with odds for display."""

    # Fixture information
    fixture_id: int
    league_name: str
    match_date: datetime
    home_team: str
    away_team: str
    status: str

    # Bookmaker odds
    bookmaker: str = "Superbet"
    odds_1x2: Odds1X2
    odds_halftime: OddsHalfTime
    odds_fulltime: Odds1X2
    odds_over_under_2_5: OddsOverUnder

    # Metadata
    is_live: bool = False
    fetched_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OddsListResponse(BaseModel):
    """Response for list of fixtures with odds."""

    total: int
    fixtures: list[FixtureWithOdds]
