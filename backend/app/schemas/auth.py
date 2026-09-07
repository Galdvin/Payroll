from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="admin@enterprise-payroll.com")
    password: str = Field(..., min_length=6, example="AdminPassword123!")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class CurrentUserPermissions(BaseModel):
    id: int
    uuid: str
    email: EmailStr
    full_name: str
    is_superuser: bool
    roles: List[str]
    permissions: List[str]

    model_config = {"from_attributes": True}
