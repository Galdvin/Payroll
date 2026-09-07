from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from app.schemas.organization import (
    DepartmentResponse,
    DesignationResponse,
    BranchResponse,
)


class BankDetailsSchema(BaseModel):
    bank_name: str
    account_number: str
    ifsc_code: Optional[str] = None
    iban: Optional[str] = None
    swift_code: Optional[str] = None


class AddressSchema(BaseModel):
    street: str
    city: str
    state: str
    country: str
    postal_code: str


class EmergencyContactSchema(BaseModel):
    name: str
    relationship: str
    phone: str


class EmployeeCreate(BaseModel):
    employee_code: str = Field(..., min_length=2, max_length=50)
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    gender: str = "Male"
    date_of_birth: date
    nationality: str = "Indian"
    employment_type: str = "Full Time"
    status: str = "Active"
    joining_date: date
    confirmation_date: Optional[date] = None

    organization_id: int
    company_id: int
    branch_id: Optional[int] = None
    department_id: Optional[int] = None
    designation_id: Optional[int] = None
    cost_center_id: Optional[int] = None
    reporting_manager_id: Optional[int] = None
    user_id: Optional[int] = None

    work_email: EmailStr
    personal_email: Optional[EmailStr] = None
    phone: Optional[str] = None
    emergency_contact: Optional[EmergencyContactSchema] = None
    address: Optional[AddressSchema] = None

    currency: str = "INR"
    bank_details: Optional[BankDetailsSchema] = None
    tax_identifier: Optional[str] = None
    statutory_identifiers: Optional[Dict[str, Any]] = None


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None
    employment_type: Optional[str] = None
    status: Optional[str] = None
    joining_date: Optional[date] = None
    confirmation_date: Optional[date] = None

    branch_id: Optional[int] = None
    department_id: Optional[int] = None
    designation_id: Optional[int] = None
    cost_center_id: Optional[int] = None
    reporting_manager_id: Optional[int] = None
    user_id: Optional[int] = None

    work_email: Optional[EmailStr] = None
    personal_email: Optional[EmailStr] = None
    phone: Optional[str] = None
    emergency_contact: Optional[EmergencyContactSchema] = None
    address: Optional[AddressSchema] = None

    currency: Optional[str] = None
    bank_details: Optional[BankDetailsSchema] = None
    tax_identifier: Optional[str] = None
    statutory_identifiers: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class EmployeeHistoryResponse(BaseModel):
    id: int
    employee_id: int
    effective_date: date
    change_type: str
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    remarks: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class EmployeeResponse(BaseModel):
    id: int
    uuid: str
    employee_code: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    gender: str
    date_of_birth: date
    nationality: str
    employment_type: str
    status: str
    joining_date: date
    confirmation_date: Optional[date] = None

    organization_id: int
    company_id: int
    branch_id: Optional[int] = None
    department_id: Optional[int] = None
    designation_id: Optional[int] = None
    cost_center_id: Optional[int] = None
    reporting_manager_id: Optional[int] = None
    user_id: Optional[int] = None

    work_email: EmailStr
    personal_email: Optional[EmailStr] = None
    phone: Optional[str] = None
    emergency_contact: Optional[Dict[str, Any]] = None
    address: Optional[Dict[str, Any]] = None

    currency: str
    bank_details: Optional[Dict[str, Any]] = None
    tax_identifier: Optional[str] = None
    statutory_identifiers: Optional[Dict[str, Any]] = None
    is_active: bool

    department: Optional[DepartmentResponse] = None
    designation: Optional[DesignationResponse] = None
    branch: Optional[BranchResponse] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
