from __future__ import annotations
from datetime import date
from typing import Optional, List

from sqlalchemy import String, Integer, Date, Boolean, Numeric, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Loan(Base):
    """Employee loan master model."""
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    principal: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    interest_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0, nullable=False) # e.g. 8.5%
    tenure_months: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    monthly_emi: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    outstanding_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    
    # Statuses: Requested, Approved, Active, Settled, Cancelled
    status: Mapped[str] = mapped_column(String(50), default="Requested", nullable=False, index=True)

    transactions: Mapped[List["LoanTransaction"]] = relationship("LoanTransaction", back_populates="loan", cascade="all, delete-orphan")


class LoanTransaction(Base):
    """Repayment transaction history for an employee loan."""
    __tablename__ = "loan_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    loan_id: Mapped[int] = mapped_column(Integer, ForeignKey("loans.id", ondelete="CASCADE"), nullable=False, index=True)
    payroll_run_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("payroll_runs.id", ondelete="SET NULL"), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(50), default="EMI_DEDUCTION", nullable=False) # EMI_DEDUCTION, EARLY_SETTLEMENT
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)

    loan: Mapped["Loan"] = relationship("Loan", back_populates="transactions")


class Advance(Base):
    """Employee salary advance model."""
    __tablename__ = "advances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    request_date: Mapped[date] = mapped_column(Date, nullable=False)
    recovery_months: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    monthly_recovery_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    recovered_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    
    # Statuses: Pending, Approved, Recovering, Fully_Recovered
    status: Mapped[str] = mapped_column(String(50), default="Pending", nullable=False, index=True)


class BonusIncentive(Base):
    """Performance bonus and sales incentive record."""
    __tablename__ = "bonuses_incentives"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="Performance Bonus", nullable=False) # Performance, Annual, Festival, Joining, Sales Incentive
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    is_taxable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    payout_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Statuses: Pending, Included_In_Payroll, Paid
    status: Mapped[str] = mapped_column(String(50), default="Pending", nullable=False, index=True)


class Reimbursement(Base):
    """Expense claim reimbursement header model."""
    __tablename__ = "reimbursements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="Travel", nullable=False) # Travel, Medical, Food, Accommodation, Phone, Other
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    
    # Statuses: Submitted, Manager_Approved, Finance_Approved, Paid, Rejected
    status: Mapped[str] = mapped_column(String(50), default="Submitted", nullable=False, index=True)
    
    manager_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    finance_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    items: Mapped[List["ReimbursementItem"]] = relationship("ReimbursementItem", back_populates="reimbursement", cascade="all, delete-orphan")


class ReimbursementItem(Base):
    """Itemized expense line with receipt file attachment."""
    __tablename__ = "reimbursement_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reimbursement_id: Mapped[int] = mapped_column(Integer, ForeignKey("reimbursements.id", ondelete="CASCADE"), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    receipt_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    receipt_file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    reimbursement: Mapped["Reimbursement"] = relationship("Reimbursement", back_populates="items")
