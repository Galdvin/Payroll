from __future__ import annotations
from datetime import time, date
from typing import Optional, List

from sqlalchemy import String, Integer, Time, Boolean, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Shift(Base):
    """Work shift configuration model (General, Night, Rotational)."""
    __tablename__ = "shifts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    grace_period_minutes: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    break_duration_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    is_night_shift: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    overtime_start_after_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)

    assignments: Mapped[List["ShiftAssignment"]] = relationship("ShiftAssignment", back_populates="shift", cascade="all, delete-orphan")


class ShiftAssignment(Base):
    """Assignment of a shift to an employee."""
    __tablename__ = "shift_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    shift_id: Mapped[int] = mapped_column(Integer, ForeignKey("shifts.id", ondelete="CASCADE"), nullable=False, index=True)
    effective_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    effective_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    shift: Mapped["Shift"] = relationship("Shift", back_populates="assignments")
