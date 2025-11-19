from pydantic import BaseModel, EmailStr, Field, computed_field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    timezone: Optional[str] = None


class UserInDB(UserBase):
    id: str
    tier: str
    subscription_status: str
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    id: str
    tier: str
    subscription_status: str
    created_at: datetime

    @computed_field
    @property
    def role(self) -> str:
        """
        Derive role from tier for frontend compatibility.

        Returns:
            "admin" for ultimate tier users, "user" for all others
        """
        return "admin" if self.tier == "ultimate" else "user"

    @computed_field
    @property
    def plan(self) -> int:
        """
        Convert tier to numeric plan for frontend compatibility.

        Frontend expects numeric plans:
        1 = free, 2 = starter, 3 = pro, 4 = premium, 5 = ultimate

        Returns:
            Numeric plan ID (1-5)
        """
        tier_to_plan = {
            "free": 1,
            "starter": 2,
            "pro": 3,
            "premium": 4,
            "ultimate": 5
        }
        return tier_to_plan.get(self.tier, 1)

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str
