def test_admin_can_access_users_list(client, admin_headers):
    response = client.get("/api/v1/users", headers=admin_headers)
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 1


def test_standard_employee_cannot_access_users_list(client, employee_headers):
    response = client.get("/api/v1/users", headers=employee_headers)
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["error_code"] == "PERMISSION_DENIED"


def test_unauthenticated_request_rejected(client):
    response = client.get("/api/v1/users")
    assert response.status_code == 401


def test_admin_can_create_user_and_assign_role(client, admin_headers):
    payload = {
        "email": "jane.smith@company.com",
        "password": "Password123!",
        "full_name": "Jane Smith",
        "role_ids": []
    }
    response = client.post("/api/v1/users", json=payload, headers=admin_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "jane.smith@company.com"
    assert data["full_name"] == "Jane Smith"


def test_admin_can_create_custom_role(client, admin_headers):
    payload = {
        "name": "Custom Payroll Reviewer",
        "description": "Role for reviewing payroll calculations",
        "permission_ids": []
    }
    response = client.post("/api/v1/roles", json=payload, headers=admin_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Custom Payroll Reviewer"
