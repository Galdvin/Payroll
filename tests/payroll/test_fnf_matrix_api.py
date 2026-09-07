from datetime import date
from app.models.financial_extras import Loan, Advance, BonusIncentive


def test_fnf_001_employee_resignation(client, admin_headers, employee_user):
    """FNF-001: Employee resignation F&F settlement"""
    payload = {
        "employee_id": employee_user.id,
        "resignation_date": "2024-09-01",
        "last_working_date": "2024-09-15",
        "settlement_reason": "Resignation"
    }
    res = client.post("/api/v1/fnf/calculate", json=payload, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["settlement_reason"] == "Resignation"
    assert data["status"] == "Calculated"


def test_fnf_002_employee_termination(client, admin_headers, employee_user):
    """FNF-002: Employee termination F&F settlement"""
    payload = {
        "employee_id": employee_user.id,
        "resignation_date": "2024-09-01",
        "last_working_date": "2024-09-10",
        "settlement_reason": "Termination"
    }
    res = client.post("/api/v1/fnf/calculate", json=payload, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["settlement_reason"] == "Termination"


def test_fnf_003_pending_salary(client, admin_headers, employee_user):
    """FNF-003: Pending salary calculated for exit month (15 days)"""
    payload = {
        "employee_id": employee_user.id,
        "resignation_date": "2024-09-01",
        "last_working_date": "2024-09-15",
        "settlement_reason": "Resignation"
    }
    res = client.post("/api/v1/fnf/calculate", json=payload, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["pending_salary_days"] == 15.0
    assert data["pending_salary_amount"] > 0.0


def test_fnf_004_leave_encashment(client, admin_headers, employee_user):
    """FNF-004: Leave encashment included in settlement"""
    payload = {
        "employee_id": employee_user.id,
        "resignation_date": "2024-09-01",
        "last_working_date": "2024-09-30",
        "settlement_reason": "Resignation"
    }
    res = client.post("/api/v1/fnf/calculate", json=payload, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "leave_encashment_amount" in data


def test_fnf_005_notice_pay(client, admin_headers, employee_user):
    """FNF-005: Notice pay credited by company (15 days notice pay)"""
    payload = {
        "employee_id": employee_user.id,
        "resignation_date": "2024-09-01",
        "last_working_date": "2024-09-15",
        "settlement_reason": "Resignation",
        "notice_days_paid": 15
    }
    res = client.post("/api/v1/fnf/calculate", json=payload, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["notice_pay_amount"] > 0.0


def test_fnf_006_notice_recovery(client, admin_headers, employee_user):
    """FNF-006: Notice recovery deducted for short notice (15 days short notice)"""
    payload = {
        "employee_id": employee_user.id,
        "resignation_date": "2024-09-01",
        "last_working_date": "2024-09-15",
        "settlement_reason": "Resignation",
        "notice_days_short": 15
    }
    res = client.post("/api/v1/fnf/calculate", json=payload, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["notice_recovery_amount"] > 0.0


def test_fnf_007_outstanding_loan(client, admin_headers, employee_user, db_session):
    """FNF-007: Outstanding loan balance deducted in F&F settlement"""
    loan = Loan(
        employee_id=employee_user.id,
        principal=40000.0,
        tenure_months=4,
        start_date=date(2024, 9, 1),
        monthly_emi=10000.0,
        outstanding_amount=40000.0,
        status="Active"
    )
    db_session.add(loan)
    db_session.commit()

    payload = {
        "employee_id": employee_user.id,
        "resignation_date": "2024-09-01",
        "last_working_date": "2024-09-30",
        "settlement_reason": "Resignation"
    }
    res = client.post("/api/v1/fnf/calculate", json=payload, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["outstanding_loan_deduction"] == 40000.0


def test_fnf_008_outstanding_advance(client, admin_headers, employee_user, db_session):
    """FNF-008: Outstanding advance balance deducted in F&F settlement"""
    adv = Advance(
        employee_id=employee_user.id,
        amount=10000.0,
        request_date=date(2024, 9, 1),
        recovery_months=2,
        monthly_recovery_amount=5000.0,
        recovered_amount=0.0,
        status="Approved"
    )
    db_session.add(adv)
    db_session.commit()

    payload = {
        "employee_id": employee_user.id,
        "resignation_date": "2024-09-01",
        "last_working_date": "2024-09-30",
        "settlement_reason": "Resignation"
    }
    res = client.post("/api/v1/fnf/calculate", json=payload, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["outstanding_advance_deduction"] == 10000.0


def test_fnf_009_bonus_settlement(client, admin_headers, employee_user, db_session):
    """FNF-009: Bonus settlement included in F&F gross amount"""
    bonus = BonusIncentive(
        employee_id=employee_user.id,
        title="Pending Retention Bonus",
        category="Performance",
        amount=25000.0,
        payout_date=date(2024, 9, 25),
        status="Pending"
    )
    db_session.add(bonus)
    db_session.commit()

    payload = {
        "employee_id": employee_user.id,
        "resignation_date": "2024-09-01",
        "last_working_date": "2024-09-30",
        "settlement_reason": "Resignation"
    }
    res = client.post("/api/v1/fnf/calculate", json=payload, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["bonus_settlement_amount"] >= 25000.0


def test_fnf_010_final_settlement_payslip(client, admin_headers, employee_user):
    """FNF-010: Final settlement statement & approval workflow"""
    calc_res = client.post("/api/v1/fnf/calculate", json={
        "employee_id": employee_user.id,
        "resignation_date": "2024-09-01",
        "last_working_date": "2024-09-30",
        "settlement_reason": "Resignation"
    }, headers=admin_headers)
    fnf_id = calc_res.json()["id"]

    # Approve F&F settlement
    app_res = client.post(f"/api/v1/fnf/{fnf_id}/approve", headers=admin_headers)
    assert app_res.status_code == 200
    assert app_res.json()["status"] == "Approved"

    # Fetch final settlement statement
    statement_res = client.get(f"/api/v1/fnf/employee/{employee_user.id}", headers=admin_headers)
    assert statement_res.status_code == 200
    data = statement_res.json()
    assert data["status"] == "Approved"
    assert "calculation_trace" in data
