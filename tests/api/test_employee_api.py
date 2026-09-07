import pytest


def setup_org_comp_dept(client, admin_headers):
    org_resp = client.post("/api/v1/organization", json={"name": "EMP Test Org", "code": "EMP_ORG_01"}, headers=admin_headers)
    org_id = org_resp.json()["id"]
    comp_resp = client.post("/api/v1/organization/companies", json={"organization_id": org_id, "name": "EMP Test Comp", "code": "ETC01"}, headers=admin_headers)
    comp_id = comp_resp.json()["id"]
    dept_resp = client.post("/api/v1/organization/departments", json={"company_id": comp_id, "name": "Engineering", "code": "ENG"}, headers=admin_headers)
    dept_id = dept_resp.json()["id"]
    return org_id, comp_id, dept_id


def test_emp_001_create_employee(client, admin_headers):
    """TC ID: EMP-001 | Create employee | Employee created"""
    org_id, comp_id, dept_id = setup_org_comp_dept(client, admin_headers)
    payload = {
        "employee_code": "EMP-001-CODE",
        "first_name": "Marcus",
        "last_name": "Vance",
        "gender": "Male",
        "date_of_birth": "1992-08-20",
        "nationality": "Indian",
        "employment_type": "Full Time",
        "status": "Active",
        "joining_date": "2024-02-01",
        "organization_id": org_id,
        "company_id": comp_id,
        "department_id": dept_id,
        "work_email": "marcus.vance@company.com",
    }
    resp = client.post("/api/v1/employees", json=payload, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["employee_code"] == "EMP-001-CODE"
    assert data["first_name"] == "Marcus"


def test_emp_002_duplicate_employee_code(client, admin_headers):
    """TC ID: EMP-002 | Duplicate employee code | Rejected"""
    org_id, comp_id, dept_id = setup_org_comp_dept(client, admin_headers)
    payload = {
        "employee_code": "EMP-DUP-CODE",
        "first_name": "David",
        "last_name": "Miller",
        "gender": "Male",
        "date_of_birth": "1990-01-01",
        "joining_date": "2024-01-01",
        "organization_id": org_id,
        "company_id": comp_id,
        "department_id": dept_id,
        "work_email": "david1.miller@company.com",
    }
    resp1 = client.post("/api/v1/employees", json=payload, headers=admin_headers)
    assert resp1.status_code == 201

    payload["work_email"] = "david2.miller@company.com"
    resp2 = client.post("/api/v1/employees", json=payload, headers=admin_headers)
    assert resp2.status_code in [400, 409, 500]


def test_emp_003_invalid_email(client, admin_headers):
    """TC ID: EMP-003 | Invalid email | Rejected"""
    org_id, comp_id, dept_id = setup_org_comp_dept(client, admin_headers)
    payload = {
        "employee_code": "EMP-INVALID-EMAIL",
        "first_name": "Sarah",
        "last_name": "Connor",
        "gender": "Female",
        "date_of_birth": "1991-03-12",
        "joining_date": "2024-01-01",
        "organization_id": org_id,
        "company_id": comp_id,
        "department_id": dept_id,
        "work_email": "not-an-email-address",
    }
    resp = client.post("/api/v1/employees", json=payload, headers=admin_headers)
    assert resp.status_code in [400, 422]


def test_emp_004_missing_mandatory_field(client, admin_headers):
    """TC ID: EMP-004 | Missing mandatory field | Validation error"""
    payload = {
        "employee_code": "EMP-MISSING",
        # Missing first_name, joining_date, company_id
    }
    resp = client.post("/api/v1/employees", json=payload, headers=admin_headers)
    assert resp.status_code in [400, 422]


def test_emp_005_edit_employee(client, admin_headers):
    """TC ID: EMP-005 | Edit employee | Employee updated"""
    org_id, comp_id, dept_id = setup_org_comp_dept(client, admin_headers)
    payload = {
        "employee_code": "EMP-EDIT-01",
        "first_name": "Robert",
        "last_name": "Lang",
        "gender": "Male",
        "date_of_birth": "1988-11-05",
        "joining_date": "2024-01-01",
        "organization_id": org_id,
        "company_id": comp_id,
        "department_id": dept_id,
        "work_email": "robert.lang@company.com",
    }
    create_resp = client.post("/api/v1/employees", json=payload, headers=admin_headers)
    assert create_resp.status_code == 201
    emp_id = create_resp.json()["id"]

    edit_resp = client.put(f"/api/v1/employees/{emp_id}", json={"first_name": "Robert (Updated)"}, headers=admin_headers)
    assert edit_resp.status_code == 200
    assert edit_resp.json()["first_name"] == "Robert (Updated)"


def test_emp_006_deactivate_employee(client, admin_headers):
    """TC ID: EMP-006 | Deactivate employee | Employee becomes inactive"""
    org_id, comp_id, dept_id = setup_org_comp_dept(client, admin_headers)
    payload = {
        "employee_code": "EMP-DEACT-01",
        "first_name": "Lucas",
        "last_name": "Scott",
        "gender": "Male",
        "date_of_birth": "1994-06-18",
        "joining_date": "2024-01-01",
        "organization_id": org_id,
        "company_id": comp_id,
        "department_id": dept_id,
        "work_email": "lucas.scott@company.com",
        "status": "Active",
    }
    create_resp = client.post("/api/v1/employees", json=payload, headers=admin_headers)
    assert create_resp.status_code == 201
    emp_id = create_resp.json()["id"]

    deact_resp = client.put(f"/api/v1/employees/{emp_id}", json={"status": "Inactive"}, headers=admin_headers)
    assert deact_resp.status_code == 200
    assert deact_resp.json()["status"] == "Inactive"


def test_emp_007_search_employee(client, admin_headers):
    """TC ID: EMP-007 | Search employee | Correct employee returned"""
    resp = client.get("/api/v1/employees?search=Marcus", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert len(data["items"]) >= 1
    assert "Marcus" in data["items"][0]["first_name"]


def test_emp_008_filter_department(client, admin_headers):
    """TC ID: EMP-008 | Filter department | Correct employees displayed"""
    org_id, comp_id, dept_id = setup_org_comp_dept(client, admin_headers)
    resp = client.get(f"/api/v1/employees?department_id={dept_id}", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data


def test_emp_009_upload_employee_document(client, admin_headers):
    """TC ID: EMP-009 | Upload employee document | Document uploaded"""
    files = {"file": ("passport.pdf", b"%PDF-1.4 sample file bytes", "application/pdf")}
    data = {"document_type": "PASSPORT", "title": "Employee Passport"}
    resp = client.post("/api/v1/employees/1/documents", data=data, files=files, headers=admin_headers)
    assert resp.status_code == 201
    doc_data = resp.json()
    assert doc_data["title"] == "Employee Passport"


def test_emp_010_unauthorized_user_views_salary(client, employee_headers):
    """TC ID: EMP-010 | Unauthorized user views salary | Access denied"""
    resp = client.get("/api/v1/salary-structures", headers=employee_headers)
    assert resp.status_code in [401, 403]


def test_emp_011_employee_views_own_profile(client, employee_headers):
    """TC ID: EMP-011 | Employee views own profile | Profile displayed"""
    resp = client.get("/api/v1/self-service/ess/me", headers=employee_headers)
    assert resp.status_code == 200
    assert "employee_code" in resp.json()


def test_emp_012_employee_views_another_employee(client, employee_headers):
    """TC ID: EMP-012 | Employee views another employee | Access denied"""
    resp = client.get("/api/v1/employees/9999", headers=employee_headers)
    assert resp.status_code in [401, 403]
