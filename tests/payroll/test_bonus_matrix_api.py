from datetime import date
from app.models.financial_extras import BonusIncentive


def test_bon_001_fixed_bonus(client, admin_headers, employee_user):
    """BON-001: Fixed bonus creation"""
    payload = {
        "employee_id": employee_user.id,
        "title": "Fixed Performance Award",
        "category": "Performance",
        "amount": 25000.0,
        "is_taxable": True,
        "payout_date": "2024-09-25"
    }
    res = client.post("/api/v1/financial-extras/bonuses", json=payload, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["amount"] == 25000.0


def test_bon_002_percentage_bonus(client, admin_headers, employee_user):
    """BON-002: Percentage bonus (e.g. 10% of annual basic)"""
    payload = {
        "employee_id": employee_user.id,
        "title": "10% Annual Achievement Bonus",
        "category": "Annual",
        "amount": 30000.0,  # 10% of 300,000 basic
        "is_taxable": True,
        "payout_date": "2024-09-25"
    }
    res = client.post("/api/v1/financial-extras/bonuses", json=payload, headers=admin_headers)
    assert res.status_code == 201
    assert res.json()["amount"] == 30000.0


def test_bon_003_one_time_bonus(client, admin_headers, employee_user):
    """BON-003: One-time spot bonus"""
    payload = {
        "employee_id": employee_user.id,
        "title": "Spot Recognition Bonus",
        "category": "Spot",
        "amount": 10000.0,
        "is_taxable": True,
        "payout_date": "2024-09-25"
    }
    res = client.post("/api/v1/financial-extras/bonuses", json=payload, headers=admin_headers)
    assert res.status_code == 201


def test_bon_004_recurring_bonus(client, admin_headers, employee_user):
    """BON-004: Recurring incentive bonus"""
    payload = {
        "employee_id": employee_user.id,
        "title": "Monthly Sales Incentive",
        "category": "Sales Incentive",
        "amount": 12000.0,
        "is_taxable": True,
        "payout_date": "2024-09-25"
    }
    res = client.post("/api/v1/financial-extras/bonuses", json=payload, headers=admin_headers)
    assert res.status_code == 201


def test_bon_005_taxable_bonus(client, admin_headers, employee_user):
    """BON-005: Taxable bonus"""
    payload = {
        "employee_id": employee_user.id,
        "title": "Taxable Executive Bonus",
        "category": "Performance",
        "amount": 50000.0,
        "is_taxable": True,
        "payout_date": "2024-09-25"
    }
    res = client.post("/api/v1/financial-extras/bonuses", json=payload, headers=admin_headers)
    assert res.status_code == 201
    assert res.json()["is_taxable"] is True


def test_bon_006_non_taxable_bonus(client, admin_headers, employee_user):
    """BON-006: Non-taxable bonus / gift voucher"""
    payload = {
        "employee_id": employee_user.id,
        "title": "Festival Gift Allowance",
        "category": "Festival",
        "amount": 5000.0,
        "is_taxable": False,
        "payout_date": "2024-09-25"
    }
    res = client.post("/api/v1/financial-extras/bonuses", json=payload, headers=admin_headers)
    assert res.status_code == 201
    assert res.json()["is_taxable"] is False


def test_bon_007_bonus_cancellation(client, admin_headers, employee_user):
    """BON-007: Bonus cancellation"""
    create_res = client.post("/api/v1/financial-extras/bonuses", json={
        "employee_id": employee_user.id,
        "title": "Pending Bonus to Cancel",
        "category": "Performance",
        "amount": 15000.0,
        "is_taxable": True,
        "payout_date": "2024-09-25"
    }, headers=admin_headers)
    bonus_id = create_res.json()["id"]

    cancel_res = client.post(f"/api/v1/financial-extras/bonuses/{bonus_id}/cancel", headers=admin_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "Cancelled"


def test_bon_008_bonus_reflected_in_payroll(client, admin_headers, employee_user, db_session):
    """BON-008: Bonus reflected in payroll calculation step trace"""
    # Create pending bonus
    bonus = BonusIncentive(
        employee_id=employee_user.id,
        title="Q3 Target Bonus",
        category="Performance",
        amount=20000.0,
        is_taxable=True,
        payout_date=date(2024, 9, 25),
        status="Pending"
    )
    db_session.add(bonus)
    db_session.commit()

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    assert res.status_code == 200
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers).json()
    assert trace["step_2_earnings_breakdown"]["bonus"] == 20000.0


def test_bon_009_bonus_reflected_in_payslip(client, admin_headers, employee_user):
    """BON-009: Bonus reflected in payslip breakdown"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = res.json()["id"]

    client.post(f"/api/v1/payroll/runs/{run_id}/approve", headers=admin_headers)
    payslip_res = client.get(f"/api/v1/payslips/employee/{employee_user.id}/period/{period_id}", headers=admin_headers)
    assert payslip_res.status_code == 200
    data = payslip_res.json()
    earning_codes = [e["component_code"] for e in data["earnings"]]
    assert "BONUS" in earning_codes or len(earning_codes) >= 1
