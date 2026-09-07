import hashlib
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.audit import AuditLog


class AuditService:

    @staticmethod
    def log_action(
        db: Session,
        action: str,
        module: str,
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
        record_id: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Records an action in the cryptographic SHA-256 tamper-evident audit trail."""
        last_log = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
        prev_hash = last_log.hash_checksum if (last_log and last_log.hash_checksum) else "0" * 64

        payload = f"{prev_hash}|{user_id}|{user_email}|{action}|{module}|{record_id}|{str(old_values)}|{str(new_values)}"
        checksum = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        entry = AuditLog(
            user_id=user_id,
            user_email=user_email,
            action=action,
            module=module,
            record_id=str(record_id) if record_id else None,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            prev_hash=prev_hash,
            hash_checksum=checksum,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def verify_audit_chain_integrity(db: Session) -> Dict[str, Any]:
        """Iterates through all historical audit log entries and verifies SHA-256 chain continuity."""
        logs = db.query(AuditLog).order_by(AuditLog.id.asc()).all()
        if not logs:
            return {"is_intact": True, "total_entries": 0, "tampered_entry_id": None}

        current_prev_hash = "0" * 64
        for log in logs:
            payload = f"{current_prev_hash}|{log.user_id}|{log.user_email}|{log.action}|{log.module}|{log.record_id}|{str(log.old_values)}|{str(log.new_values)}"
            expected_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

            if log.hash_checksum != expected_hash:
                return {
                    "is_intact": False,
                    "total_entries": len(logs),
                    "tampered_entry_id": log.id,
                    "reason": f"Hash mismatch at audit entry ID {log.id}",
                }
            current_prev_hash = log.hash_checksum

        return {"is_intact": True, "total_entries": len(logs), "tampered_entry_id": None}

    @staticmethod
    def mask_pii(value: str) -> str:
        """Utility for masking PII data like Bank Account numbers or PANs."""
        if not value or len(value) < 4:
            return "****"
        return "*" * (len(value) - 4) + value[-4:]
