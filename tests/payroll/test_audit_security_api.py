import pytest
from app.services.audit_service import AuditService


def test_audit_log_recording_and_chain_integrity(client, admin_headers, db):
    # 1. Manually trigger cryptographic audit logs
    entry1 = AuditService.log_action(
        db,
        action="PAYROLL_CALCULATE",
        module="PAYROLL",
        user_id=1,
        user_email="admin@payroll.com",
        record_id="RUN-1",
        new_values={"status": "Calculated", "gross": 150000.0},
    )
    assert entry1.hash_checksum is not None
    assert len(entry1.hash_checksum) == 64

    entry2 = AuditService.log_action(
        db,
        action="LOAN_APPROVE",
        module="FINANCIAL_EXTRAS",
        user_id=1,
        user_email="admin@payroll.com",
        record_id="LN-5",
        new_values={"status": "APPROVED", "emi": 12500.0},
    )
    assert entry2.prev_hash == entry1.hash_checksum

    # 2. Test Audit Log API endpoint
    logs_resp = client.get("/api/v1/audit/logs", headers=admin_headers)
    assert logs_resp.status_code == 200
    logs_data = logs_resp.json()
    assert logs_data["total"] >= 2
    assert len(logs_data["logs"]) >= 2

    # 3. Test Cryptographic SHA-256 Chain Integrity Verification API
    verify_resp = client.get("/api/v1/audit/verify-integrity", headers=admin_headers)
    assert verify_resp.status_code == 200
    v_data = verify_resp.json()
    assert v_data["is_intact"] is True
    assert v_data["tampered_entry_id"] is None

    # 4. Test PII Data Masking helper
    masked_acc = AuditService.mask_pii("987654321012")
    assert masked_acc == "********1012"
    masked_pan = AuditService.mask_pii("ABCDE1234F")
    assert masked_pan == "******234F"
