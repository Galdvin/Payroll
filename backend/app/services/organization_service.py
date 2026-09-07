from typing import List
from sqlalchemy.orm import Session
from app.core.exceptions import PayrollException, ResourceNotFoundException
from app.models.organization import (
    Organization,
    Company,
    Branch,
    Department,
    Designation,
    CostCenter,
)
from app.schemas.organization import (
    OrganizationCreate,
    CompanyCreate,
    BranchCreate,
    DepartmentCreate,
    DesignationCreate,
    CostCenterCreate,
)


class OrganizationService:

    # --- Organization ---
    @staticmethod
    def get_organizations(db: Session) -> List[Organization]:
        return db.query(Organization).all()

    @staticmethod
    def create_organization(db: Session, data: OrganizationCreate) -> Organization:
        existing = db.query(Organization).filter(Organization.code == data.code).first()
        if existing:
            raise PayrollException(f"Organization code '{data.code}' already exists.", error_code="ORG_CODE_EXISTS")
        org = Organization(**data.model_dump())
        db.add(org)
        db.commit()
        db.refresh(org)
        return org

    # --- Company ---
    @staticmethod
    def get_companies(db: Session, organization_id: int) -> List[Company]:
        return db.query(Company).filter(Company.organization_id == organization_id).all()

    @staticmethod
    def create_company(db: Session, data: CompanyCreate) -> Company:
        company = Company(**data.model_dump())
        db.add(company)
        db.commit()
        db.refresh(company)
        return company

    # --- Branch ---
    @staticmethod
    def get_branches(db: Session, company_id: int) -> List[Branch]:
        return db.query(Branch).filter(Branch.company_id == company_id).all()

    @staticmethod
    def create_branch(db: Session, data: BranchCreate) -> Branch:
        branch = Branch(**data.model_dump())
        db.add(branch)
        db.commit()
        db.refresh(branch)
        return branch

    # --- Department ---
    @staticmethod
    def get_departments(db: Session, company_id: int) -> List[Department]:
        return db.query(Department).filter(Department.company_id == company_id).all()

    @staticmethod
    def create_department(db: Session, data: DepartmentCreate) -> Department:
        dept = Department(**data.model_dump())
        db.add(dept)
        db.commit()
        db.refresh(dept)
        return dept

    # --- Designation ---
    @staticmethod
    def get_designations(db: Session, company_id: int) -> List[Designation]:
        return db.query(Designation).filter(Designation.company_id == company_id).all()

    @staticmethod
    def create_designation(db: Session, data: DesignationCreate) -> Designation:
        desig = Designation(**data.model_dump())
        db.add(desig)
        db.commit()
        db.refresh(desig)
        return desig

    # --- CostCenter ---
    @staticmethod
    def get_cost_centers(db: Session, company_id: int) -> List[CostCenter]:
        return db.query(CostCenter).filter(CostCenter.company_id == company_id).all()

    @staticmethod
    def create_cost_center(db: Session, data: CostCenterCreate) -> CostCenter:
        cc = CostCenter(**data.model_dump())
        db.add(cc)
        db.commit()
        db.refresh(cc)
        return cc
