from typing import List, Optional
from pydantic import BaseModel, Field


class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=2, max_length=50)
    tax_identifier: Optional[str] = None
    currency: str = "INR"
    country: str = "India"


class OrganizationResponse(OrganizationCreate):
    id: int

    model_config = {"from_attributes": True}


class CompanyCreate(BaseModel):
    organization_id: int
    name: str
    code: str
    registration_number: Optional[str] = None
    logo_url: Optional[str] = None


class CompanyResponse(CompanyCreate):
    id: int

    model_config = {"from_attributes": True}


class BranchCreate(BaseModel):
    company_id: int
    name: str
    code: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    timezone: str = "Asia/Kolkata"


class BranchResponse(BranchCreate):
    id: int

    model_config = {"from_attributes": True}


class DepartmentCreate(BaseModel):
    company_id: int
    parent_department_id: Optional[int] = None
    name: str
    code: str


class DepartmentResponse(DepartmentCreate):
    id: int

    model_config = {"from_attributes": True}


class DesignationCreate(BaseModel):
    company_id: int
    title: str
    code: str
    grade: Optional[str] = None


class DesignationResponse(DesignationCreate):
    id: int

    model_config = {"from_attributes": True}


class CostCenterCreate(BaseModel):
    company_id: int
    name: str
    code: str
    budget_allocation: Optional[float] = None


class CostCenterResponse(CostCenterCreate):
    id: int

    model_config = {"from_attributes": True}
