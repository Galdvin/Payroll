from __future__ import annotations
from typing import Optional, Dict, Any

from sqlalchemy import String, Integer, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class AuditLog(Base):
    """Immutable record for tracking all critical system, security, and financial operations."""
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    user_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    action: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    module: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    record_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    old_values: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    new_values: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prev_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    hash_checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

