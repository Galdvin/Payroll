from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, Date, DateTime, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Attendance(Base):
    """Daily attendance log record for an employee."""
    __tablename__ = "attendance"
    __table_args__ = (UniqueConstraint("employee_id", "date", name="uix_employee_attendance_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    check_in: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    check_out: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Statuses: Present, Absent, Half Day, WFH, Holiday, Weekly Off, Unpaid Leave, Paid Leave
    status: Mapped[str] = mapped_column(String(50), default="Present", nullable=False, index=True)
    late_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    early_departure_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    overtime_hours: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0, nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="Manual", nullable=False) # Manual, Biometric, Import


class AttendanceSummary(Base):
    """Monthly attendance aggregation used directly as an input to the payroll calculation engine."""
    __tablename__ = "attendance_summary"
    __table_args__ = (UniqueConstraint("employee_id", "year_month", name="uix_employee_attendance_period"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    year_month: Mapped[str] = mapped_column(String(7), nullable=False, index=True) # e.g. "2024-09"
    total_days: Mapped[int] = mapped_column(Integer, nullable=False)
    present_days: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    absent_days: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    paid_leave_days: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0, nullable=False)
    unpaid_leave_days: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0, nullable=False)
    weekly_off_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    holiday_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    payable_days: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    overtime_hours: Mapped[float] = mapped_column(Numeric(6, 2), default=0.0, nullable=False)
