from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.payroll import (
    PayrollPeriodCreate,
    PayrollPeriodResponse,
    CalculatePayrollRequest,
    PayrollRunResponse,
    PayrollEmployeeResponse,
)
from app.services.payroll_engine_service import PayrollEngineService
from app.security.permissions import RequirePermission, get_current_user
from app.models.user import User

router = APIRouter(prefix="/payroll", tags=["Payroll Engine & Periods"])


@router.get("/periods", response_model=List[PayrollPeriodResponse], status_code=status.HTTP_200_OK)
def list_payroll_periods(company_id: int = 1, db: Session = Depends(get_db), _: User = Depends(RequirePermission("payroll.view"))):
    return PayrollEngineService.get_periods(db, company_id=company_id)


@router.post("/periods", response_model=PayrollPeriodResponse, status_code=status.HTTP_201_CREATED)
def create_payroll_period(body: PayrollPeriodCreate, db: Session = Depends(get_db), _: User = Depends(RequirePermission("payroll.create"))):
    return PayrollEngineService.create_period(db, body)


@router.post("/calculate", response_model=PayrollRunResponse, status_code=status.HTTP_200_OK)
def calculate_payroll(
    body: CalculatePayrollRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll.calculate")),
):
    """Execute the core payroll calculation engine pipeline for a given period."""
    return PayrollEngineService.calculate_payroll_for_period(db, user_id=current_user.id, period_id=body.payroll_period_id)


@router.get("/runs/{run_id}", response_model=PayrollRunResponse, status_code=status.HTTP_200_OK)
def get_payroll_run(run_id: int, db: Session = Depends(get_db), _: User = Depends(RequirePermission("payroll.view"))):
    return PayrollEngineService.get_payroll_run(db, run_id=run_id)


@router.get("/runs/{run_id}/trace/{employee_id}", status_code=status.HTTP_200_OK)
def get_calculation_trace(run_id: int, employee_id: int, db: Session = Depends(get_db), _: User = Depends(RequirePermission("payroll.view"))):
    """Fetch explainable step-by-step mathematical calculation trace tree for an employee."""
    return PayrollEngineService.get_employee_calculation_trace(db, run_id=run_id, employee_id=employee_id)


@router.post("/runs/{run_id}/approve", response_model=PayrollRunResponse, status_code=status.HTTP_200_OK)
def approve_payroll_run(run_id: int, db: Session = Depends(get_db), _: User = Depends(RequirePermission("payroll.approve"))):
    """Approve calculated payroll run."""
    return PayrollEngineService.approve_payroll_run(db, run_id=run_id)


@router.post("/runs/{run_id}/lock", response_model=PayrollRunResponse, status_code=status.HTTP_200_OK)
def lock_payroll_run(run_id: int, db: Session = Depends(get_db), _: User = Depends(RequirePermission("payroll.lock"))):
    """Lock finalized payroll run preventing any future modifications."""
    return PayrollEngineService.lock_payroll_run(db, run_id=run_id)
