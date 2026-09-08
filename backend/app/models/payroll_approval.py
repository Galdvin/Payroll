from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class PayrollApproval(Base):
    """Audit trail for multi-tier payroll run approvals."""
    __tablename__ = "payroll_approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    payroll_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("payroll_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    stage: Mapped[str] = mapped_column(String(50), nullable=False)  # DRAFT, CALCULATED, MANAGER_APPROVED, FINANCE_APPROVED, LOCKED
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # PENDING, APPROVED, REJECTED
    approver_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    payroll_run: Mapped["PayrollRun"] = relationship("PayrollRun")
    approver: Mapped[Optional["User"]] = relationship("User")
