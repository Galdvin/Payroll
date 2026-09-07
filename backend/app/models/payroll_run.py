from datetime import date
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Integer, Date, Boolean, Numeric, ForeignKey, Text, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class PayrollPeriod(Base):
    """Payroll period definition (e.g. September 2024)."""
    __tablename__ = "payroll_periods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    year_month: Mapped[str] = mapped_column(String(7), unique=True, index=True, nullable=False) # e.g. "2024-09"
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    cutoff_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Statuses: Draft, Open, Locked, Closed
    status: Mapped[str] = mapped_column(String(50), default="Open", nullable=False, index=True)

    runs: Mapped[List["PayrollRun"]] = relationship("PayrollRun", back_populates="payroll_period", cascade="all, delete-orphan")


class PayrollRun(Base):
    """Execution batch for a payroll calculation run."""
    __tablename__ = "payroll_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    payroll_period_id: Mapped[int] = mapped_column(Integer, ForeignKey("payroll_periods.id", ondelete="CASCADE"), nullable=False, index=True)
    total_employees: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_gross: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0, nullable=False)
    total_deductions: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0, nullable=False)
    total_net: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0, nullable=False)
    total_employer_cost: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0, nullable=False)
    
    # Lifecycle Statuses: Draft, Attendance Review, Calculated, Validated, Approved, Locked, Paid
    status: Mapped[str] = mapped_column(String(50), default="Calculated", nullable=False, index=True)
    executed_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    payroll_period: Mapped["PayrollPeriod"] = relationship("PayrollPeriod", back_populates="runs")
    employee_results: Mapped[List["PayrollEmployee"]] = relationship("PayrollEmployee", back_populates="payroll_run", cascade="all, delete-orphan")


class PayrollEmployee(Base):
    """Calculated payroll row for a specific employee including mandatory calculation trace tree."""
    __tablename__ = "payroll_employees"
    __table_args__ = (UniqueConstraint("payroll_run_id", "employee_id", name="uix_run_employee"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    payroll_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("payroll_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    
    total_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    payable_days: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    
    gross_salary: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    taxable_income: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    employee_statutory: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    employer_statutory: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    total_deductions: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    net_salary: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    employer_cost: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    # Mandatory Explainable Step-by-Step Mathematical Calculation Trace Tree
    calculation_trace: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

    payroll_run: Mapped["PayrollRun"] = relationship("PayrollRun", back_populates="employee_results")
    employee: Mapped["Employee"] = relationship("Employee")
    earnings: Mapped[List["PayrollEarning"]] = relationship("PayrollEarning", back_populates="payroll_employee", cascade="all, delete-orphan")
    deductions: Mapped[List["PayrollDeduction"]] = relationship("PayrollDeduction", back_populates="payroll_employee", cascade="all, delete-orphan")


class PayrollEarning(Base):
    """Itemized earning component result."""
    __tablename__ = "payroll_earnings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    payroll_employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("payroll_employees.id", ondelete="CASCADE"), nullable=False, index=True)
    component_code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    full_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    prorated_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    payroll_employee: Mapped["PayrollEmployee"] = relationship("PayrollEmployee", back_populates="earnings")


class PayrollDeduction(Base):
    """Itemized deduction component result."""
    __tablename__ = "payroll_deductions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    payroll_employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("payroll_employees.id", ondelete="CASCADE"), nullable=False, index=True)
    component_code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    payroll_employee: Mapped["PayrollEmployee"] = relationship("PayrollEmployee", back_populates="deductions")
