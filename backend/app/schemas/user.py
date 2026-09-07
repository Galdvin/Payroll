from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from app.schemas.rbac import RoleResponse


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    organization_id: Optional[int] = None
    company_id: Optional[int] = None
    role_ids: List[int] = []


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    organization_id: Optional[int] = None
    company_id: Optional[int] = None
    role_ids: Optional[List[int]] = None


class UserResponse(BaseModel):
    id: int
    uuid: str
    email: EmailStr
    full_name: str
    is_active: bool
    is_superuser: bool
    organization_id: Optional[int] = None
    company_id: Optional[int] = None
    roles: List[RoleResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
