from datetime import date
from typing import Optional, List
from sqlalchemy import String, Integer, Date, Boolean, Numeric, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class StatutoryRule(Base):
    """Versioned statutory contribution rule configuration (PF, ESI, PT, UAE Pension)."""
    __tablename__ = "statutory_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    country: Mapped[str] = mapped_column(String(100), default="India", nullable=False, index=True)
    rule_code: Mapped[str] = mapped_column(String(50), index=True, nullable=False) # IN_PF, IN_ESI, IN_PT, UAE_PENSION
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    
    employee_rate: Mapped[float] = mapped_column(Numeric(6, 4), default=0.0, nullable=False) # e.g. 0.1200 for 12%
    employer_rate: Mapped[float] = mapped_column(Numeric(6, 4), default=0.0, nullable=False) # e.g. 0.1200 for 12%
    
    wage_ceiling: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True) # e.g. 15000.00 for PF
    monthly_cap: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True) # e.g. 1800.00 for PF
    eligibility_threshold: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True) # e.g. 21000.00 for ESI
    
    rule_version: Mapped[str] = mapped_column(String(50), default="v2024.1", nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class TaxRule(Base):
    """Versioned income tax regime configuration (Old Regime vs New Regime)."""
    __tablename__ = "tax_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    country: Mapped[str] = mapped_column(String(100), default="India", nullable=False, index=True)
    financial_year: Mapped[str] = mapped_column(String(20), nullable=False, index=True) # e.g. "2024-2025"
    regime_name: Mapped[str] = mapped_column(String(50), nullable=False) # "New Regime", "Old Regime"
    
    standard_deduction: Mapped[float] = mapped_column(Numeric(12, 2), default=75000.0, nullable=False)
    cess_rate: Mapped[float] = mapped_column(Numeric(6, 4), default=0.0400, nullable=False) # 4% Health & Education Cess
    
    rule_version: Mapped[str] = mapped_column(String(50), default="v2024.1", nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    tax_slabs: Mapped[List["TaxSlab"]] = relationship("TaxSlab", back_populates="tax_rule", cascade="all, delete-orphan")


class TaxSlab(Base):
    """Progressive income tax slab for a tax regime."""
    __tablename__ = "tax_slabs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tax_rule_id: Mapped[int] = mapped_column(Integer, ForeignKey("tax_rules.id", ondelete="CASCADE"), nullable=False, index=True)
    
    from_income: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    to_income: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True) # Null for upper slab
    tax_rate: Mapped[float] = mapped_column(Numeric(6, 4), nullable=False) # e.g. 0.05 for 5%

    tax_rule: Mapped["TaxRule"] = relationship("TaxRule", back_populates="tax_slabs")
