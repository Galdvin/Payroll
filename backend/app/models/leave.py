from __future__ import annotations
from datetime import date
from typing import Optional, List

from sqlalchemy import String, Integer, Date, Boolean, Numeric, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class LeaveType(Base):
    """Catalog of leave types (Annual, Sick, Casual, Maternity, Paternity, Unpaid, Compensatory)."""
    __tablename__ = "leave_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_encashable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    policies: Mapped[List["LeavePolicy"]] = relationship("LeavePolicy", back_populates="leave_type", cascade="all, delete-orphan")


class LeavePolicy(Base):
    """Leave policy defining quotas and carryover per leave type."""
    __tablename__ = "leave_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    leave_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("leave_types.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    annual_quota: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    accrual_frequency: Mapped[str] = mapped_column(String(50), default="Yearly", nullable=False) # Monthly, Yearly
    max_carry_forward: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0, nullable=False)

    leave_type: Mapped["LeaveType"] = relationship("LeaveType", back_populates="policies")


class LeaveBalance(Base):
    """Leave balance balance sheet per employee per year."""
    __tablename__ = "leave_balances"
    __table_args__ = (UniqueConstraint("employee_id", "leave_type_id", "year", name="uix_employee_leave_balance_year"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    leave_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("leave_types.id", ondelete="CASCADE"), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    accrued: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0, nullable=False)
    used: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0, nullable=False)
    pending: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0, nullable=False)
    total_balance: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0, nullable=False)

    leave_type: Mapped["LeaveType"] = relationship("LeaveType")


class LeaveRequest(Base):
    """Leave application request and approval workflow model."""
    __tablename__ = "leave_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    leave_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("leave_types.id", ondelete="RESTRICT"), nullable=False, index=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_days: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Statuses: Pending, Approved, Rejected, Cancelled
    status: Mapped[str] = mapped_column(String(50), default="Pending", nullable=False, index=True)
    approved_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approval_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    leave_type: Mapped["LeaveType"] = relationship("LeaveType")
