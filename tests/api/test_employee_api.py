def setup_org_and_company(client, admin_headers):
    org_resp = client.post("/api/v1/organization", json={"name": "Test Org", "code": "TEST_ORG_01"}, headers=admin_headers)
    org_id = org_resp.json()["id"]
    comp_resp = client.post("/api/v1/organization/companies", json={"organization_id": org_id, "name": "Test Comp", "code": "TC01"}, headers=admin_headers)
    comp_id = comp_resp.json()["id"]
    dept_resp = client.post("/api/v1/organization/departments", json={"company_id": comp_id, "name": "HR", "code": "HR"}, headers=admin_headers)
    dept_id = dept_resp.json()["id"]
    return org_id, comp_id, dept_id


def test_employee_creation_and_history_logging(client, admin_headers):
    org_id, comp_id, dept_id = setup_org_and_company(client, admin_headers)

    emp_payload = {
        "employee_code": "EMP1001",
        "first_name": "Alexander",
        "middle_name": "G",
        "last_name": "Wright",
        "gender": "Male",
        "date_of_birth": "1990-05-15",
        "nationality": "Indian",
        "employment_type": "Full Time",
        "status": "Active",
        "joining_date": "2024-01-10",
        "organization_id": org_id,
        "company_id": comp_id,
        "department_id": dept_id,
        "work_email": "alexander.wright@company.com",
        "currency": "INR",
        "tax_identifier": "ABCDE1234F"
    }

    # 1. Create Employee
    resp = client.post("/api/v1/employees", json=emp_payload, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["employee_code"] == "EMP1001"
    assert data["first_name"] == "Alexander"
    emp_id = data["id"]

    # 2. Update Employee status
    update_resp = client.put(f"/api/v1/employees/{emp_id}", json={"status": "Probation"}, headers=admin_headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "Probation"

    # 3. Retrieve Employee History Audit
    hist_resp = client.get(f"/api/v1/employees/{emp_id}/history", headers=admin_headers)
    assert hist_resp.status_code == 200
    history = hist_resp.json()
    assert len(history) >= 2  # INITIAL_JOINING and PROFILE_UPDATE
