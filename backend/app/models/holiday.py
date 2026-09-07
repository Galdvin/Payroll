from datetime import date
from typing import Optional
from sqlalchemy import String, Integer, Date, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Holiday(Base):
    """Company and branch holiday calendar model."""
    __tablename__ = "holidays"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    branch_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("branches.id", ondelete="CASCADE"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    holiday_type: Mapped[str] = mapped_column(String(50), default="National", nullable=False) # National, Regional, Custom
    is_optional: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
