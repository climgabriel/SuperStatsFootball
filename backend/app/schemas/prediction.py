from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class PredictionRequest(BaseModel):
    fixture_id: int
    model_type: str  # 'poisson', 'dixon_coles', 'elo', 'logistic', 'random_forest', 'xgboost'


class PredictionData(BaseModel):
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    predicted_home_score: Optional[float] = None
    predicted_away_score: Optional[float] = None
    most_likely_score: Optional[str] = None
    confidence_interval: Optional[Dict[str, Any]] = None
    model_details: Optional[Dict[str, Any]] = None


class PredictionResponse(BaseModel):
    id: str
    fixture_id: int
    model_type: str
    prediction_data: PredictionData
    confidence_score: Optional[float] = None
    created_at: datetime
    is_admin_model: bool

    class Config:
        from_attributes = True


class TeamRatingResponse(BaseModel):
    team_id: int
    league_id: int
    season: int
    elo_rating: float
    offensive_strength: Optional[float] = None
    defensive_strength: Optional[float] = None
    home_advantage: Optional[float] = None
    form_last_5: Optional[float] = None
    updated_at: datetime

    class Config:
        from_attributes = True
