from pydantic import BaseModel, EmailStr, Field, field_serializer, model_serializer
from typing import Optional, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=72)


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

    @model_serializer(mode='wrap')
    def serialize_model(self, serializer):
        """
        Custom serializer to add role and plan fields for frontend compatibility.
        """
        # Get the base serialized data
        data = serializer(self)

        # Add computed role field
        # "admin" for ultimate tier users, "user" for all others
        data['role'] = "admin" if self.tier == "ultimate" else "user"

        # Add computed plan field
        # Maps tier to numeric plan (1-5) for frontend
        tier_to_plan = {
            "free": 1,
            "starter": 2,
            "pro": 3,
            "premium": 4,
            "ultimate": 5
        }
        data['plan'] = tier_to_plan.get(self.tier, 1)

        return data

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str
