def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_login_success(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@enterprise-payroll.com", "password": "AdminPassword123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@enterprise-payroll.com", "password": "WrongPassword!"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error_code"] == "INVALID_CREDENTIALS"


def test_get_current_user_profile(client, admin_headers):
    response = client.get("/api/v1/auth/me", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@enterprise-payroll.com"
    assert data["is_superuser"] is True
    assert "*" in data["permissions"]


def test_refresh_token_flow(client):
    # 1. Login to get refresh token
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@enterprise-payroll.com", "password": "AdminPassword123!"}
    )
    refresh_token = login_resp.json()["refresh_token"]

    # 2. Call refresh endpoint
    refresh_resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_resp.status_code == 200
    data = refresh_resp.json()
    assert "access_token" in data
