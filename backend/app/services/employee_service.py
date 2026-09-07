from datetime import date
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.exceptions import PayrollException, ResourceNotFoundException
from app.models.employee import Employee, EmployeeHistory
from app.models.document import EmployeeDocument
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


class EmployeeService:

    @staticmethod
    def get_employees(
        db: Session,
        organization_id: Optional[int] = None,
        department_id: Optional[int] = None,
        status: Optional[str] = None,
        employment_type: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Employee], int]:
        query = db.query(Employee)

        if organization_id:
            query = query.filter(Employee.organization_id == organization_id)
        if department_id:
            query = query.filter(Employee.department_id == department_id)
        if status:
            query = query.filter(Employee.status == status)
        if employment_type:
            query = query.filter(Employee.employment_type == employment_type)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Employee.employee_code.ilike(search_pattern),
                    Employee.first_name.ilike(search_pattern),
                    Employee.last_name.ilike(search_pattern),
                    Employee.work_email.ilike(search_pattern),
                )
            )

        total = query.count()
        employees = query.order_by(Employee.id.desc()).offset(skip).limit(limit).all()
        return employees, total

    @staticmethod
    def get_by_id(db: Session, employee_id: int) -> Employee:
        emp = db.query(Employee).filter(Employee.id == employee_id).first()
        if not emp:
            raise ResourceNotFoundException("Employee", employee_id)
        return emp

    @staticmethod
    def create_employee(db: Session, data: EmployeeCreate) -> Employee:
        # Check employee code uniqueness
        existing_code = db.query(Employee).filter(Employee.employee_code == data.employee_code).first()
        if existing_code:
            raise PayrollException(f"Employee Code '{data.employee_code}' is already registered.", error_code="EMP_CODE_EXISTS")

        # Check work email uniqueness
        existing_email = db.query(Employee).filter(Employee.work_email == data.work_email).first()
        if existing_email:
            raise PayrollException(f"Work Email '{data.work_email}' is already registered.", error_code="WORK_EMAIL_EXISTS")

        dump = data.model_dump()

        # Handle nested Pydantic models for JSON fields
        if dump.get("bank_details"):
            dump["bank_details"] = data.bank_details.model_dump()
        if dump.get("address"):
            dump["address"] = data.address.model_dump()
        if dump.get("emergency_contact"):
            dump["emergency_contact"] = data.emergency_contact.model_dump()

        employee = Employee(**dump)
        db.add(employee)
        db.flush()

        # Log initial creation in EmployeeHistory
        history = EmployeeHistory(
            employee_id=employee.id,
            effective_date=employee.joining_date,
            change_type="INITIAL_JOINING",
            new_values={"status": employee.status, "department_id": employee.department_id},
            remarks=f"Employee {employee.first_name} {employee.last_name} joined organization."
        )
        db.add(history)

        db.commit()
        db.refresh(employee)
        return employee

    @staticmethod
    def update_employee(db: Session, employee_id: int, data: EmployeeUpdate) -> Employee:
        employee = EmployeeService.get_by_id(db, employee_id)

        update_dict = data.model_dump(exclude_unset=True)
        old_state = {
            "status": employee.status,
            "department_id": employee.department_id,
            "designation_id": employee.designation_id,
            "work_email": employee.work_email,
        }

        # Convert nested Pydantic schemas to dict if present
        if "bank_details" in update_dict and data.bank_details is not None:
            update_dict["bank_details"] = data.bank_details.model_dump()
        if "address" in update_dict and data.address is not None:
            update_dict["address"] = data.address.model_dump()
        if "emergency_contact" in update_dict and data.emergency_contact is not None:
            update_dict["emergency_contact"] = data.emergency_contact.model_dump()

        for key, val in update_dict.items():
            setattr(employee, key, val)

        # Record history if critical attributes changed
        new_state = {
            "status": employee.status,
            "department_id": employee.department_id,
            "designation_id": employee.designation_id,
            "work_email": employee.work_email,
        }
        if old_state != new_state:
            history = EmployeeHistory(
                employee_id=employee.id,
                effective_date=date.today(),
                change_type="PROFILE_UPDATE",
                old_values=old_state,
                new_values=new_state,
                remarks="Employee profile updated."
            )
            db.add(history)

        db.commit()
        db.refresh(employee)
        return employee

    @staticmethod
    def get_employee_history(db: Session, employee_id: int) -> List[EmployeeHistory]:
        EmployeeService.get_by_id(db, employee_id)
        return db.query(EmployeeHistory).filter(EmployeeHistory.employee_id == employee_id).order_by(EmployeeHistory.id.desc()).all()

    @staticmethod
    def add_employee_document(
        db: Session,
        employee_id: int,
        document_type: str,
        title: str,
        file_path: str,
        file_size: int,
        mime_type: str = "application/pdf",
        uploaded_by_user_id: Optional[int] = None,
    ) -> EmployeeDocument:
        EmployeeService.get_by_id(db, employee_id)
        doc = EmployeeDocument(
            employee_id=employee_id,
            document_type=document_type,
            title=title,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            uploaded_by_user_id=uploaded_by_user_id,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    @staticmethod
    def get_employee_documents(db: Session, employee_id: int) -> List[EmployeeDocument]:
        EmployeeService.get_by_id(db, employee_id)
        return db.query(EmployeeDocument).filter(EmployeeDocument.employee_id == employee_id).all()
