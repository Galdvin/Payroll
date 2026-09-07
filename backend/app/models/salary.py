from datetime import date
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Integer, Date, Boolean, Numeric, ForeignKey, Text, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class SalaryComponent(Base):
    """Configurable salary component catalog (Earnings & Deductions)."""
    __tablename__ = "salary_components"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    # Types: Earning, Deduction
    component_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # Calculation Types: Fixed, Percentage, Formula
    calculation_type: Mapped[str] = mapped_column(String(20), default="Fixed", nullable=False)
    
    percentage_base_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # e.g. "BASIC"
    percentage_value: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True) # e.g. 40.0 for 40%
    formula_expression: Mapped[Optional[str]] = mapped_column(String(255), nullable=True) # e.g. "BASIC * 0.40"
    
    frequency: Mapped[str] = mapped_column(String(20), default="Monthly", nullable=False) # Monthly, Daily, Hourly
    is_taxable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_statutory_applicable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False) # PF / ESI applicability
    is_prorated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False) # Scales with payable days
    rounding_rule: Mapped[str] = mapped_column(String(20), default="Nearest", nullable=False) # Nearest, Up, Down, None
    min_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    max_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)


class SalaryStructure(Base):
    """Salary Structure template grouping components."""
    __tablename__ = "salary_structures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    structure_components: Mapped[List["StructureComponent"]] = relationship("StructureComponent", back_populates="salary_structure", cascade="all, delete-orphan")


class StructureComponent(Base):
    """Junction linking SalaryStructure to SalaryComponent with default amounts/percentages."""
    __tablename__ = "structure_components"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    structure_id: Mapped[int] = mapped_column(Integer, ForeignKey("salary_structures.id", ondelete="CASCADE"), nullable=False, index=True)
    component_id: Mapped[int] = mapped_column(Integer, ForeignKey("salary_components.id", ondelete="CASCADE"), nullable=False, index=True)
    default_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    default_percentage: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)

    salary_structure: Mapped["SalaryStructure"] = relationship("SalaryStructure", back_populates="structure_components")
    component: Mapped["SalaryComponent"] = relationship("SalaryComponent")


class EmployeeSalary(Base):
    """Active salary structure assigned to an employee."""
    __tablename__ = "employee_salary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    salary_structure_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("salary_structures.id", ondelete="SET NULL"), nullable=True)
    
    total_ctc: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    gross_salary: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    net_salary: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    assigned_components: Mapped[List["EmployeeSalaryComponent"]] = relationship("EmployeeSalaryComponent", back_populates="employee_salary", cascade="all, delete-orphan")


class EmployeeSalaryComponent(Base):
    """Calculated breakdown of individual components for an employee's salary."""
    __tablename__ = "employee_salary_components"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_salary_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee_salary.id", ondelete="CASCADE"), nullable=False, index=True)
    component_id: Mapped[int] = mapped_column(Integer, ForeignKey("salary_components.id", ondelete="RESTRICT"), nullable=False, index=True)
    monthly_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    annual_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    employee_salary: Mapped["EmployeeSalary"] = relationship("EmployeeSalary", back_populates="assigned_components")
    component: Mapped["SalaryComponent"] = relationship("SalaryComponent")


class SalaryRevision(Base):
    """Historical record tracking salary increments, promotions, and CTC revisions."""
    __tablename__ = "salary_revisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    old_ctc: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    new_ctc: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    increment_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    revision_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approved_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
