from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.employee import EmployeeResponse


class PayrollPeriodCreate(BaseModel):
    company_id: int = 1
    name: str = Field(..., example="September 2024 Payroll")
    year_month: str = Field(..., example="2024-09")
    start_date: date
    end_date: date
    cutoff_date: date


class PayrollPeriodResponse(PayrollPeriodCreate):
    id: int
    status: str

    model_config = {"from_attributes": True}


class CalculatePayrollRequest(BaseModel):
    payroll_period_id: int


class PayrollEarningResponse(BaseModel):
    id: int
    component_code: str
    name: str
    full_amount: float
    prorated_amount: float

    model_config = {"from_attributes": True}


class PayrollDeductionResponse(BaseModel):
    id: int
    component_code: str
    name: str
    amount: float

    model_config = {"from_attributes": True}


class PayrollEmployeeResponse(BaseModel):
    id: int
    payroll_run_id: int
    employee_id: int
    total_days: int
    payable_days: float
    gross_salary: float
    taxable_income: float
    employee_statutory: float
    employer_statutory: float
    total_deductions: float
    net_salary: float
    employer_cost: float
    calculation_trace: Dict[str, Any]
    employee: Optional[EmployeeResponse] = None
    earnings: List[PayrollEarningResponse] = []
    deductions: List[PayrollDeductionResponse] = []

    model_config = {"from_attributes": True}


class PayrollRunResponse(BaseModel):
    id: int
    payroll_period_id: int
    total_employees: int
    total_gross: float
    total_deductions: float
    total_net: float
    total_employer_cost: float
    status: str
    executed_by_user_id: Optional[int] = None
    payroll_period: PayrollPeriodResponse
    employee_results: List[PayrollEmployeeResponse] = []

    model_config = {"from_attributes": True}
