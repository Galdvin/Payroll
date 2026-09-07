from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class SalaryComponentCreate(BaseModel):
    name: str = Field(..., example="Basic Salary")
    code: str = Field(..., example="BASIC")
    component_type: str = Field(..., example="Earning") # Earning, Deduction
    calculation_type: str = Field("Fixed", example="Percentage") # Fixed, Percentage, Formula
    percentage_base_code: Optional[str] = None
    percentage_value: Optional[float] = None
    formula_expression: Optional[str] = None
    frequency: str = "Monthly"
    is_taxable: bool = True
    is_statutory_applicable: bool = True
    is_prorated: bool = True
    rounding_rule: str = "Nearest"
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None


class SalaryComponentResponse(SalaryComponentCreate):
    id: int

    model_config = {"from_attributes": True}


class StructureComponentItem(BaseModel):
    component_id: int
    default_amount: Optional[float] = None
    default_percentage: Optional[float] = None


class SalaryStructureCreate(BaseModel):
    company_id: int
    name: str
    description: Optional[str] = None
    components: List[StructureComponentItem] = []


class SalaryStructureResponse(BaseModel):
    id: int
    company_id: int
    name: str
    description: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}


class EmployeeSalaryAssign(BaseModel):
    employee_id: int
    salary_structure_id: Optional[int] = None
    total_ctc: float = Field(..., example=600000.0) # Annual CTC
    effective_date: date
    currency: str = "INR"


class EmployeeSalaryComponentResponse(BaseModel):
    id: int
    component_id: int
    monthly_amount: float
    annual_amount: float
    component: SalaryComponentResponse

    model_config = {"from_attributes": True}


class EmployeeSalaryResponse(BaseModel):
    id: int
    employee_id: int
    salary_structure_id: Optional[int] = None
    total_ctc: float
    gross_salary: float
    net_salary: float
    effective_date: date
    currency: str
    is_active: bool
    assigned_components: List[EmployeeSalaryComponentResponse] = []

    model_config = {"from_attributes": True}


class SalaryRevisionCreate(BaseModel):
    employee_id: int
    new_ctc: float
    effective_date: date
    revision_reason: Optional[str] = None


class SalaryRevisionResponse(BaseModel):
    id: int
    employee_id: int
    effective_date: date
    old_ctc: float
    new_ctc: float
    increment_percentage: float
    revision_reason: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
