from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    expires_in_days: Optional[int] = Field(None, gt=0)


class ApiKeyResponse(BaseModel):
    id: int
    key_value: str
    name: str
    description: Optional[str]
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool
    is_revoked: bool

    class Config:
        from_attributes = True


class ApiKeyValidate(BaseModel):
    key_value: str


class ApiKeyValidationResponse(BaseModel):
    is_valid: bool
    is_active: bool
    is_expired: bool
    is_revoked: bool
    key_id: Optional[int]
    key_name: Optional[str]
    owner_id: Optional[int]
    expires_at: Optional[datetime]
