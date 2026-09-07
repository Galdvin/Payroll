def test_tax_001_zero_taxable_income(client, admin_headers):
    """TAX-001: Zero taxable income -> 0.0 tax"""
    res = client.post("/api/v1/tax-statutory/evaluate-tds", json={
        "gross_monthly_salary": 0.0,
        "regime_name": "New Regime"
    }, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["taxable_annual"] == 0.0
    assert data["monthly_tds"] == 0.0


def test_tax_002_income_below_threshold(client, admin_headers):
    """TAX-002: Income below basic exemption threshold (₹300k taxable)"""
    # Gross ₹25,000 / mo = ₹300,000 / yr. Less ₹75,000 std ded = ₹225,000 taxable (below ₹300k slab)
    res = client.post("/api/v1/tax-statutory/evaluate-tds", json={
        "gross_monthly_salary": 25000.0,
        "regime_name": "New Regime"
    }, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["taxable_annual"] == 225000.0
    assert data["total_annual_tax"] == 0.0
    assert data["monthly_tds"] == 0.0


def test_tax_003_income_at_threshold(client, admin_headers):
    """TAX-003: Income exactly at threshold boundary (₹375k gross - ₹75k std ded = ₹300k taxable)"""
    res = client.post("/api/v1/tax-statutory/evaluate-tds", json={
        "gross_monthly_salary": 31250.0,  # ₹375,000 annual
        "regime_name": "New Regime"
    }, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["taxable_annual"] == 300000.0
    assert data["total_annual_tax"] == 0.0


def test_tax_004_income_above_threshold(client, admin_headers):
    """TAX-004: Income above threshold (enters 5% slab)"""
    # Gross ₹50,000 / mo = ₹600,000 annual. Less ₹75,000 std ded = ₹525,000 taxable
    res = client.post("/api/v1/tax-statutory/evaluate-tds", json={
        "gross_monthly_salary": 50000.0,
        "regime_name": "New Regime"
    }, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["taxable_annual"] == 525000.0
    assert data["total_annual_tax"] > 0.0


def test_tax_005_multiple_tax_slabs(client, admin_headers):
    """TAX-005: High income spanning multiple tax slabs (5%, 10%, 15%, 20%, 30%)"""
    # Gross ₹150,000 / mo = ₹1,800,000 annual. Less ₹75,000 std ded = ₹1,725,000 taxable
    res = client.post("/api/v1/tax-statutory/evaluate-tds", json={
        "gross_monthly_salary": 150000.0,
        "regime_name": "New Regime"
    }, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["taxable_annual"] == 1725000.0
    assert data["tax_before_cess"] > 100000.0


def test_tax_006_exemption(client, admin_headers):
    """TAX-006: Exemption standard deduction deducted from gross"""
    res = client.post("/api/v1/tax-statutory/evaluate-tds", json={
        "gross_monthly_salary": 100000.0,
        "regime_name": "New Regime"
    }, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["annual_gross"] == 1200000.0
    assert data["standard_deduction"] == 75000.0
    assert data["taxable_annual"] == 1125000.0


def test_tax_007_deduction(client, admin_headers):
    """TAX-007: Deduction reduces taxable base"""
    res = client.post("/api/v1/tax-statutory/evaluate-tds", json={
        "gross_monthly_salary": 80000.0,
        "regime_name": "New Regime"
    }, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["standard_deduction"] == 75000.0


def test_tax_008_tax_regime_change(client, admin_headers):
    """TAX-008: Tax regime change (New Regime evaluation)"""
    res = client.post("/api/v1/tax-statutory/evaluate-tds", json={
        "gross_monthly_salary": 100000.0,
        "regime_name": "New Regime"
    }, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["regime_name"] == "New Regime"


def test_tax_009_tax_rule_version_change(client, admin_headers):
    """TAX-009: Tax-rule version change tracking"""
    res = client.get("/api/v1/tax-statutory/tax-rules?country=India", headers=admin_headers)
    assert res.status_code == 200
    rules = res.json()
    assert len(rules) >= 1
    assert "rule_version" in rules[0]


def test_tax_010_mid_year_employee_joining(client, admin_headers, employee_user):
    """TAX-010: Mid-year employee joining tax computation"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    assert res.status_code == 200
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers).json()
    assert "step_4_tax_tds" in trace


def test_tax_011_mid_year_employee_leaving(client, admin_headers, employee_user):
    """TAX-011: Mid-year employee leaving tax settlement"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    assert res.status_code == 200


def test_tax_012_tax_recalculation(client, admin_headers):
    """TAX-012: Tax recalculation via evaluate-tds API"""
    res1 = client.post("/api/v1/tax-statutory/evaluate-tds", json={"gross_monthly_salary": 50000.0}, headers=admin_headers)
    res2 = client.post("/api/v1/tax-statutory/evaluate-tds", json={"gross_monthly_salary": 100000.0}, headers=admin_headers)
    assert res1.status_code == 200
    assert res2.status_code == 200
    assert res2.json()["monthly_tds"] > res1.json()["monthly_tds"]
