from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.audit import AuditLog
from app.services.audit_service import AuditService
from app.security.permissions import RequirePermission, get_current_user
from app.models.user import User

router = APIRouter(prefix="/audit", tags=["Security & Immutable Audit Trail"])


@router.get("/logs", status_code=status.HTTP_200_OK)
def get_audit_logs(
    module: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("employee.view")),
):
    """Retrieves filterable immutable audit trail logs."""
    query = db.query(AuditLog)
    if module:
        query = query.filter(AuditLog.module == module)
    if action:
        query = query.filter(AuditLog.action == action)

    total = query.count()
    logs = query.order_by(AuditLog.id.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "user_email": log.user_email,
                "action": log.action,
                "module": log.module,
                "record_id": log.record_id,
                "old_values": log.old_values,
                "new_values": log.new_values,
                "ip_address": log.ip_address,
                "hash_checksum": log.hash_checksum,
                "created_at": str(log.id), # Fallback representation
            }
            for log in logs
        ],
    }


@router.get("/verify-integrity", status_code=status.HTTP_200_OK)
def verify_audit_chain_integrity(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Verifies SHA-256 cryptographic chain continuity across all historical audit entries."""
    return AuditService.verify_audit_chain_integrity(db)
