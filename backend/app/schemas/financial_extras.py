from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class LoanRequestCreate(BaseModel):
    employee_id: int
    principal: float = Field(..., example=100000.0)
    interest_rate: float = Field(10.0, example=10.0) # 10%
    tenure_months: int = Field(12, example=12)
    start_date: date


class LoanResponse(BaseModel):
    id: int
    employee_id: int
    principal: float
    interest_rate: float
    tenure_months: int
    start_date: date
    monthly_emi: float
    outstanding_amount: float
    status: str

    model_config = {"from_attributes": True}


class AdvanceRequestCreate(BaseModel):
    employee_id: int
    amount: float = Field(..., example=15000.0)
    request_date: date
    recovery_months: int = 1


class AdvanceResponse(BaseModel):
    id: int
    employee_id: int
    amount: float
    request_date: date
    recovery_months: int
    monthly_recovery_amount: float
    recovered_amount: float
    status: str

    model_config = {"from_attributes": True}


class BonusIncentiveCreate(BaseModel):
    employee_id: int
    title: str = Field(..., example="Q3 Performance Bonus")
    category: str = Field("Performance Bonus", example="Performance Bonus")
    amount: float = Field(..., example=25000.0)
    is_taxable: bool = True
    payout_date: date


class BonusIncentiveResponse(BonusIncentiveCreate):
    id: int
    status: str

    model_config = {"from_attributes": True}


class ReimbursementItemCreate(BaseModel):
    description: str
    amount: float


class ReimbursementCreate(BaseModel):
    employee_id: int
    title: str
    category: str = "Travel"
    items: List[ReimbursementItemCreate] = []


class ReimbursementItemResponse(BaseModel):
    id: int
    description: str
    amount: float
    receipt_file_path: Optional[str] = None

    model_config = {"from_attributes": True}


class ReimbursementResponse(BaseModel):
    id: int
    employee_id: int
    title: str
    category: str
    total_amount: float
    status: str
    items: List[ReimbursementItemResponse] = []

    model_config = {"from_attributes": True}


class ReimbursementApprovalRequest(BaseModel):
    status: str = Field(..., example="Manager_Approved") # Manager_Approved, Finance_Approved, Rejected
