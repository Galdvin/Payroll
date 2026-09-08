def test_slip_001_generate_payslip(client, admin_headers, employee_user):
    """SLIP-001: Generate payslip"""
    # Calculate payroll run
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]
    client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)

    res = client.get(f"/api/v1/payslips/employee/{employee_user.id}/period/{period_id}", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["employee_id"] == employee_user.id
    assert data["gross_salary"] > 0


def test_slip_002_download_pdf(client, admin_headers, employee_user):
    """SLIP-002: Download PDF payslip stream"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.get(f"/api/v1/payslips/employee/{employee_user.id}/period/{period_id}/pdf", headers=admin_headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content.startswith(b"%PDF-1.")


def test_slip_003_verify_employee_information(client, admin_headers, employee_user):
    """SLIP-003: Verify employee information on payslip"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.get(f"/api/v1/payslips/employee/{employee_user.id}/period/{period_id}", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_days"] == 30
    assert data["payable_days"] > 0


def test_slip_004_verify_earnings(client, admin_headers, employee_user):
    """SLIP-004: Verify earnings component breakdown"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.get(f"/api/v1/payslips/employee/{employee_user.id}/period/{period_id}", headers=admin_headers)
    data = res.json()
    earnings = data["earnings"]
    assert len(earnings) >= 1
    codes = [e["code"] for e in earnings]
    assert "BASIC" in codes


def test_slip_005_verify_deductions(client, admin_headers, employee_user):
    """SLIP-005: Verify deductions component breakdown"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.get(f"/api/v1/payslips/employee/{employee_user.id}/period/{period_id}", headers=admin_headers)
    data = res.json()
    deductions = data["deductions"]
    sum_deductions = sum(d["amount"] for d in deductions)
    assert round(data["total_deductions"], 2) == round(sum_deductions, 2)
    codes = [d["code"] for d in deductions]
    assert "PF_EE" in codes


def test_slip_006_verify_gross_salary(client, admin_headers, employee_user):
    """SLIP-006: Verify gross salary calculation integrity"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.get(f"/api/v1/payslips/employee/{employee_user.id}/period/{period_id}", headers=admin_headers)
    data = res.json()
    sum_earnings = sum(e["prorated_amount"] for e in data["earnings"])
    assert round(data["gross_salary"], 2) == round(sum_earnings, 2)


def test_slip_007_verify_net_salary(client, admin_headers, employee_user):
    """SLIP-007: Verify net salary equals gross minus deductions"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.get(f"/api/v1/payslips/employee/{employee_user.id}/period/{period_id}", headers=admin_headers)
    data = res.json()
    expected_net = data["gross_salary"] - data["total_deductions"]
    assert round(data["net_salary"], 2) == round(expected_net, 2)


def test_slip_008_verify_tax(client, admin_headers, employee_user):
    """SLIP-008: Verify taxable income and TDS tax step"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.get(f"/api/v1/payslips/employee/{employee_user.id}/period/{period_id}", headers=admin_headers)
    data = res.json()
    assert data["taxable_income"] >= 0.0
    assert "step_4_tax_tds" in data["calculation_trace"]


def test_slip_009_verify_employer_contribution(client, admin_headers, employee_user):
    """SLIP-009: Verify employer contribution (PF + ESI) and CTC cost"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.get(f"/api/v1/payslips/employee/{employee_user.id}/period/{period_id}", headers=admin_headers)
    data = res.json()
    assert data["employer_statutory"] >= 0.0
    assert data["employer_cost"] >= data["gross_salary"]
    assert round(data["employer_cost"], 2) == round(data["gross_salary"] + data["employer_statutory"], 2)


def test_slip_010_employee_sees_own_payslip(client, admin_headers, employee_user):
    """SLIP-010: Employee sees own payslip"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.get(f"/api/v1/payslips/employee/{employee_user.id}/period/{period_id}", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["employee_id"] == employee_user.id


def test_slip_011_employee_cannot_see_another_payslip(client, employee_headers):
    """SLIP-011: Employee cannot see another employee's payslip (rejected)"""
    # Employee attempts to view payslip of employee ID 9999
    res = client.get("/api/v1/payslips/employee/9999/period/1", headers=employee_headers)
    assert res.status_code in (400, 403)
    assert "ACCESS_DENIED" in str(res.json())
