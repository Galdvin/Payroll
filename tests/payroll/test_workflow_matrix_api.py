def test_wf_001_create_payroll(client, admin_headers):
    """WF-001: Create payroll period"""
    res = client.post("/api/v1/payroll/periods", json={
        "company_id": 1,
        "name": "December 2024 Payroll",
        "year_month": "2024-12",
        "start_date": "2024-12-01",
        "end_date": "2024-12-31",
        "cutoff_date": "2024-12-25"
    }, headers=admin_headers)
    assert res.status_code == 201
    assert res.json()["year_month"] == "2024-12"


def test_wf_002_calculate_payroll(client, admin_headers):
    """WF-002: Calculate payroll"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "Calculated"


def test_wf_003_validate_payroll(client, admin_headers):
    """WF-003: Validate payroll"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    calc_res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = calc_res.json()["id"]

    val_res = client.post(f"/api/v1/payroll/runs/{run_id}/status?target_status=Validated", headers=admin_headers)
    assert val_res.status_code == 200
    assert val_res.json()["status"] == "Validated"


def test_wf_004_submit_payroll(client, admin_headers):
    """WF-004: Submit payroll"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    calc_res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = calc_res.json()["id"]

    sub_res = client.post(f"/api/v1/payroll/runs/{run_id}/status?target_status=Submitted", headers=admin_headers)
    assert sub_res.status_code == 200
    assert sub_res.json()["status"] == "Submitted"


def test_wf_005_approve_payroll(client, admin_headers):
    """WF-005: Approve payroll"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    calc_res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = calc_res.json()["id"]

    app_res = client.post(f"/api/v1/payroll/runs/{run_id}/approve", headers=admin_headers)
    assert app_res.status_code == 200
    assert app_res.json()["status"] == "Approved"


def test_wf_006_reject_payroll(client, admin_headers):
    """WF-006: Reject payroll"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    calc_res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = calc_res.json()["id"]

    rej_res = client.post(f"/api/v1/payroll/runs/{run_id}/status?target_status=Rejected", headers=admin_headers)
    assert rej_res.status_code == 200
    assert rej_res.json()["status"] == "Rejected"


def test_wf_007_send_back_payroll(client, admin_headers):
    """WF-007: Send back payroll for corrections"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    calc_res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = calc_res.json()["id"]

    # Reject / Submit then send back to Calculated
    client.post(f"/api/v1/payroll/runs/{run_id}/status?target_status=Submitted", headers=admin_headers)
    back_res = client.post(f"/api/v1/payroll/runs/{run_id}/status?target_status=Calculated", headers=admin_headers)
    assert back_res.status_code == 200
    assert back_res.json()["status"] == "Calculated"


def test_wf_008_lock_payroll(client, admin_headers):
    """WF-008: Lock payroll"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    calc_res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = calc_res.json()["id"]

    lock_res = client.post(f"/api/v1/payroll/runs/{run_id}/lock", headers=admin_headers)
    assert lock_res.status_code == 200
    assert lock_res.json()["status"] == "Locked"


def test_wf_009_attempt_modification_after_lock(client, admin_headers):
    """WF-009: Attempt modification after lock (rejected)"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    # Ensure period is locked
    calc_res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = calc_res.json()["id"]
    client.post(f"/api/v1/payroll/runs/{run_id}/lock", headers=admin_headers)

    # Recalculate locked period
    re_res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    assert re_res.status_code == 400
    assert re_res.json()["error_code"] == "PAYROLL_ALREADY_LOCKED"


def test_wf_010_unlock_with_authorized_permission(client, admin_headers):
    """WF-010: Unlock with authorized permission"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    calc_res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = calc_res.json()["id"]
    client.post(f"/api/v1/payroll/runs/{run_id}/lock", headers=admin_headers)

    unlock_res = client.post(f"/api/v1/payroll/runs/{run_id}/unlock", headers=admin_headers)
    assert unlock_res.status_code == 200
    assert unlock_res.json()["status"] == "Calculated"


def test_wf_011_unauthorized_unlock(client, employee_headers):
    """WF-011: Unauthorized unlock (rejected 403)"""
    res = client.post("/api/v1/payroll/runs/1/unlock", headers=employee_headers)
    assert res.status_code == 403


def test_wf_012_close_payroll(client, admin_headers):
    """WF-012: Close payroll period"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    calc_res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = calc_res.json()["id"]

    close_res = client.post(f"/api/v1/payroll/runs/{run_id}/status?target_status=Closed", headers=admin_headers)
    assert close_res.status_code == 200
    assert close_res.json()["status"] == "Closed"
