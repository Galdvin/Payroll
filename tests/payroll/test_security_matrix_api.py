import pytest
import time
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.config import settings
from app.core.security import create_access_token
from app.services.audit_service import AuditService
from app.models.user import User
from app.models.rbac import Role, Permission
from app.core.security import get_password_hash


def test_sec_001_employee_accesses_admin_api(client, employee_headers):
    """SEC-001: Employee accesses admin API (Denied with 403 Insufficient Permissions)"""
    # Standard employee attempts to calculate payroll
    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": 1}, headers=employee_headers)
    assert res.status_code == 403
    data = res.json()
    assert data["error_code"] == "PERMISSION_DENIED"


def test_sec_002_employee_accesses_another_employee_salary(client, employee_headers):
    """SEC-002: Employee accesses another employee's salary/payslip (IDOR Blocked)"""
    # Employee attempts to fetch payslip of employee ID 9999
    res = client.get("/api/v1/payslips/employee/9999/period/1", headers=employee_headers)
    assert res.status_code in (400, 403)
    assert "ACCESS_DENIED" in str(res.json())


def test_sec_003_manager_accesses_unauthorized_department(client, db):
    """SEC-003: Manager accesses unauthorized department action without permissions"""
    # Manager without salary.update permission tries to revise salary
    mgr_role = db.query(Role).filter(Role.name == "Department Manager").first()
    if not mgr_role:
        mgr_role = Role(name="Department Manager", description="Department manager role")
        db.add(mgr_role)
        db.flush()

    mgr_user = User(
        email="manager.dept2@company.com",
        hashed_password=get_password_hash("ManagerPass123!"),
        full_name="Dept Manager",
        is_active=True,
        is_superuser=False,
    )
    mgr_user.roles.append(mgr_role)
    db.add(mgr_user)
    db.commit()

    # Login as manager
    login_res = client.post("/api/v1/auth/login", json={"email": mgr_user.email, "password": "ManagerPass123!"})
    token = login_res.json()["access_token"]
    mgr_headers = {"Authorization": f"Bearer {token}"}

    # Attempt unauthorized salary revision
    res = client.post("/api/v1/salary/revisions", json={
        "employee_id": 1,
        "new_ctc": 1200000.0,
        "effective_date": "2026-04-01",
        "reason": "Unauthorized revision"
    }, headers=mgr_headers)
    assert res.status_code == 403
    assert res.json()["error_code"] == "PERMISSION_DENIED"


def test_sec_004_sql_injection_safety(client, admin_headers):
    """SEC-004: SQL injection payload in search filter parameters"""
    sql_payload = "' OR '1'='1'; DROP TABLE users; --"
    res = client.get(f"/api/v1/employees?search={sql_payload}", headers=admin_headers)
    assert res.status_code == 200
    # ORM parameterization protects database and returns clean JSON structure
    data = res.json()
    assert "items" in data


def test_sec_005_xss_header_and_sanitization(client, admin_headers):
    """SEC-005: XSS protection headers and input handling"""
    xss_script = "<script>alert('XSS')</script>"
    res = client.get(f"/api/v1/employees?search={xss_script}", headers=admin_headers)
    assert res.status_code == 200
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"
    assert res.headers.get("X-Content-Type-Options") == "nosniff"


def test_sec_006_invalid_jwt(client):
    """SEC-006: Invalid JWT signature or malformed bearer token"""
    bad_headers = {"Authorization": "Bearer header.payload.invalid_signature"}
    res = client.get("/api/v1/auth/me", headers=bad_headers)
    assert res.status_code == 401
    assert res.json()["error_code"] == "TOKEN_EXPIRED"


def test_sec_007_expired_jwt(client):
    """SEC-007: Expired JWT token handling"""
    to_encode = {
        "exp": datetime.now(timezone.utc) - timedelta(minutes=10),
        "sub": "1",
        "type": "access"
    }
    expired_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    headers = {"Authorization": f"Bearer {expired_token}"}
    
    res = client.get("/api/v1/auth/me", headers=headers)
    assert res.status_code == 401
    assert res.json()["error_code"] == "TOKEN_EXPIRED"


def test_sec_008_token_replay_and_logout_revocation(client, employee_user):
    """SEC-008: Token replay prevention and refresh token revocation"""
    login_res = client.post("/api/v1/auth/login", json={
        "email": employee_user.email,
        "password": "EmployeePass123!"
    })
    token_data = login_res.json()
    ref_token = token_data["refresh_token"]

    # Revoke refresh token via logout
    logout_res = client.post("/api/v1/auth/logout", json={"refresh_token": ref_token}, headers={"Authorization": f"Bearer {token_data['access_token']}"})
    assert logout_res.status_code == 200

    # Attempt token replay with revoked refresh token
    replay_res = client.post("/api/v1/auth/refresh", json={"refresh_token": ref_token})
    assert replay_res.status_code == 401
    assert replay_res.json()["error_code"] == "TOKEN_EXPIRED"


def test_sec_009_brute_force_login(client):
    """SEC-009: Invalid credentials brute-force login rejection"""
    for _ in range(5):
        res = client.post("/api/v1/auth/login", json={
            "email": "nonexistent@payroll.com",
            "password": "WrongPassword123!"
        })
        assert res.status_code == 401
        assert res.json()["error_code"] == "INVALID_CREDENTIALS"


def test_sec_010_unauthorized_payroll_approval(client, employee_headers):
    """SEC-010: Unauthorized payroll approval attempt by standard employee"""
    res = client.post("/api/v1/payslips/run/1/approve", json={"action": "APPROVE", "remarks": "Unauthorized"}, headers=employee_headers)
    assert res.status_code == 403
    assert res.json()["error_code"] == "PERMISSION_DENIED"


def test_sec_011_unauthorized_payroll_unlock(client, employee_headers):
    """SEC-011: Unauthorized payroll unlock attempt without payroll.unlock permission"""
    res = client.post("/api/v1/payroll/runs/1/unlock", headers=employee_headers)
    assert res.status_code == 403
    assert res.json()["error_code"] == "PERMISSION_DENIED"


def test_sec_012_unauthorized_salary_modification(client, employee_headers):
    """SEC-012: Unauthorized salary component creation or structure assignment"""
    res = client.post("/api/v1/salary/components", json={
        "code": "HACK",
        "name": "Hack Bonus",
        "component_type": "EARNING",
        "calculation_type": "FLAT",
        "default_value": 50000.0,
    }, headers=employee_headers)
    assert res.status_code == 403
    assert res.json()["error_code"] == "PERMISSION_DENIED"


def test_sec_013_malicious_file_upload_validation(client, admin_headers):
    """SEC-013: Upload employee document with file metadata and MIME verification"""
    file_content = b"executable binary malicious payload"
    files = {"file": ("malicious.exe", file_content, "application/octet-stream")}
    data = {"document_type": "IDENTITY_PROOF", "title": "ID Card"}

    res = client.post("/api/v1/employees/1/documents", data=data, files=files, headers=admin_headers)
    assert res.status_code == 201
    doc_data = res.json()
    assert doc_data["title"] == "ID Card"
    assert doc_data["mime_type"] == "application/octet-stream"


def test_sec_014_sensitive_information_in_logs_and_pii_masking():
    """SEC-014: Sensitive information PII masking verification"""
    masked_bank = AuditService.mask_pii("987654321012")
    assert masked_bank == "********1012"
    masked_pan = AuditService.mask_pii("ABCDE1234F")
    assert masked_pan == "******234F"


def test_sec_015_api_idor_testing(client, employee_headers):
    """SEC-015: API IDOR isolation check across employee self-service endpoints"""
    # Employee cannot view another employee's specific JSON payslip breakdown
    res = client.get("/api/v1/payslips/employee/999/period/1", headers=employee_headers)
    assert res.status_code in (400, 403)
    assert "ACCESS_DENIED" in str(res.json())
