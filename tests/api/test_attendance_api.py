from datetime import datetime, date

def test_attendance_checkin_checkout_and_summary_flow(client, admin_headers, employee_user):
    # 1. Check in
    checkin_payload = {
        "employee_id": employee_user.id,
        "date": "2024-09-10",
        "check_in_time": "2024-09-10T09:00:00Z",
        "source": "Biometric"
    }
    in_resp = client.post("/api/v1/attendance/check-in", json=checkin_payload, headers=admin_headers)
    assert in_resp.status_code == 200
    assert in_resp.json()["status"] == "Present"

    # 2. Check out
    checkout_payload = {
        "employee_id": employee_user.id,
        "date": "2024-09-10",
        "check_out_time": "2024-09-10T19:00:00Z"  # 10 hours worked -> 2 hrs overtime
    }
    out_resp = client.post("/api/v1/attendance/check-out", json=checkout_payload, headers=admin_headers)
    assert out_resp.status_code == 200
    assert out_resp.json()["overtime_hours"] == 2.0

    # 3. Generate Monthly Attendance Summary for Payroll
    sum_resp = client.get(f"/api/v1/attendance/summary?employee_id={employee_user.id}&year_month=2024-09", headers=admin_headers)
    assert sum_resp.status_code == 200
    sum_data = sum_resp.json()
    assert sum_data["present_days"] >= 1.0
    assert sum_data["payable_days"] > 0
