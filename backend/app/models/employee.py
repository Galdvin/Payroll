import uuid
from datetime import date
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Date, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Employee(Base):
    """Employee master model containing personal, organizational, financial, and statutory metadata."""
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    employee_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    # Personal Details
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False) # Male, Female, Other
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    nationality: Mapped[str] = mapped_column(String(100), default="Indian", nullable=False)

    # Employment Status
    employment_type: Mapped[str] = mapped_column(String(50), default="Full Time", nullable=False)
    # Statuses: Active, Probation, Notice Period, Suspended, Resigned, Terminated, Retired
    status: Mapped[str] = mapped_column(String(50), default="Active", index=True, nullable=False)
    joining_date: Mapped[date] = mapped_column(Date, nullable=False)
    confirmation_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Organizational Associations
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    branch_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("branches.id", ondelete="SET NULL"), nullable=True, index=True)
    department_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True)
    designation_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("designations.id", ondelete="SET NULL"), nullable=True, index=True)
    cost_center_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("cost_centers.id", ondelete="SET NULL"), nullable=True, index=True)
    reporting_manager_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, index=True)

    # Optional Link to ESS User Account
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Contact & Address
    work_email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    personal_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    emergency_contact: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    address: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Financial & Government Identifiers
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    bank_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    tax_identifier: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # PAN / SSN / National ID
    statutory_identifiers: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True) # PF / ESI / UAN

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Self-referential reporting manager relationship
    reporting_manager: Mapped[Optional["Employee"]] = relationship("Employee", remote_side=[id], backref="direct_reports")
    documents: Mapped[List["EmployeeDocument"]] = relationship("EmployeeDocument", back_populates="employee", cascade="all, delete-orphan")
    history_records: Mapped[List["EmployeeHistory"]] = relationship("EmployeeHistory", back_populates="employee", cascade="all, delete-orphan")


class EmployeeHistory(Base):
    """Audit log table maintaining chronological history of employee status, department, and salary revisions."""
    __tablename__ = "employee_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    change_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. STATUS_CHANGE, PROMOTION, TRANSFER, SALARY_REVISION
    old_values: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    new_values: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    employee: Mapped["Employee"] = relationship("Employee", back_populates="history_records")
