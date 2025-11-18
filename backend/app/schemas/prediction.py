from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class PredictionRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    fixture_id: int
    model_type: str  # 'poisson', 'dixon_coles', 'bivariate_poisson', 'elo', 'glicko'


class PredictionData(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    predicted_home_score: Optional[float] = None
    predicted_away_score: Optional[float] = None
    most_likely_score: Optional[str] = None
    confidence_interval: Optional[Dict[str, Any]] = None
    model_details: Optional[Dict[str, Any]] = None


class PredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: str
    fixture_id: int
    model_type: str
    prediction_data: PredictionData
    confidence_score: Optional[float] = None
    created_at: datetime
    is_admin_model: bool


class TeamRatingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    team_id: int
    league_id: int
    season: int
    elo_rating: float
    offensive_strength: Optional[float] = None
    defensive_strength: Optional[float] = None
    home_advantage: Optional[float] = None
    form_last_5: Optional[float] = None
    updated_at: datetime
