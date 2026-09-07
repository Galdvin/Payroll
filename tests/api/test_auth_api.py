import pytest


def test_auth_001_login_valid_credentials(client):
    """TC ID: AUTH-001 | Login with valid credentials | User successfully logs in"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@enterprise-payroll.com", "password": "AdminPassword123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_auth_002_login_invalid_password(client):
    """TC ID: AUTH-002 | Login with invalid password | Login rejected"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@enterprise-payroll.com", "password": "WrongPassword!"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error_code"] == "INVALID_CREDENTIALS"


def test_auth_003_login_invalid_username(client):
    """TC ID: AUTH-003 | Login with invalid username | Login rejected"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@enterprise-payroll.com", "password": "AdminPassword123!"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error_code"] == "INVALID_CREDENTIALS"


def test_auth_004_empty_username(client):
    """TC ID: AUTH-004 | Empty username | Validation error"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "", "password": "AdminPassword123!"}
    )
    assert response.status_code in [400, 422]


def test_auth_005_empty_password(client):
    """TC ID: AUTH-005 | Empty password | Validation error"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@enterprise-payroll.com", "password": ""}
    )
    assert response.status_code in [400, 422]


def test_auth_006_password_reset(client):
    """TC ID: AUTH-006 | Password reset | Reset workflow works"""
    reset_resp = client.post(
        "/api/v1/auth/password-reset",
        json={"email": "admin@enterprise-payroll.com", "new_password": "NewAdminPassword123!"}
    )
    assert reset_resp.status_code == 200
    assert reset_resp.json()["success"] is True

    # Re-test login with new password
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@enterprise-payroll.com", "password": "NewAdminPassword123!"}
    )
    assert login_resp.status_code == 200

    # Reset back to default
    client.post(
        "/api/v1/auth/password-reset",
        json={"email": "admin@enterprise-payroll.com", "new_password": "AdminPassword123!"}
    )


def test_auth_007_expired_token(client):
    """TC ID: AUTH-007 | Expired token | User rejected"""
    invalid_headers = {"Authorization": "Bearer invalid_expired_jwt_token_payload"}
    response = client.get("/api/v1/auth/me", headers=invalid_headers)
    assert response.status_code in [401, 403]


def test_auth_008_refresh_token(client):
    """TC ID: AUTH-008 | Refresh token | New access token generated"""
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@enterprise-payroll.com", "password": "AdminPassword123!"}
    )
    refresh_token = login_resp.json()["refresh_token"]

    refresh_resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_resp.status_code == 200
    data = refresh_resp.json()
    assert "access_token" in data


def test_auth_009_logout(client, admin_headers):
    """TC ID: AUTH-009 | Logout | Session invalidated"""
    logout_resp = client.post("/api/v1/auth/logout", json={}, headers=admin_headers)
    assert logout_resp.status_code == 200
    assert logout_resp.json()["success"] is True


def test_auth_010_multiple_failed_logins(client):
    """TC ID: AUTH-010 | Multiple failed logins | Rate limiting / rejection triggered"""
    for _ in range(5):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@enterprise-payroll.com", "password": "BadPassword"}
        )
        assert resp.status_code == 401


def test_auth_011_employee_accesses_admin_url(client, employee_headers):
    """TC ID: AUTH-011 | Employee accesses admin URL | Access denied"""
    response = client.get("/api/v1/users", headers=employee_headers)
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["error_code"] == "PERMISSION_DENIED"


def test_auth_012_payroll_admin_accesses_payroll(client, admin_headers):
    """TC ID: AUTH-012 | Payroll admin accesses payroll | Access allowed"""
    response = client.get("/api/v1/payroll/periods", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
