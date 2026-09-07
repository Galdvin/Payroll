from typing import List, Optional
from sqlalchemy import String, Integer, Text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Organization(Base):
    """Top-level organizational tenant entity."""
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    tax_identifier: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    country: Mapped[str] = mapped_column(String(100), default="India", nullable=False)

    companies: Mapped[List["Company"]] = relationship("Company", back_populates="organization", cascade="all, delete-orphan")


class Company(Base):
    """Company legal entity under an Organization."""
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    registration_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="companies")
    branches: Mapped[List["Branch"]] = relationship("Branch", back_populates="company", cascade="all, delete-orphan")
    departments: Mapped[List["Department"]] = relationship("Department", back_populates="company", cascade="all, delete-orphan")
    cost_centers: Mapped[List["CostCenter"]] = relationship("CostCenter", back_populates="company", cascade="all, delete-orphan")


class Branch(Base):
    """Branch location of a Company."""
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), default="India", nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Kolkata", nullable=False)

    company: Mapped["Company"] = relationship("Company", back_populates="branches")


class Department(Base):
    """Department model supporting self-referential parent-child hierarchy."""
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_department_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)

    company: Mapped["Company"] = relationship("Company", back_populates="departments")
    parent_department: Mapped[Optional["Department"]] = relationship("Department", remote_side=[id], backref="sub_departments")


class Designation(Base):
    """Job designations and hierarchy grades."""
    __tablename__ = "designations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    grade: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)


class CostCenter(Base):
    """Financial Cost Center for accounting allocation."""
    __tablename__ = "cost_centers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    budget_allocation: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)

    company: Mapped["Company"] = relationship("Company", back_populates="cost_centers")
