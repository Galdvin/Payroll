from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import PayrollException, ResourceNotFoundException
from app.models.salary import (
    SalaryComponent,
    SalaryStructure,
    StructureComponent,
    EmployeeSalary,
    EmployeeSalaryComponent,
    SalaryRevision,
)
from app.models.employee import Employee, EmployeeHistory
from app.schemas.salary import (
    SalaryComponentCreate,
    SalaryStructureCreate,
    EmployeeSalaryAssign,
    SalaryRevisionCreate,
)

DEFAULT_COMPONENTS = [
    # Earnings
    ("Basic Salary", "BASIC", "Earning", "Fixed", None, None, True, True, True),
    ("House Rent Allowance", "HRA", "Earning", "Percentage", "BASIC", 40.0, True, True, True),
    ("Transport Allowance", "TRANSPORT", "Earning", "Fixed", None, None, True, True, True),
    ("Medical Allowance", "MEDICAL", "Earning", "Fixed", None, None, True, True, True),
    ("Special Allowance", "SPECIAL_ALLOWANCE", "Earning", "Fixed", None, None, True, True, True),
    # Deductions
    ("Employee Provident Fund", "PF_EE", "Deduction", "Percentage", "BASIC", 12.0, False, True, False),
    ("Professional Tax", "PT", "Deduction", "Fixed", None, None, False, True, False),
]


class SalaryService:

    @staticmethod
    def seed_salary_components(db: Session) -> List[SalaryComponent]:
        components = []
        for name, code, c_type, calc_type, base_code, p_val, taxable, stat, prorated in DEFAULT_COMPONENTS:
            comp = db.query(SalaryComponent).filter(SalaryComponent.code == code).first()
            if not comp:
                comp = SalaryComponent(
                    name=name,
                    code=code,
                    component_type=c_type,
                    calculation_type=calc_type,
                    percentage_base_code=base_code,
                    percentage_value=p_val,
                    is_taxable=taxable,
                    is_statutory_applicable=stat,
                    is_prorated=prorated,
                )
                db.add(comp)
                db.flush()
            components.append(comp)
        db.commit()
        return components

    @staticmethod
    def get_components(db: Session) -> List[SalaryComponent]:
        SalaryService.seed_salary_components(db)
        return db.query(SalaryComponent).all()

    @staticmethod
    def create_component(db: Session, data: SalaryComponentCreate) -> SalaryComponent:
        existing = db.query(SalaryComponent).filter(SalaryComponent.code == data.code).first()
        if existing:
            raise PayrollException(f"Salary Component code '{data.code}' already exists.", error_code="COMPONENT_EXISTS")
        comp = SalaryComponent(**data.model_dump())
        db.add(comp)
        db.commit()
        db.refresh(comp)
        return comp

    @staticmethod
    def get_structures(db: Session, company_id: int = 1) -> List[SalaryStructure]:
        return db.query(SalaryStructure).filter(SalaryStructure.company_id == company_id).all()

    @staticmethod
    def create_structure(db: Session, data: SalaryStructureCreate) -> SalaryStructure:
        # Check for duplicate component IDs in request
        comp_ids = [item.component_id for item in data.components]
        if len(comp_ids) != len(set(comp_ids)):
            raise PayrollException("Duplicate component detected in salary structure.", error_code="DUPLICATE_COMPONENT")

        struct = SalaryStructure(
            company_id=data.company_id,
            name=data.name,
            description=data.description,
        )
        db.add(struct)
        db.flush()

        for item in data.components:
            sc = StructureComponent(
                structure_id=struct.id,
                component_id=item.component_id,
                default_amount=item.default_amount,
                default_percentage=item.default_percentage,
            )
            db.add(sc)

        db.commit()
        db.refresh(struct)
        return struct

    # --- Engine CTC Breakdown & Assignment ---
    @staticmethod
    def assign_employee_salary(db: Session, data: EmployeeSalaryAssign) -> EmployeeSalary:
        if data.total_ctc < 0:
            raise PayrollException("Total CTC cannot be negative.", error_code="NEGATIVE_SALARY")

        emp = db.query(Employee).filter(Employee.id == data.employee_id).first()
        if not emp:
            raise ResourceNotFoundException("Employee", data.employee_id)


        SalaryService.seed_salary_components(db)
        comp_map = {c.code: c for c in db.query(SalaryComponent).all()}

        monthly_ctc = data.total_ctc / 12.0

        # Calculate Earnings Breakdown:
        # Basic = 50% of monthly CTC
        monthly_basic = round(monthly_ctc * 0.50, 2)
        # HRA = 40% of Basic
        monthly_hra = round(monthly_basic * 0.40, 2)
        # Transport Allowance
        monthly_transport = 3000.0
        # Medical Allowance
        monthly_medical = 2000.0
        # Special Allowance = Remainder of monthly CTC
        monthly_special = max(0.0, round(monthly_ctc - (monthly_basic + monthly_hra + monthly_transport + monthly_medical), 2))

        gross_salary = monthly_basic + monthly_hra + monthly_transport + monthly_medical + monthly_special

        # Calculate Deductions:
        # PF EE = 12% of Basic capped at 1800
        pf_ee = min(1800.0, round(monthly_basic * 0.12, 2))
        # Professional Tax (PT) = 200
        pt_ee = 200.0 if gross_salary > 15000 else 0.0

        total_deductions = pf_ee + pt_ee
        net_salary = round(gross_salary - total_deductions, 2)

        # Deactivate previous active salary structure if present
        existing_sal = db.query(EmployeeSalary).filter(EmployeeSalary.employee_id == data.employee_id).first()
        if existing_sal:
            db.delete(existing_sal)
            db.flush()

        emp_salary = EmployeeSalary(
            employee_id=data.employee_id,
            salary_structure_id=data.salary_structure_id,
            total_ctc=data.total_ctc,
            gross_salary=gross_salary,
            net_salary=net_salary,
            effective_date=data.effective_date,
            currency=data.currency,
            is_active=True,
        )
        db.add(emp_salary)
        db.flush()

        # Add Component Rows
        earnings_breakdown = [
            ("BASIC", monthly_basic),
            ("HRA", monthly_hra),
            ("TRANSPORT", monthly_transport),
            ("MEDICAL", monthly_medical),
            ("SPECIAL_ALLOWANCE", monthly_special),
            ("PF_EE", pf_ee),
            ("PT", pt_ee),
        ]

        for code, m_amt in earnings_breakdown:
            if code in comp_map:
                c_row = EmployeeSalaryComponent(
                    employee_salary_id=emp_salary.id,
                    component_id=comp_map[code].id,
                    monthly_amount=m_amt,
                    annual_amount=round(m_amt * 12.0, 2),
                )
                db.add(c_row)

        db.commit()
        db.refresh(emp_salary)
        return emp_salary

    @staticmethod
    def get_employee_salary(db: Session, employee_id: int) -> EmployeeSalary:
        sal = db.query(EmployeeSalary).filter(EmployeeSalary.employee_id == employee_id).first()
        if not sal:
            raise ResourceNotFoundException("EmployeeSalary", employee_id)
        return sal

    @staticmethod
    def revise_salary(db: Session, user_id: int, data: SalaryRevisionCreate) -> SalaryRevision:
        current_sal = db.query(EmployeeSalary).filter(EmployeeSalary.employee_id == data.employee_id).first()
        old_ctc = float(current_sal.total_ctc) if current_sal else 0.0
        new_ctc = data.new_ctc

        increment_pct = round(((new_ctc - old_ctc) / old_ctc * 100.0), 2) if old_ctc > 0 else 0.0

        # Log Revision Audit
        rev = SalaryRevision(
            employee_id=data.employee_id,
            effective_date=data.effective_date,
            old_ctc=old_ctc,
            new_ctc=new_ctc,
            increment_percentage=increment_pct,
            revision_reason=data.revision_reason,
            approved_by_user_id=user_id,
        )
        db.add(rev)

        # Re-run CTC assignment engine
        SalaryService.assign_employee_salary(
            db,
            EmployeeSalaryAssign(
                employee_id=data.employee_id,
                total_ctc=new_ctc,
                effective_date=data.effective_date,
            )
        )

        db.commit()
        db.refresh(rev)
        return rev

    @staticmethod
    def get_salary_revisions(db: Session, employee_id: int) -> List[SalaryRevision]:
        return db.query(SalaryRevision).filter(SalaryRevision.employee_id == employee_id).order_by(SalaryRevision.id.desc()).all()

    @staticmethod
    def delete_component(db: Session, component_id: int) -> dict:
        comp = db.query(SalaryComponent).filter(SalaryComponent.id == component_id).first()
        if not comp:
            raise ResourceNotFoundException("SalaryComponent", component_id)
        db.delete(comp)
        db.commit()
        return {"success": True, "message": f"Salary component {component_id} deleted successfully."}

    @staticmethod
    def delete_structure(db: Session, structure_id: int) -> dict:
        struct = db.query(SalaryStructure).filter(SalaryStructure.id == structure_id).first()
        if not struct:
            raise ResourceNotFoundException("SalaryStructure", structure_id)
        db.delete(struct)
        db.commit()
        return {"success": True, "message": f"Salary structure {structure_id} deleted successfully."}
