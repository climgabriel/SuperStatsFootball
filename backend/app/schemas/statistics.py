from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# Goals Statistics
class GoalsStats(BaseModel):
    over_under_2_5: dict
    over_under_1_5: dict
    over_under_3_5: dict
    btts: dict
    total_goals: dict


class GoalsStatisticsResponse(BaseModel):
    fixture_id: int
    league_name: str
    match_date: datetime
    home_team: str
    away_team: str
    status: str
    goals_stats: GoalsStats


# Corners Statistics
class CornersStats(BaseModel):
    total_corners: dict
    home_corners: dict
    away_corners: dict
    first_corner: Optional[dict] = None
    last_corner: Optional[dict] = None


class CornersStatisticsResponse(BaseModel):
    fixture_id: int
    league_name: str
    match_date: datetime
    home_team: str
    away_team: str
    status: str
    corners_stats: CornersStats


# Cards Statistics
class CardsStats(BaseModel):
    total_cards: dict
    home_cards: dict
    away_cards: dict
    bookings: Optional[dict] = None


class CardsStatisticsResponse(BaseModel):
    fixture_id: int
    league_name: str
    match_date: datetime
    home_team: str
    away_team: str
    status: str
    cards_stats: CardsStats


# Shots Statistics
class ShotsStats(BaseModel):
    total_shots: dict
    home_shots: dict
    away_shots: dict


class ShotsStatisticsResponse(BaseModel):
    fixture_id: int
    league_name: str
    match_date: datetime
    home_team: str
    away_team: str
    status: str
    shots_stats: ShotsStats


# Fouls Statistics
class FoulsStats(BaseModel):
    total_fouls: dict
    home_fouls: dict
    away_fouls: dict
    discipline_index: Optional[dict] = None


class FoulsStatisticsResponse(BaseModel):
    fixture_id: int
    league_name: str
    match_date: datetime
    home_team: str
    away_team: str
    status: str
    fouls_stats: FoulsStats


# Offsides Statistics
class OffsiddesStats(BaseModel):
    total_offsides: dict
    home_offsides: dict
    away_offsides: dict
    attacking_style: Optional[dict] = None


class OffsStatisticsResponse(BaseModel):
    fixture_id: int
    league_name: str
    match_date: datetime
    home_team: str
    away_team: str
    status: str
    offsides_stats: OffsiddesStats


# List responses
class StatisticsListResponse(BaseModel):
    total: int
    fixtures: List


class GoalsListResponse(BaseModel):
    total: int
    fixtures: List[GoalsStatisticsResponse]


class CornersListResponse(BaseModel):
    total: int
    fixtures: List[CornersStatisticsResponse]


class CardsListResponse(BaseModel):
    total: int
    fixtures: List[CardsStatisticsResponse]


class ShotsListResponse(BaseModel):
    total: int
    fixtures: List[ShotsStatisticsResponse]


class FoulsListResponse(BaseModel):
    total: int
    fixtures: List[FoulsStatisticsResponse]


class OffsListResponse(BaseModel):
    total: int
    fixtures: List[OffsStatisticsResponse]
