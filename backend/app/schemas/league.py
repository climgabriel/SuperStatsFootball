from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LeagueBase(BaseModel):
    id: int
    name: str
    country: Optional[str] = None
    logo: Optional[str] = None
    season: int
    tier_required: str = "free"
    is_active: bool = True
    priority: int = 0


class LeagueCreate(LeagueBase):
    pass


class LeagueUpdate(BaseModel):
    name: Optional[str] = None
    tier_required: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class LeagueResponse(LeagueBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
