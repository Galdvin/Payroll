from __future__ import annotations
from datetime import date
from typing import Optional, Dict, Any

from sqlalchemy import String, Integer, Date, Numeric, ForeignKey, Text, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class FnfSettlement(Base):
    """Full & Final (F&F) Settlement model tracking employee exit calculations."""
    __tablename__ = "fnf_settlements"
    __table_args__ = (UniqueConstraint("employee_id", name="uix_employee_fnf_settlement"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    resignation_date: Mapped[date] = mapped_column(Date, nullable=False)
    last_working_date: Mapped[date] = mapped_column(Date, nullable=False)
    settlement_date: Mapped[date] = mapped_column(Date, nullable=False)
    settlement_reason: Mapped[str] = mapped_column(String(50), default="Resignation", nullable=False) # Resignation, Termination, Retirement

    # Earnings & Credits
    pending_salary_days: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0, nullable=False)
    pending_salary_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    
    leave_encashment_days: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0, nullable=False)
    leave_encashment_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    
    notice_pay_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False) # Company pays employee
    bonus_settlement_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    gratuity_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    
    gross_settlement_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)

    # Deductions & Recoveries
    notice_recovery_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False) # Employee short notice recovery
    outstanding_loan_deduction: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    outstanding_advance_deduction: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    
    total_deductions_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    net_settlement_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)

    # Statuses: Draft, Calculated, Approved, Paid
    status: Mapped[str] = mapped_column(String(50), default="Calculated", nullable=False, index=True)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    calculation_trace: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

    employee: Mapped["Employee"] = relationship("Employee")
