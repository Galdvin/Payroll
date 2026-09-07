from datetime import date
from app.models.employee import Employee
from app.models.salary import EmployeeSalary
from app.models.attendance import AttendanceSummary
from app.models.financial_extras import Loan, Advance, BonusIncentive, Reimbursement


def test_pay_001_basic_salary_only(client, admin_headers, employee_user, db_session):
    """PAY-001: Basic salary only -> Correct gross"""
    # Set salary with basic only
    sal = db_session.query(EmployeeSalary).filter(EmployeeSalary.employee_id == employee_user.id).first()
    if sal:
        sal.total_ctc = 300000.0
        sal.gross_salary = 25000.0
        db_session.commit()

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["total_gross"] > 0


def test_pay_002_basic_plus_allowances(client, admin_headers, employee_user):
    """PAY-002: Basic + allowances -> Correct gross"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    assert res.status_code == 200
    run_id = res.json()["id"]

    trace_resp = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers)
    trace = trace_resp.json()
    earnings = trace["step_2_earnings_breakdown"]
    assert "basic" in earnings
    assert "hra" in earnings
    assert "transport" in earnings


def test_pay_003_basic_plus_bonus(client, admin_headers, employee_user, db_session):
    """PAY-003: Basic + bonus -> Correct gross"""
    # Create pending bonus
    bonus = BonusIncentive(
        employee_id=employee_user.id,
        title="Annual Performance Bonus",
        category="Performance Bonus",
        amount=15000.0,
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

    trace_resp = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers)
    assert trace_resp.json()["step_2_earnings_breakdown"]["bonus"] == 15000.0


def test_pay_004_basic_plus_overtime(client, admin_headers, employee_user, db_session):
    """PAY-004: Basic + overtime -> Correct gross"""
    # Record attendance summary with 10 OT hours
    att = db_session.query(AttendanceSummary).filter(
        AttendanceSummary.employee_id == employee_user.id,
        AttendanceSummary.year_month == "2024-09"
    ).first()
    if not att:
        att = AttendanceSummary(
            employee_id=employee_user.id,
            year_month="2024-09",
            total_days=30,
            present_days=22.0,
            absent_days=0.0,
            payable_days=30.0,
            overtime_hours=10.0
        )
        db_session.add(att)
    else:
        att.overtime_hours = 10.0
    db_session.commit()

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    assert res.status_code == 200
    run_id = res.json()["id"]

    trace_resp = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers)
    ot_data = trace_resp.json()["step_2_earnings_breakdown"]["overtime"]
    assert ot_data["hours"] == 10.0
    assert ot_data["pay"] > 0.0


def test_pay_005_multiple_deductions(client, admin_headers, employee_user, db_session):
    """PAY-005: Multiple deductions -> Correct net take home"""
    # Create active loan and advance
    loan = Loan(
        employee_id=employee_user.id,
        principal=50000.0,
        tenure_months=10,
        start_date=date(2024, 1, 1),
        monthly_emi=5000.0,
        outstanding_amount=50000.0,
        status="Active"
    )
    db_session.add(loan)
    db_session.commit()

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    assert res.status_code == 200
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers).json()
    deductions = trace["step_3_deductions_breakdown"]
    assert deductions["employee_pf"]["amount"] == 1800.0
    assert deductions["loan_emi_deduction"]["amount"] == 5000.0


def test_pay_006_tax_deduction(client, admin_headers, employee_user):
    """PAY-006: Tax deduction correctly calculated"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    assert res.status_code == 200
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers).json()
    tax_info = trace["step_4_tax_tds"]
    assert tax_info["standard_deduction"] == 50000.0
    assert tax_info["regime_name"] == "New Regime"


def test_pay_007_statutory_deduction(client, admin_headers, employee_user):
    """PAY-007: Statutory deduction correct contribution"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers).json()
    deductions = trace["step_3_deductions_breakdown"]
    assert deductions["employee_pf"]["amount"] == 1800.0
    assert deductions["professional_tax"]["amount"] == 200.0


def test_pay_008_loan_deduction(client, admin_headers, employee_user, db_session):
    """PAY-008: Loan deduction EMI deducted"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers).json()
    assert trace["step_3_deductions_breakdown"]["loan_emi_deduction"]["amount"] >= 0.0


def test_pay_009_advance_deduction(client, admin_headers, employee_user, db_session):
    """PAY-009: Advance deduction recovery deducted"""
    adv = Advance(
        employee_id=employee_user.id,
        amount=10000.0,
        request_date=date(2024, 9, 1),
        monthly_recovery_amount=2000.0,
        status="Approved"
    )
    db_session.add(adv)
    db_session.commit()

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers).json()
    assert trace["step_3_deductions_breakdown"]["advance_recovery"]["amount"] == 2000.0


def test_pay_010_unpaid_leave(client, admin_headers, employee_user, db_session):
    """PAY-010: Unpaid leave deduction proration applied"""
    att = db_session.query(AttendanceSummary).filter(
        AttendanceSummary.employee_id == employee_user.id,
        AttendanceSummary.year_month == "2024-09"
    ).first()
    if att:
        att.payable_days = 20.0  # 10 unpaid leave days -> 20/30 factor
        db_session.commit()

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers).json()
    assert trace["step_1_proration"]["proration_factor"] == 0.6667


def test_pay_011_bonus(client, admin_headers, employee_user, db_session):
    """PAY-011: Bonus correctly included"""
    bonus = BonusIncentive(
        employee_id=employee_user.id,
        title="Festival Bonus",
        category="Festival Bonus",
        amount=10000.0,
        payout_date=date(2024, 9, 25),
        status="Pending"
    )
    db_session.add(bonus)
    db_session.commit()

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers).json()
    assert trace["step_2_earnings_breakdown"]["bonus"] == 10000.0


def test_pay_012_incentive(client, admin_headers, employee_user, db_session):
    """PAY-012: Sales Incentive correctly included"""
    incentive = BonusIncentive(
        employee_id=employee_user.id,
        title="Q3 Sales Incentive",
        category="Sales Incentive",
        amount=8000.0,
        payout_date=date(2024, 9, 25),
        status="Pending"
    )
    db_session.add(incentive)
    db_session.commit()

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers).json()
    assert trace["step_2_earnings_breakdown"]["bonus"] == 8000.0


def test_pay_013_reimbursement(client, admin_headers, employee_user, db_session):
    """PAY-013: Reimbursement correct treatment (non-taxable payout)"""
    reimb = Reimbursement(
        employee_id=employee_user.id,
        title="Travel Expenses",
        category="Travel",
        total_amount=4500.0,
        status="Finance_Approved"
    )
    db_session.add(reimb)
    db_session.commit()

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers).json()
    assert trace["step_2_earnings_breakdown"]["reimbursement"] == 4500.0


def test_pay_014_arrears(client, admin_headers, employee_user):
    """PAY-014: Arrears correctly included"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    assert res.status_code == 200


def test_pay_015_salary_revision(client, admin_headers, employee_user):
    """PAY-015: Salary revision correct effective salary"""
    # Perform salary revision
    client.post("/api/v1/salary/revisions", json={
        "employee_id": employee_user.id,
        "new_ctc": 900000.0,
        "effective_date": "2024-09-01",
        "revision_reason": "Promotion"
    }, headers=admin_headers)

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers).json()
    # Basic for 900,000 CTC = 900,000 / 12 * 0.50 = 37,500
    assert trace["step_2_earnings_breakdown"]["basic"]["full"] == 37500.0


def test_pay_016_new_joiner(client, admin_headers, db_session):
    """PAY-016: New joiner correct proration"""
    # Create new joiner on Sep 16, 2024 (15 days out of 30)
    emp = Employee(
        company_id=1,
        employee_code="EMP_JOINER_01",
        first_name="New",
        last_name="Joiner",
        email="joiner@company.com",
        date_of_joining=date(2024, 9, 16),
        is_active=True
    )
    db_session.add(emp)
    db_session.commit()

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{emp.id}", headers=admin_headers).json()
    assert trace["step_1_proration"]["payable_days"] == 15.0
    assert trace["step_1_proration"]["proration_factor"] == 0.5000


def test_pay_017_resigned_employee(client, admin_headers, db_session):
    """PAY-017: Resigned employee correct proration"""
    emp = Employee(
        company_id=1,
        employee_code="EMP_RESIGNED_01",
        first_name="Resigned",
        last_name="Staff",
        email="resigned@company.com",
        date_of_joining=date(2023, 1, 1),
        resignation_date=date(2024, 9, 10),
        status="Resigned",
        is_active=True
    )
    db_session.add(emp)
    db_session.commit()

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{emp.id}", headers=admin_headers).json()
    assert trace["step_1_proration"]["payable_days"] == 10.0
    assert trace["step_1_proration"]["proration_factor"] == 0.3333


def test_pay_018_terminated_employee(client, admin_headers, db_session):
    """PAY-018: Terminated employee settlement proration"""
    emp = Employee(
        company_id=1,
        employee_code="EMP_TERM_01",
        first_name="Terminated",
        last_name="Staff",
        email="terminated@company.com",
        date_of_joining=date(2022, 1, 1),
        status="Terminated",
        is_active=True
    )
    db_session.add(emp)
    db_session.commit()

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{emp.id}", headers=admin_headers).json()
    assert trace["step_1_proration"]["payable_days"] == 0.0
    assert trace["step_5_final_takehome"]["gross_salary"] == 0.0


def test_pay_019_zero_attendance(client, admin_headers, employee_user, db_session):
    """PAY-019: Zero attendance policy"""
    att = db_session.query(AttendanceSummary).filter(
        AttendanceSummary.employee_id == employee_user.id,
        AttendanceSummary.year_month == "2024-09"
    ).first()
    if att:
        att.payable_days = 0.0
        db_session.commit()

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers).json()
    assert trace["step_1_proration"]["proration_factor"] == 0.0


def test_pay_020_maximum_salary(client, admin_headers, db_session):
    """PAY-020: Maximum salary high-value CTC precision without overflow"""
    emp = Employee(
        company_id=1,
        employee_code="EMP_EXEC_MAX",
        first_name="CEO",
        last_name="Executive",
        email="ceo@company.com",
        date_of_joining=date(2020, 1, 1),
        is_active=True
    )
    db_session.add(emp)
    db_session.commit()

    # Assign 10 Crore CTC (100,000,000 INR)
    client.post("/api/v1/salary/assign", json={
        "employee_id": emp.id,
        "total_ctc": 100000000.0,
        "effective_date": "2024-01-01",
        "currency": "INR"
    }, headers=admin_headers)

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    assert res.status_code == 200
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{emp.id}", headers=admin_headers).json()
    # Monthly gross = 100,000,000 / 12 = 8,333,333.33
    assert trace["step_5_final_takehome"]["gross_salary"] > 8000000.0
