from datetime import date

def test_leave_001_apply_annual_leave(client, admin_headers, employee_user):
    """LEAVE-001: Apply annual leave"""
    types_resp = client.get("/api/v1/leaves/types", headers=admin_headers)
    annual_id = [t for t in types_resp.json() if t["code"] == "AL"][0]["id"]

    payload = {
        "employee_id": employee_user.id,
        "leave_type_id": annual_id,
        "start_date": "2024-10-01",
        "end_date": "2024-10-03",
        "reason": "Vacation"
    }
    res = client.post("/api/v1/leaves/requests", json=payload, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "Pending"
    assert data["total_days"] == 3.0


def test_leave_002_apply_leave_without_balance(client, admin_headers, employee_user):
    """LEAVE-002: Apply leave without balance (rejected)"""
    types_resp = client.get("/api/v1/leaves/types", headers=admin_headers)
    annual_id = [t for t in types_resp.json() if t["code"] == "AL"][0]["id"]

    # Request 50 days (exceeds standard 12 days quota)
    payload = {
        "employee_id": employee_user.id,
        "leave_type_id": annual_id,
        "start_date": "2024-11-01",
        "end_date": "2024-12-20",
        "reason": "Excessive leave request"
    }
    res = client.post("/api/v1/leaves/requests", json=payload, headers=admin_headers)
    assert res.status_code == 400
    assert "balance" in res.json()["detail"].lower()


def test_leave_003_manager_approves(client, admin_headers, employee_user):
    """LEAVE-003: Manager approves leave request -> Balance reduced"""
    types_resp = client.get("/api/v1/leaves/types", headers=admin_headers)
    annual_id = [t for t in types_resp.json() if t["code"] == "AL"][0]["id"]

    # Apply
    apply_res = client.post("/api/v1/leaves/requests", json={
        "employee_id": employee_user.id,
        "leave_type_id": annual_id,
        "start_date": "2024-05-10",
        "end_date": "2024-05-12",
        "reason": "Family function"
    }, headers=admin_headers)
    req_id = apply_res.json()["id"]

    # Approve
    app_res = client.post(f"/api/v1/leaves/requests/{req_id}/approve", json={
        "status": "Approved",
        "approval_comments": "Approved"
    }, headers=admin_headers)
    assert app_res.status_code == 200
    assert app_res.json()["status"] == "Approved"

    # Check balance
    bal_res = client.get(f"/api/v1/leaves/balances?employee_id={employee_user.id}&year=2024", headers=admin_headers)
    al_bal = [b for b in bal_res.json() if b["leave_type_id"] == annual_id][0]
    assert al_bal["used"] == 3.0
    assert al_bal["total_balance"] == 9.0


def test_leave_004_manager_rejects(client, admin_headers, employee_user):
    """LEAVE-004: Manager rejects -> Balance unchanged"""
    types_resp = client.get("/api/v1/leaves/types", headers=admin_headers)
    annual_id = [t for t in types_resp.json() if t["code"] == "AL"][0]["id"]

    apply_res = client.post("/api/v1/leaves/requests", json={
        "employee_id": employee_user.id,
        "leave_type_id": annual_id,
        "start_date": "2024-06-01",
        "end_date": "2024-06-02",
        "reason": "Weekend trip"
    }, headers=admin_headers)
    req_id = apply_res.json()["id"]

    rej_res = client.post(f"/api/v1/leaves/requests/{req_id}/approve", json={
        "status": "Rejected",
        "approval_comments": "Project deadline"
    }, headers=admin_headers)
    assert rej_res.status_code == 200
    assert rej_res.json()["status"] == "Rejected"


def test_leave_005_cancel_leave(client, admin_headers, employee_user):
    """LEAVE-005: Cancel leave -> Balance restored"""
    types_resp = client.get("/api/v1/leaves/types", headers=admin_headers)
    annual_id = [t for t in types_resp.json() if t["code"] == "AL"][0]["id"]

    apply_res = client.post("/api/v1/leaves/requests", json={
        "employee_id": employee_user.id,
        "leave_type_id": annual_id,
        "start_date": "2024-07-01",
        "end_date": "2024-07-02",
        "reason": "Personal work"
    }, headers=admin_headers)
    req_id = apply_res.json()["id"]

    # Cancel request
    cancel_res = client.post(f"/api/v1/leaves/requests/{req_id}/cancel", headers=admin_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "Cancelled"


def test_leave_006_unpaid_leave(client, admin_headers, employee_user):
    """LEAVE-006: Unpaid leave -> Attendance marked as Unpaid Leave"""
    types_resp = client.get("/api/v1/leaves/types", headers=admin_headers)
    unpaid_id = [t for t in types_resp.json() if t["code"] == "UL"][0]["id"]

    apply_res = client.post("/api/v1/leaves/requests", json={
        "employee_id": employee_user.id,
        "leave_type_id": unpaid_id,
        "start_date": "2024-08-10",
        "end_date": "2024-08-11",
        "reason": "Leave without pay"
    }, headers=admin_headers)
    req_id = apply_res.json()["id"]

    app_res = client.post(f"/api/v1/leaves/requests/{req_id}/approve", json={
        "status": "Approved"
    }, headers=admin_headers)
    assert app_res.status_code == 200

    # Verify attendance status
    att_res = client.get(f"/api/v1/attendance?employee_id={employee_user.id}&start_date=2024-08-10&end_date=2024-08-11", headers=admin_headers)
    records = att_res.json()
    assert len(records) >= 1
    assert records[0]["status"] == "Unpaid Leave"


def test_leave_007_leave_crossing_payroll_period(client, admin_headers, employee_user):
    """LEAVE-007: Leave crossing payroll period (Sep 28 to Oct 02)"""
    types_resp = client.get("/api/v1/leaves/types", headers=admin_headers)
    annual_id = [t for t in types_resp.json() if t["code"] == "AL"][0]["id"]

    apply_res = client.post("/api/v1/leaves/requests", json={
        "employee_id": employee_user.id,
        "leave_type_id": annual_id,
        "start_date": "2024-09-28",
        "end_date": "2024-10-02",
        "reason": "Cross-month holiday"
    }, headers=admin_headers)
    assert apply_res.status_code == 201
    assert apply_res.json()["total_days"] == 5.0

    # Approve
    req_id = apply_res.json()["id"]
    client.post(f"/api/v1/leaves/requests/{req_id}/approve", json={"status": "Approved"}, headers=admin_headers)

    # Check monthly summaries for Sep and Oct
    sep_sum = client.get(f"/api/v1/attendance/summary?employee_id={employee_user.id}&year_month=2024-09", headers=admin_headers).json()
    oct_sum = client.get(f"/api/v1/attendance/summary?employee_id={employee_user.id}&year_month=2024-10", headers=admin_headers).json()

    assert sep_sum["paid_leave_days"] >= 3.0  # Sep 28, 29, 30
    assert oct_sum["paid_leave_days"] >= 2.0  # Oct 01, 02


def test_leave_008_holiday_inside_leave_period(client, admin_headers, employee_user):
    """LEAVE-008: Holiday inside leave period excluded from leave days"""
    # Create official holiday on 2024-08-15 (Independence Day)
    client.post("/api/v1/leaves/holidays", json={
        "company_id": 1,
        "name": "Independence Day",
        "date": "2024-08-15",
        "holiday_type": "National"
    }, headers=admin_headers)

    types_resp = client.get("/api/v1/leaves/types", headers=admin_headers)
    annual_id = [t for t in types_resp.json() if t["code"] == "AL"][0]["id"]

    # Apply 3-day leave spanning Aug 14 to Aug 16 (includes Aug 15 holiday)
    apply_res = client.post("/api/v1/leaves/requests", json={
        "employee_id": employee_user.id,
        "leave_type_id": annual_id,
        "start_date": "2024-08-14",
        "end_date": "2024-08-16",
        "reason": "August break"
    }, headers=admin_headers)
    assert apply_res.status_code == 201
    assert apply_res.json()["total_days"] == 2.0  # 3 calendar days - 1 holiday = 2 net leave days


def test_leave_009_carry_forward_leave(client, admin_headers, employee_user):
    """LEAVE-009: Carry-forward leave from 2024 to 2025"""
    cf_res = client.post("/api/v1/leaves/carry-forward", json={
        "employee_id": employee_user.id,
        "from_year": 2024,
        "to_year": 2025,
        "max_carry_forward": 5.0
    }, headers=admin_headers)
    assert cf_res.status_code == 200
    data = cf_res.json()
    assert data["carried_forward_days"] > 0
    assert data["to_year"] == 2025


def test_leave_010_leave_encashment(client, admin_headers, employee_user):
    """LEAVE-010: Leave encashment correct payment calculation"""
    types_resp = client.get("/api/v1/leaves/types", headers=admin_headers)
    annual_id = [t for t in types_resp.json() if t["code"] == "AL"][0]["id"]

    enc_res = client.post("/api/v1/leaves/encash", json={
        "employee_id": employee_user.id,
        "leave_type_id": annual_id,
        "days": 3.0,
        "year": 2024,
        "daily_rate": 2000.0
    }, headers=admin_headers)
    assert enc_res.status_code == 200
    data = enc_res.json()
    assert data["days_encashed"] == 3.0
    assert data["encashment_amount"] == 6000.0
