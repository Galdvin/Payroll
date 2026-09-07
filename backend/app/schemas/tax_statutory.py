from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class StatutoryRuleCreate(BaseModel):
    country: str = "India"
    rule_code: str = Field(..., example="IN_PF")
    name: str = Field(..., example="Employee Provident Fund")
    employee_rate: float = Field(..., example=0.1200)
    employer_rate: float = Field(..., example=0.1200)
    wage_ceiling: Optional[float] = 15000.0
    monthly_cap: Optional[float] = 1800.0
    eligibility_threshold: Optional[float] = None
    rule_version: str = "v2024.1"
    effective_date: date
    is_active: bool = True


class StatutoryRuleResponse(StatutoryRuleCreate):
    id: int

    model_config = {"from_attributes": True}


class TaxSlabItem(BaseModel):
    from_income: float
    to_income: Optional[float] = None
    tax_rate: float


class TaxRuleCreate(BaseModel):
    country: str = "India"
    financial_year: str = "2024-2025"
    regime_name: str = "New Regime"
    standard_deduction: float = 75000.0
    cess_rate: float = 0.0400
    rule_version: str = "v2024.1"
    effective_date: date
    is_active: bool = True
    slabs: List[TaxSlabItem] = []


class TaxSlabResponse(BaseModel):
    id: int
    from_income: float
    to_income: Optional[float] = None
    tax_rate: float

    model_config = {"from_attributes": True}


class TaxRuleResponse(BaseModel):
    id: int
    country: str
    financial_year: str
    regime_name: str
    standard_deduction: float
    cess_rate: float
    rule_version: str
    effective_date: date
    is_active: bool
    tax_slabs: List[TaxSlabResponse] = []

    model_config = {"from_attributes": True}


class EvaluateTDSRequest(BaseModel):
    gross_monthly_salary: float
    regime_name: str = "New Regime"
