from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
    CompanyCreate,
    CompanyResponse,
    BranchCreate,
    BranchResponse,
    DepartmentCreate,
    DepartmentResponse,
    DesignationCreate,
    DesignationResponse,
    CostCenterCreate,
    CostCenterResponse,
)
from app.services.organization_service import OrganizationService
from app.security.permissions import RequirePermission, get_current_user
from app.models.user import User

router = APIRouter(prefix="/organization", tags=["Organization & Hierarchy"])


# --- Organizations ---
@router.get("", response_model=List[OrganizationResponse], status_code=status.HTTP_200_OK)
def list_organizations(db: Session = Depends(get_db), _: User = Depends(RequirePermission("employee.view"))):
    return OrganizationService.get_organizations(db)


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(body: OrganizationCreate, db: Session = Depends(get_db), _: User = Depends(RequirePermission("employee.create"))):
    return OrganizationService.create_organization(db, body)


# --- Companies ---
@router.get("/companies", response_model=List[CompanyResponse], status_code=status.HTTP_200_OK)
def list_companies(organization_id: int = 1, db: Session = Depends(get_db), _: User = Depends(RequirePermission("employee.view"))):
    return OrganizationService.get_companies(db, organization_id)


@router.post("/companies", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(body: CompanyCreate, db: Session = Depends(get_db), _: User = Depends(RequirePermission("employee.create"))):
    return OrganizationService.create_company(db, body)


# --- Branches ---
@router.get("/branches", response_model=List[BranchResponse], status_code=status.HTTP_200_OK)
def list_branches(company_id: int = 1, db: Session = Depends(get_db), _: User = Depends(RequirePermission("employee.view"))):
    return OrganizationService.get_branches(db, company_id)


@router.post("/branches", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
def create_branch(body: BranchCreate, db: Session = Depends(get_db), _: User = Depends(RequirePermission("employee.create"))):
    return OrganizationService.create_branch(db, body)


# --- Departments ---
@router.get("/departments", response_model=List[DepartmentResponse], status_code=status.HTTP_200_OK)
def list_departments(company_id: int = 1, db: Session = Depends(get_db), _: User = Depends(RequirePermission("employee.view"))):
    return OrganizationService.get_departments(db, company_id)


@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(body: DepartmentCreate, db: Session = Depends(get_db), _: User = Depends(RequirePermission("employee.create"))):
    return OrganizationService.create_department(db, body)


# --- Designations ---
@router.get("/designations", response_model=List[DesignationResponse], status_code=status.HTTP_200_OK)
def list_designations(company_id: int = 1, db: Session = Depends(get_db), _: User = Depends(RequirePermission("employee.view"))):
    return OrganizationService.get_designations(db, company_id)


@router.post("/designations", response_model=DesignationResponse, status_code=status.HTTP_201_CREATED)
def create_designation(body: DesignationCreate, db: Session = Depends(get_db), _: User = Depends(RequirePermission("employee.create"))):
    return OrganizationService.create_designation(db, body)


# --- Cost Centers ---
@router.get("/cost-centers", response_model=List[CostCenterResponse], status_code=status.HTTP_200_OK)
def list_cost_centers(company_id: int = 1, db: Session = Depends(get_db), _: User = Depends(RequirePermission("employee.view"))):
    return OrganizationService.get_cost_centers(db, company_id)


@router.post("/cost-centers", response_model=CostCenterResponse, status_code=status.HTTP_201_CREATED)
def create_cost_center(body: CostCenterCreate, db: Session = Depends(get_db), _: User = Depends(RequirePermission("employee.create"))):
    return OrganizationService.create_cost_center(db, body)
