def test_sal_001_create_salary_structure(client, admin_headers):
    """SAL-001: Create salary structure"""
    # Fetch existing components
    comp_resp = client.get("/api/v1/salary/components", headers=admin_headers)
    components = comp_resp.json()
    c1_id = components[0]["id"]
    c2_id = components[1]["id"]

    payload = {
        "company_id": 1,
        "name": "Executive Compensation Structure",
        "description": "Standard structure for executive grade",
        "components": [
            {"component_id": c1_id, "default_percentage": 50.0},
            {"component_id": c2_id, "default_percentage": 40.0}
        ]
    }
    res = client.post("/api/v1/salary/structures", json=payload, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Executive Compensation Structure"


def test_sal_002_add_fixed_component(client, admin_headers):
    """SAL-002: Add fixed component"""
    payload = {
        "name": "Shift Allowance",
        "code": "SHIFT_ALLOW",
        "component_type": "Earning",
        "calculation_type": "Fixed",
        "frequency": "Monthly",
        "is_taxable": True,
        "is_statutory_applicable": True,
        "is_prorated": True
    }
    res = client.post("/api/v1/salary/components", json=payload, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["calculation_type"] == "Fixed"


def test_sal_003_percentage_component(client, admin_headers, employee_user):
    """SAL-003: Percentage component calculated correctly"""
    # Assign CTC of 600,000 INR (50,000 / month)
    assign_payload = {
        "employee_id": employee_user.id,
        "total_ctc": 600000.0,
        "effective_date": "2024-01-01",
        "currency": "INR"
    }
    res = client.post("/api/v1/salary/assign", json=assign_payload, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    
    # Monthly CTC = 50,000. Basic = 50% = 25,000. HRA = 40% of Basic = 10,000.
    basic_comp = [c for c in data["assigned_components"] if c["component"]["code"] == "BASIC"][0]
    hra_comp = [c for c in data["assigned_components"] if c["component"]["code"] == "HRA"][0]
    
    assert basic_comp["monthly_amount"] == 25000.0
    assert hra_comp["monthly_amount"] == 10000.0  # Exactly 40% of 25,000


def test_sal_004_formula_component(client, admin_headers):
    """SAL-004: Formula component correct formula definition"""
    payload = {
        "name": "Performance Bonus Component",
        "code": "PERF_BONUS",
        "component_type": "Earning",
        "calculation_type": "Formula",
        "formula_expression": "BASIC * 0.10 + 1000",
        "frequency": "Monthly",
        "is_taxable": True,
        "is_statutory_applicable": False,
        "is_prorated": False
    }
    res = client.post("/api/v1/salary/components", json=payload, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["formula_expression"] == "BASIC * 0.10 + 1000"


def test_sal_005_taxable_component(client, admin_headers):
    """SAL-005: Taxable component included in taxable income calculation"""
    payload = {
        "name": "Taxable Executive Bonus",
        "code": "TAXABLE_BONUS",
        "component_type": "Earning",
        "calculation_type": "Fixed",
        "is_taxable": True
    }
    res = client.post("/api/v1/salary/components", json=payload, headers=admin_headers)
    assert res.status_code == 201
    assert res.json()["is_taxable"] is True


def test_sal_006_non_taxable_component(client, admin_headers):
    """SAL-006: Non-taxable component excluded from taxable income"""
    payload = {
        "name": "Non-Taxable Medical Reimbursement",
        "code": "NON_TAXABLE_MED",
        "component_type": "Earning",
        "calculation_type": "Fixed",
        "is_taxable": False
    }
    res = client.post("/api/v1/salary/components", json=payload, headers=admin_headers)
    assert res.status_code == 201
    assert res.json()["is_taxable"] is False


def test_sal_007_salary_revision(client, admin_headers, employee_user):
    """SAL-007: Salary revision effective date and new CTC applied"""
    # Initial assignment
    client.post("/api/v1/salary/assign", json={
        "employee_id": employee_user.id,
        "total_ctc": 600000.0,
        "effective_date": "2024-01-01",
        "currency": "INR"
    }, headers=admin_headers)

    # Perform revision
    rev_payload = {
        "employee_id": employee_user.id,
        "new_ctc": 720000.0,
        "effective_date": "2024-10-01",
        "revision_reason": "Annual Promotion"
    }
    res = client.post("/api/v1/salary/revisions", json=rev_payload, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["old_ctc"] == 600000.0
    assert data["new_ctc"] == 720000.0
    assert data["effective_date"] == "2024-10-01"


def test_sal_008_historical_salary(client, admin_headers, employee_user):
    """SAL-008: Historical salary revision retains old salary audit log"""
    res = client.get(f"/api/v1/salary/revisions/{employee_user.id}", headers=admin_headers)
    assert res.status_code == 200
    revisions = res.json()
    assert len(revisions) >= 1
    assert revisions[0]["old_ctc"] == 600000.0
    assert revisions[0]["new_ctc"] == 720000.0


def test_sal_009_negative_salary(client, admin_headers, employee_user):
    """SAL-009: Negative salary rejected"""
    payload = {
        "employee_id": employee_user.id,
        "total_ctc": -500000.0,
        "effective_date": "2024-01-01"
    }
    res = client.post("/api/v1/salary/assign", json=payload, headers=admin_headers)
    assert res.status_code == 400
    assert "negative" in res.json()["detail"].lower()


def test_sal_010_duplicate_component(client, admin_headers):
    """SAL-010: Duplicate component code prevented"""
    payload = {
        "name": "Basic Salary Duplicate",
        "code": "BASIC",  # Code 'BASIC' already exists
        "component_type": "Earning",
        "calculation_type": "Fixed"
    }
    res = client.post("/api/v1/salary/components", json=payload, headers=admin_headers)
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"].lower()
