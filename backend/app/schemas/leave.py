from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class LeaveTypeCreate(BaseModel):
    name: str
    code: str
    is_paid: bool = True
    is_encashable: bool = False
    requires_approval: bool = True


class LeaveTypeResponse(LeaveTypeCreate):
    id: int

    model_config = {"from_attributes": True}


class LeavePolicyCreate(BaseModel):
    leave_type_id: int
    company_id: int
    annual_quota: float
    accrual_frequency: str = "Yearly"
    max_carry_forward: float = 0.0


class LeavePolicyResponse(LeavePolicyCreate):
    id: int

    model_config = {"from_attributes": True}


class LeaveBalanceResponse(BaseModel):
    id: int
    employee_id: int
    leave_type_id: int
    year: int
    accrued: float
    used: float
    pending: float
    total_balance: float
    leave_type: LeaveTypeResponse

    model_config = {"from_attributes": True}


class LeaveRequestApply(BaseModel):
    employee_id: int
    leave_type_id: int
    start_date: date
    end_date: date
    reason: Optional[str] = None


class LeaveApprovalRequest(BaseModel):
    status: str = Field(..., example="Approved") # Approved or Rejected
    approval_comments: Optional[str] = None


class LeaveRequestResponse(BaseModel):
    id: int
    employee_id: int
    leave_type_id: int
    start_date: date
    end_date: date
    total_days: float
    reason: Optional[str] = None
    status: str
    approved_by_user_id: Optional[int] = None
    approval_comments: Optional[str] = None
    leave_type: LeaveTypeResponse

    model_config = {"from_attributes": True}


class HolidayCreate(BaseModel):
    company_id: int
    branch_id: Optional[int] = None
    name: str
    date: date
    holiday_type: str = "National"
    is_optional: bool = False


class HolidayResponse(HolidayCreate):
    id: int

    model_config = {"from_attributes": True}


class CarryForwardRequest(BaseModel):
    employee_id: int
    from_year: int
    to_year: int
    max_carry_forward: float = 5.0


class CarryForwardResponse(BaseModel):
    employee_id: int
    from_year: int
    to_year: int
    carried_forward_days: float
    new_total_balance: float


class LeaveEncashmentRequest(BaseModel):
    employee_id: int
    leave_type_id: int
    days: float
    year: int = 2024
    daily_rate: float = 1000.0


class LeaveEncashmentResponse(BaseModel):
    employee_id: int
    leave_type_id: int
    days_encashed: float
    encashment_amount: float
    remaining_balance: float

