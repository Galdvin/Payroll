from datetime import datetime, date
from app.models.audit import AuditLog

def test_att_001_mark_employee_present(client, admin_headers, employee_user):
    """ATT-001: Mark employee present"""
    payload = {
        "employee_id": employee_user.id,
        "date": "2024-09-01",
        "status": "Present",
        "source": "Manual"
    }
    res = client.post("/api/v1/attendance/record", json=payload, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "Present"
    assert data["employee_id"] == employee_user.id


def test_att_002_mark_absent(client, admin_headers, employee_user):
    """ATT-002: Mark absent"""
    payload = {
        "employee_id": employee_user.id,
        "date": "2024-09-02",
        "status": "Absent",
        "source": "Manual"
    }
    res = client.post("/api/v1/attendance/record", json=payload, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "Absent"


def test_att_003_half_day(client, admin_headers, employee_user):
    """ATT-003: Half day"""
    payload = {
        "employee_id": employee_user.id,
        "date": "2024-09-03",
        "status": "Half Day",
        "source": "Manual"
    }
    res = client.post("/api/v1/attendance/record", json=payload, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "Half Day"


def test_att_004_check_in_check_out_working_hours(client, admin_headers, employee_user):
    """ATT-004: Check-in/check-out working hours calculated"""
    checkin_payload = {
        "employee_id": employee_user.id,
        "date": "2024-09-04",
        "check_in_time": "2024-09-04T09:00:00Z"
    }
    in_res = client.post("/api/v1/attendance/check-in", json=checkin_payload, headers=admin_headers)
    assert in_res.status_code == 200

    checkout_payload = {
        "employee_id": employee_user.id,
        "date": "2024-09-04",
        "check_out_time": "2024-09-04T17:00:00Z"  # 8 hours
    }
    out_res = client.post("/api/v1/attendance/check-out", json=checkout_payload, headers=admin_headers)
    assert out_res.status_code == 200
    data = out_res.json()
    assert data["check_in"] is not None
    assert data["check_out"] is not None


def test_att_005_late_arrival(client, admin_headers, employee_user):
    """ATT-005: Late arrival status calculated"""
    checkin_payload = {
        "employee_id": employee_user.id,
        "date": "2024-09-05",
        "check_in_time": "2024-09-05T09:45:00Z"  # 45 minutes late (shift start 09:00)
    }
    res = client.post("/api/v1/attendance/check-in", json=checkin_payload, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["late_minutes"] == 45


def test_att_006_early_departure(client, admin_headers, employee_user):
    """ATT-006: Early departure correctly calculated"""
    # Check in on time
    client.post("/api/v1/attendance/check-in", json={
        "employee_id": employee_user.id,
        "date": "2024-09-06",
        "check_in_time": "2024-09-06T09:00:00Z"
    }, headers=admin_headers)

    # Check out 90 minutes early (16:30 vs 18:00 standard end)
    res = client.post("/api/v1/attendance/check-out", json={
        "employee_id": employee_user.id,
        "date": "2024-09-06",
        "check_out_time": "2024-09-06T16:30:00Z"
    }, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["early_departure_minutes"] == 90


def test_att_007_overtime(client, admin_headers, employee_user):
    """ATT-007: Overtime hours calculated"""
    client.post("/api/v1/attendance/check-in", json={
        "employee_id": employee_user.id,
        "date": "2024-09-07",
        "check_in_time": "2024-09-07T09:00:00Z"
    }, headers=admin_headers)

    res = client.post("/api/v1/attendance/check-out", json={
        "employee_id": employee_user.id,
        "date": "2024-09-07",
        "check_out_time": "2024-09-07T19:00:00Z"  # 10 hours worked -> 2 hours OT
    }, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["overtime_hours"] == 2.0


def test_att_008_holiday_attendance(client, admin_headers, employee_user):
    """ATT-008: Holiday attendance work calculated"""
    payload = {
        "employee_id": employee_user.id,
        "date": "2024-09-08",
        "status": "Holiday",
        "overtime_hours": 8.0,
        "source": "Manual"
    }
    res = client.post("/api/v1/attendance/record", json=payload, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "Holiday"
    assert data["overtime_hours"] == 8.0


def test_att_009_duplicate_attendance(client, admin_headers, employee_user):
    """ATT-009: Duplicate attendance prevention"""
    payload = {
        "employee_id": employee_user.id,
        "date": "2024-09-09",
        "check_in_time": "2024-09-09T09:00:00Z"
    }
    # First check-in
    res1 = client.post("/api/v1/attendance/check-in?prevent_duplicate=true", json=payload, headers=admin_headers)
    assert res1.status_code == 200

    # Duplicate check-in attempt with prevent_duplicate=true
    res2 = client.post("/api/v1/attendance/check-in?prevent_duplicate=true", json=payload, headers=admin_headers)
    assert res2.status_code == 400
    assert "Duplicate" in res2.json()["detail"]


def test_att_010_bulk_attendance_import(client, admin_headers, employee_user):
    """ATT-010: Bulk attendance import valid records"""
    payload = {
        "records": [
            {
                "employee_id": employee_user.id,
                "date": "2024-09-10",
                "status": "Present",
                "source": "Import"
            },
            {
                "employee_id": employee_user.id,
                "date": "2024-09-11",
                "status": "Present",
                "source": "Import"
            }
        ]
    }
    res = client.post("/api/v1/attendance/bulk-import", json=payload, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert data[0]["source"] == "Import"


def test_att_011_invalid_employee_in_import(client, admin_headers, employee_user):
    """ATT-011: Invalid employee in import raises error"""
    payload = {
        "records": [
            {
                "employee_id": 999999,  # Non-existent employee
                "date": "2024-09-12",
                "status": "Present",
                "source": "Import"
            }
        ]
    }
    res = client.post("/api/v1/attendance/bulk-import", json=payload, headers=admin_headers)
    assert res.status_code == 400
    assert "Invalid employee ID" in res.json()["detail"]


def test_att_012_attendance_correction_audit(client, admin_headers, employee_user, db_session):
    """ATT-012: Attendance correction change audited in tamper-evident log"""
    # Create initial attendance record
    rec_res = client.post("/api/v1/attendance/record", json={
        "employee_id": employee_user.id,
        "date": "2024-09-13",
        "status": "Absent"
    }, headers=admin_headers)
    att_id = rec_res.json()["id"]

    # Perform correction to "Present"
    corr_res = client.put(f"/api/v1/attendance/{att_id}/correct", json={
        "status": "Present",
        "reason": "Employee presented manual sign-in sheet"
    }, headers=admin_headers)
    assert corr_res.status_code == 200
    assert corr_res.json()["status"] == "Present"

    # Verify audit log entry
    audit_entry = db_session.query(AuditLog).filter(
        AuditLog.action == "ATTENDANCE_CORRECTION",
        AuditLog.record_id == str(att_id)
    ).first()
    assert audit_entry is not None
    assert audit_entry.old_values["status"] == "Absent"
    assert audit_entry.new_values["status"] == "Present"
    assert audit_entry.hash_checksum is not None
