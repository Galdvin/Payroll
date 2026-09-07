from datetime import date
from app.models.employee import Employee
from app.models.attendance import AttendanceSummary


def test_pror_001_join_on_first(client, admin_headers, db_session):
    """PROR-001: Employee joins on 1st -> Full 100% salary"""
    emp = Employee(
        company_id=1,
        employee_code="EMP_PROR_01",
        first_name="FirstDay",
        last_name="Joiner",
        email="firstday@company.com",
        date_of_joining=date(2024, 9, 1),
        is_active=True
    )
    db_session.add(emp)
    db_session.commit()

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{emp.id}", headers=admin_headers).json()
    assert trace["step_1_proration"]["payable_days"] == 30.0
    assert trace["step_1_proration"]["proration_factor"] == 1.0


def test_pror_002_join_mid_month(client, admin_headers, db_session):
    """PROR-002: Employee joins mid-month (16th) -> 50% prorated salary"""
    emp = Employee(
        company_id=1,
        employee_code="EMP_PROR_02",
        first_name="MidMonth",
        last_name="Joiner",
        email="midmonth@company.com",
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


def test_pror_003_join_last_day(client, admin_headers, db_session):
    """PROR-003: Employee joins last day of month (30th) -> 1/30th prorated salary"""
    emp = Employee(
        company_id=1,
        employee_code="EMP_PROR_03",
        first_name="LastDay",
        last_name="Joiner",
        email="lastday@company.com",
        date_of_joining=date(2024, 9, 30),
        is_active=True
    )
    db_session.add(emp)
    db_session.commit()

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{emp.id}", headers=admin_headers).json()
    assert trace["step_1_proration"]["payable_days"] == 1.0
    assert trace["step_1_proration"]["proration_factor"] == 0.0333


def test_pror_004_resign_mid_month(client, admin_headers, db_session):
    """PROR-004: Employee resigns mid-month (15th) -> 50% prorated salary"""
    emp = Employee(
        company_id=1,
        employee_code="EMP_PROR_04",
        first_name="MidResign",
        last_name="Staff",
        email="midresign@company.com",
        date_of_joining=date(2023, 1, 1),
        resignation_date=date(2024, 9, 15),
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
    assert trace["step_1_proration"]["payable_days"] == 15.0
    assert trace["step_1_proration"]["proration_factor"] == 0.5000


def test_pror_005_resign_last_day(client, admin_headers, db_session):
    """PROR-005: Employee resigns on last day (30th) -> Full 100% salary"""
    emp = Employee(
        company_id=1,
        employee_code="EMP_PROR_05",
        first_name="LastDayResign",
        last_name="Staff",
        email="lastdayresign@company.com",
        date_of_joining=date(2023, 1, 1),
        resignation_date=date(2024, 9, 30),
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
    assert trace["step_1_proration"]["payable_days"] == 30.0
    assert trace["step_1_proration"]["proration_factor"] == 1.0


def test_pror_006_unpaid_leave(client, admin_headers, employee_user, db_session):
    """PROR-006: Unpaid leave deduction (5 days unpaid leave)"""
    att = db_session.query(AttendanceSummary).filter(
        AttendanceSummary.employee_id == employee_user.id,
        AttendanceSummary.year_month == "2024-09"
    ).first()
    if att:
        att.payable_days = 25.0
        db_session.commit()

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers).json()
    assert trace["step_1_proration"]["payable_days"] == 25.0
    assert trace["step_1_proration"]["proration_factor"] == 0.8333


def test_pror_007_salary_revision_mid_month(client, admin_headers, employee_user):
    """PROR-007: Salary revision mid-month"""
    client.post("/api/v1/salary/revisions", json={
        "employee_id": employee_user.id,
        "new_ctc": 840000.0,
        "effective_date": "2024-09-16",
        "revision_reason": "Mid-month promotion"
    }, headers=admin_headers)

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    assert res.status_code == 200


def test_pror_008_different_month_lengths(client, admin_headers):
    """PROR-008: Different month lengths (31-day October period)"""
    # Create October 2024 period (31 days)
    p_res = client.post("/api/v1/payroll/periods", json={
        "company_id": 1,
        "name": "October 2024 Payroll",
        "year_month": "2024-10",
        "start_date": "2024-10-01",
        "end_date": "2024-10-31",
        "cutoff_date": "2024-10-25"
    }, headers=admin_headers)
    assert p_res.status_code == 201
    oct_period_id = p_res.json()["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": oct_period_id}, headers=admin_headers)
    assert res.status_code == 200
    run_id = res.json()["id"]
    assert res.json()["status"] == "Calculated"


def test_pror_009_leap_year(client, admin_headers):
    """PROR-009: Leap year February payroll (Feb 2024 = 29 days)"""
    p_res = client.post("/api/v1/payroll/periods", json={
        "company_id": 1,
        "name": "February 2024 Leap Year Payroll",
        "year_month": "2024-02",
        "start_date": "2024-02-01",
        "end_date": "2024-02-29",
        "cutoff_date": "2024-02-25"
    }, headers=admin_headers)
    assert p_res.status_code == 201
    feb_period_id = p_res.json()["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": feb_period_id}, headers=admin_headers)
    assert res.status_code == 200


def test_pror_010_february_payroll(client, admin_headers):
    """PROR-010: Standard February payroll (Feb 2023 = 28 days)"""
    p_res = client.post("/api/v1/payroll/periods", json={
        "company_id": 1,
        "name": "February 2023 Payroll",
        "year_month": "2023-02",
        "start_date": "2023-02-01",
        "end_date": "2023-02-28",
        "cutoff_date": "2023-02-25"
    }, headers=admin_headers)
    assert p_res.status_code == 201
    feb23_period_id = p_res.json()["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": feb23_period_id}, headers=admin_headers)
    assert res.status_code == 200
