from datetime import date
from app.models.financial_extras import Loan, Advance


def test_loan_001_create_loan(client, admin_headers, employee_user):
    """LOAN-001: Create loan request"""
    payload = {
        "employee_id": employee_user.id,
        "principal": 120000.0,
        "interest_rate": 12.0,
        "tenure_months": 12,
        "start_date": "2024-09-01"
    }
    res = client.post("/api/v1/financial-extras/loans", json=payload, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "Requested"
    assert data["principal"] == 120000.0
    assert data["monthly_emi"] > 10000.0  # ~10,661 EMI


def test_loan_002_approve_loan(client, admin_headers, employee_user):
    """LOAN-002: Approve loan request"""
    create_res = client.post("/api/v1/financial-extras/loans", json={
        "employee_id": employee_user.id,
        "principal": 60000.0,
        "interest_rate": 10.0,
        "tenure_months": 6,
        "start_date": "2024-09-01"
    }, headers=admin_headers)
    loan_id = create_res.json()["id"]

    app_res = client.post(f"/api/v1/financial-extras/loans/{loan_id}/approve", headers=admin_headers)
    assert app_res.status_code == 200
    assert app_res.json()["status"] == "Active"


def test_loan_003_calculate_emi(client, admin_headers, employee_user):
    """LOAN-003: Calculate EMI mathematical formula"""
    # 100,000 principal @ 0% interest for 10 months -> EMI = 10,000
    res = client.post("/api/v1/financial-extras/loans", json={
        "employee_id": employee_user.id,
        "principal": 100000.0,
        "interest_rate": 0.0,
        "tenure_months": 10,
        "start_date": "2024-09-01"
    }, headers=admin_headers)
    assert res.status_code == 201
    assert res.json()["monthly_emi"] == 10000.0


def test_loan_004_deduct_emi_from_salary(client, admin_headers, employee_user, db_session):
    """LOAN-004: Deduct EMI from salary during payroll calculation"""
    loan = Loan(
        employee_id=employee_user.id,
        principal=60000.0,
        interest_rate=0.0,
        tenure_months=6,
        start_date=date(2024, 9, 1),
        monthly_emi=10000.0,
        outstanding_amount=60000.0,
        status="Active"
    )
    db_session.add(loan)
    db_session.commit()

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers).json()
    assert trace["step_3_deductions_breakdown"]["loan_emi_deduction"]["amount"] == 10000.0


def test_loan_005_partial_loan_recovery(client, admin_headers, employee_user, db_session):
    """LOAN-005: Partial loan recovery / repayment"""
    loan = Loan(
        employee_id=employee_user.id,
        principal=50000.0,
        interest_rate=0.0,
        tenure_months=5,
        start_date=date(2024, 9, 1),
        monthly_emi=10000.0,
        outstanding_amount=50000.0,
        status="Active"
    )
    db_session.add(loan)
    db_session.commit()

    repay_res = client.post(f"/api/v1/financial-extras/loans/{loan.id}/repay", json={
        "amount": 20000.0,
        "transaction_type": "PARTIAL_REPAYMENT"
    }, headers=admin_headers)
    assert repay_res.status_code == 200
    assert repay_res.json()["outstanding_amount"] == 30000.0


def test_loan_006_early_settlement(client, admin_headers, employee_user, db_session):
    """LOAN-006: Early settlement settles outstanding loan"""
    loan = Loan(
        employee_id=employee_user.id,
        principal=30000.0,
        interest_rate=0.0,
        tenure_months=3,
        start_date=date(2024, 9, 1),
        monthly_emi=10000.0,
        outstanding_amount=30000.0,
        status="Active"
    )
    db_session.add(loan)
    db_session.commit()

    repay_res = client.post(f"/api/v1/financial-extras/loans/{loan.id}/repay", json={
        "amount": 30000.0,
        "transaction_type": "EARLY_SETTLEMENT"
    }, headers=admin_headers)
    assert repay_res.status_code == 200
    data = repay_res.json()
    assert data["outstanding_amount"] == 0.0
    assert data["status"] == "Settled"


def test_loan_007_loan_cancellation(client, admin_headers, employee_user):
    """LOAN-007: Loan cancellation"""
    create_res = client.post("/api/v1/financial-extras/loans", json={
        "employee_id": employee_user.id,
        "principal": 40000.0,
        "interest_rate": 10.0,
        "tenure_months": 4,
        "start_date": "2024-09-01"
    }, headers=admin_headers)
    loan_id = create_res.json()["id"]

    cancel_res = client.post(f"/api/v1/financial-extras/loans/{loan_id}/cancel", headers=admin_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "Cancelled"


def test_loan_008_advance_request(client, admin_headers, employee_user):
    """LOAN-008: Advance request"""
    payload = {
        "employee_id": employee_user.id,
        "amount": 15000.0,
        "request_date": "2024-09-05",
        "recovery_months": 3
    }
    res = client.post("/api/v1/financial-extras/advances", json=payload, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["amount"] == 15000.0
    assert data["monthly_recovery_amount"] == 5000.0


def test_loan_009_advance_recovery(client, admin_headers, employee_user, db_session):
    """LOAN-009: Advance recovery deducted in payroll"""
    adv = Advance(
        employee_id=employee_user.id,
        amount=12000.0,
        request_date=date(2024, 9, 1),
        recovery_months=3,
        monthly_recovery_amount=4000.0,
        recovered_amount=0.0,
        status="Approved"
    )
    db_session.add(adv)
    db_session.commit()

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers).json()
    assert trace["step_3_deductions_breakdown"]["advance_recovery"]["amount"] == 4000.0


def test_loan_010_outstanding_balance_calculation(client, admin_headers, employee_user, db_session):
    """LOAN-010: Outstanding balance calculation updated after repayments"""
    loan = Loan(
        employee_id=employee_user.id,
        principal=80000.0,
        interest_rate=0.0,
        tenure_months=8,
        start_date=date(2024, 9, 1),
        monthly_emi=10000.0,
        outstanding_amount=80000.0,
        status="Active"
    )
    db_session.add(loan)
    db_session.commit()

    client.post(f"/api/v1/financial-extras/loans/{loan.id}/repay", json={
        "amount": 10000.0,
        "transaction_type": "EMI_DEDUCTION"
    }, headers=admin_headers)

    res = client.get(f"/api/v1/financial-extras/loans?employee_id={employee_user.id}", headers=admin_headers)
    assert res.status_code == 200
    matched = [l for l in res.json() if l["id"] == loan.id][0]
    assert matched["outstanding_amount"] == 70000.0
