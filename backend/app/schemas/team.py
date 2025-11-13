from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TeamBase(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    country: Optional[str] = None
    logo: Optional[str] = None
    founded: Optional[int] = None
    venue_name: Optional[str] = None
    venue_capacity: Optional[int] = None


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    logo: Optional[str] = None
    venue_name: Optional[str] = None
    venue_capacity: Optional[int] = None


class TeamResponse(TeamBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
