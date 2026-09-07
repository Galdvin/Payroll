from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.salary import (
    SalaryComponentCreate,
    SalaryComponentResponse,
    SalaryStructureCreate,
    SalaryStructureResponse,
    EmployeeSalaryAssign,
    EmployeeSalaryResponse,
    SalaryRevisionCreate,
    SalaryRevisionResponse,
)
from app.services.salary_service import SalaryService
from app.security.permissions import RequirePermission, get_current_user
from app.models.user import User

router = APIRouter(prefix="/salary", tags=["Salary Engine & Components"])


@router.get("/components", response_model=List[SalaryComponentResponse], status_code=status.HTTP_200_OK)
def list_components(db: Session = Depends(get_db), _: User = Depends(RequirePermission("salary.view"))):
    return SalaryService.get_components(db)


@router.post("/components", response_model=SalaryComponentResponse, status_code=status.HTTP_201_CREATED)
def create_component(body: SalaryComponentCreate, db: Session = Depends(get_db), _: User = Depends(RequirePermission("salary.update"))):
    return SalaryService.create_component(db, body)


@router.get("/structures", response_model=List[SalaryStructureResponse], status_code=status.HTTP_200_OK)
def list_structures(company_id: int = 1, db: Session = Depends(get_db), _: User = Depends(RequirePermission("salary.view"))):
    return SalaryService.get_structures(db, company_id=company_id)


@router.post("/structures", response_model=SalaryStructureResponse, status_code=status.HTTP_201_CREATED)
def create_structure(body: SalaryStructureCreate, db: Session = Depends(get_db), _: User = Depends(RequirePermission("salary.update"))):
    return SalaryService.create_structure(db, body)


@router.post("/assign", response_model=EmployeeSalaryResponse, status_code=status.HTTP_200_OK)
def assign_salary(body: EmployeeSalaryAssign, db: Session = Depends(get_db), _: User = Depends(RequirePermission("salary.update"))):
    """Assign CTC to employee and compute detailed earnings/deductions breakdown."""
    return SalaryService.assign_employee_salary(db, body)


@router.get("/employee/{employee_id}", response_model=EmployeeSalaryResponse, status_code=status.HTTP_200_OK)
def get_employee_salary(employee_id: int, db: Session = Depends(get_db), _: User = Depends(RequirePermission("salary.view"))):
    return SalaryService.get_employee_salary(db, employee_id=employee_id)


@router.post("/revisions", response_model=SalaryRevisionResponse, status_code=status.HTTP_201_CREATED)
def revise_salary(
    body: SalaryRevisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("salary.update")),
):
    """Revise employee CTC, calculate increment %, re-run breakdown engine, and audit revision."""
    return SalaryService.revise_salary(db, user_id=current_user.id, data=body)


@router.get("/revisions/{employee_id}", response_model=List[SalaryRevisionResponse], status_code=status.HTTP_200_OK)
def list_salary_revisions(employee_id: int, db: Session = Depends(get_db), _: User = Depends(RequirePermission("salary.view"))):
    return SalaryService.get_salary_revisions(db, employee_id=employee_id)
