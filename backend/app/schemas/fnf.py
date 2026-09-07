from datetime import date
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class FnfCalculateRequest(BaseModel):
    employee_id: int
    resignation_date: date
    last_working_date: date
    settlement_reason: str = "Resignation" # Resignation, Termination, Retirement
    notice_days_short: int = 0
    notice_days_paid: int = 0
    additional_bonus: float = 0.0
    gratuity_override: Optional[float] = None
    remarks: Optional[str] = None


class FnfSettlementResponse(BaseModel):
    id: int
    employee_id: int
    company_id: int
    resignation_date: date
    last_working_date: date
    settlement_date: date
    settlement_reason: str
    
    pending_salary_days: float
    pending_salary_amount: float
    leave_encashment_days: float
    leave_encashment_amount: float
    notice_pay_amount: float
    bonus_settlement_amount: float
    gratuity_amount: float
    gross_settlement_amount: float
    
    notice_recovery_amount: float
    outstanding_loan_deduction: float
    outstanding_advance_deduction: float
    total_deductions_amount: float
    net_settlement_amount: float
    
    status: str
    remarks: Optional[str] = None
    calculation_trace: Dict[str, Any]

    model_config = {"from_attributes": True}
