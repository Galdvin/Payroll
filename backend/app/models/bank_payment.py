from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Integer, Date, Numeric, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class BankPaymentBatch(Base):
    """Batch file tracking for corporate bank salary disbursement."""
    __tablename__ = "bank_payment_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    payroll_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("payroll_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    bank_format: Mapped[str] = mapped_column(String(50), nullable=False) # HDFC_CMS, ICICI_CIB, SBI_CMP, ISO20022
    total_records: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0, nullable=False)
    checksum_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="GENERATED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    payroll_run = relationship("PayrollRun")


class JournalEntry(Base):
    """Double-entry General Ledger (GL) accounting entry."""
    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    payroll_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("payroll_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    account_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    account_name: Mapped[str] = mapped_column(String(150), nullable=False)
    debit_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0, nullable=False)
    credit_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0, nullable=False)
    narration: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    payroll_run = relationship("PayrollRun")
