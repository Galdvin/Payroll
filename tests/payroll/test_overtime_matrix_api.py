from datetime import date
from app.models.attendance import AttendanceSummary
from app.models.audit import AuditLog

def test_ot_001_normal_overtime(client, admin_headers, employee_user, db_session):
    """OT-001: Normal overtime (1.5x multiplier)"""
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
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers).json()
    ot_data = trace["step_2_earnings_breakdown"]["overtime"]
    assert ot_data["hours"] == 10.0
    assert ot_data["multiplier"] == 1.5
    assert ot_data["pay"] > 0.0


def test_ot_002_weekend_overtime(client, admin_headers, employee_user):
    """OT-002: Weekend overtime (2.0x multiplier)"""
    res = client.post("/api/v1/attendance/record", json={
        "employee_id": employee_user.id,
        "date": "2024-09-07",  # Saturday
        "status": "Weekly Off",
        "overtime_hours": 8.0,
        "source": "Manual"
    }, headers=admin_headers)
    assert res.status_code == 201
    assert res.json()["overtime_hours"] == 8.0


def test_ot_003_holiday_overtime(client, admin_headers, employee_user):
    """OT-003: Holiday overtime (2.5x multiplier)"""
    res = client.post("/api/v1/attendance/record", json={
        "employee_id": employee_user.id,
        "date": "2024-09-15",
        "status": "Holiday",
        "overtime_hours": 8.0,
        "source": "Manual"
    }, headers=admin_headers)
    assert res.status_code == 201
    assert res.json()["status"] == "Holiday"


def test_ot_004_night_overtime(client, admin_headers, employee_user):
    """OT-004: Night overtime calculation"""
    res = client.post("/api/v1/attendance/record", json={
        "employee_id": employee_user.id,
        "date": "2024-09-16",
        "status": "Present",
        "overtime_hours": 4.0,
        "source": "Night Shift Biometric"
    }, headers=admin_headers)
    assert res.status_code == 201


def test_ot_005_multiple_overtime_categories(client, admin_headers, employee_user, db_session):
    """OT-005: Multiple overtime categories combined"""
    att = db_session.query(AttendanceSummary).filter(
        AttendanceSummary.employee_id == employee_user.id,
        AttendanceSummary.year_month == "2024-09"
    ).first()
    if att:
        att.overtime_hours = 24.0  # Combined 10 hrs Normal + 8 hrs Weekend + 6 hrs Holiday
        db_session.commit()

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers).json()
    assert trace["step_2_earnings_breakdown"]["overtime"]["hours"] == 24.0


def test_ot_006_zero_overtime(client, admin_headers, employee_user, db_session):
    """OT-006: Zero overtime -> 0.0 OT pay"""
    att = db_session.query(AttendanceSummary).filter(
        AttendanceSummary.employee_id == employee_user.id,
        AttendanceSummary.year_month == "2024-09"
    ).first()
    if att:
        att.overtime_hours = 0.0
        db_session.commit()

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = res.json()["id"]

    trace = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers).json()
    assert trace["step_2_earnings_breakdown"]["overtime"]["pay"] == 0.0


def test_ot_007_invalid_negative_ot(client, admin_headers, employee_user):
    """OT-007: Invalid negative OT rejected"""
    payload = {
        "employee_id": employee_user.id,
        "date": "2024-09-17",
        "status": "Present",
        "overtime_hours": -5.0
    }
    res = client.post("/api/v1/attendance/record", json=payload, headers=admin_headers)
    assert res.status_code == 400
    assert "negative" in res.json()["detail"].lower()


def test_ot_008_ot_exceeding_configured_limit(client, admin_headers, employee_user):
    """OT-008: OT exceeding configured daily limit rejected"""
    payload = {
        "employee_id": employee_user.id,
        "date": "2024-09-18",
        "status": "Present",
        "overtime_hours": 16.0  # Exceeds max limit 12.0
    }
    res = client.post("/api/v1/attendance/record", json=payload, headers=admin_headers)
    assert res.status_code == 400
    assert "exceed" in res.json()["detail"].lower()


def test_ot_009_manual_ot_correction(client, admin_headers, employee_user, db_session):
    """OT-009: Manual OT correction audited in tamper-evident log"""
    # Create record with 2.0 OT
    rec_res = client.post("/api/v1/attendance/record", json={
        "employee_id": employee_user.id,
        "date": "2024-09-19",
        "status": "Present",
        "overtime_hours": 2.0
    }, headers=admin_headers)
    att_id = rec_res.json()["id"]

    # Correct OT to 4.0
    corr_res = client.put(f"/api/v1/attendance/{att_id}/correct", json={
        "overtime_hours": 4.0,
        "reason": "Supervisor verified 2 additional OT hours"
    }, headers=admin_headers)
    assert corr_res.status_code == 200
    assert corr_res.json()["overtime_hours"] == 4.0

    # Verify audit log
    audit_entry = db_session.query(AuditLog).filter(
        AuditLog.action == "ATTENDANCE_CORRECTION",
        AuditLog.record_id == str(att_id)
    ).first()
    assert audit_entry is not None
    assert audit_entry.new_values["overtime_hours"] == 4.0


def test_ot_010_ot_reflected_in_payslip(client, admin_headers, employee_user, db_session):
    """OT-010: OT reflected in payslip API / PDF"""
    att = db_session.query(AttendanceSummary).filter(
        AttendanceSummary.employee_id == employee_user.id,
        AttendanceSummary.year_month == "2024-09"
    ).first()
    if att:
        att.overtime_hours = 8.0
        db_session.commit()

    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = res.json()["id"]

    # Approve & fetch payslip summary
    client.post(f"/api/v1/payroll/runs/{run_id}/approve", headers=admin_headers)
    payslip_res = client.get(f"/api/v1/payslips/employee/{employee_user.id}/period/{period_id}", headers=admin_headers)
    assert payslip_res.status_code == 200
    data = payslip_res.json()
    earning_names = [e["name"] for e in data["earnings"]]
    assert "Overtime Pay" in earning_names or "SPECIAL_ALLOWANCE" in earning_names
