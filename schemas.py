from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str = Field(..., min_length=8, max_length=72)

class UserResponse(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class URLCreate(BaseModel):
    url: HttpUrl
    ttl_days: Optional[int] = None  # Время жизни ссылки в днях

class URLInfo(BaseModel):
    original_url: str
    short_url: str
    clicks: int
    expires_at: Optional[datetime]
    class Config:
        from_attributes = True

class URLRanking(BaseModel):
    short_url: str
    original_url: str
    weekly_clicks: int