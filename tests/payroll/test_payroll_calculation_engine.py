def test_payroll_calculation_engine_and_trace_tree(client, admin_headers, employee_user):
    # 1. Fetch Payroll Periods
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    assert periods_resp.status_code == 200
    periods = periods_resp.json()
    assert len(periods) >= 1
    period_id = periods[0]["id"]

    # 2. Execute Payroll Calculation Engine
    calc_resp = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    assert calc_resp.status_code == 200
    run_data = calc_resp.json()
    assert run_data["status"] == "Calculated"
    assert run_data["total_employees"] >= 1
    assert run_data["total_gross"] > 0
    run_id = run_data["id"]

    # 3. Fetch Step-by-Step Mathematical Calculation Trace Tree
    trace_resp = client.get(f"/api/v1/payroll/runs/{run_id}/trace/{employee_user.id}", headers=admin_headers)
    assert trace_resp.status_code == 200
    trace = trace_resp.json()
    assert "step_1_proration" in trace
    assert "step_2_earnings_breakdown" in trace
    assert "step_3_deductions_breakdown" in trace
    assert "step_5_final_takehome" in trace

    # 4. Approve and Lock Payroll Run
    app_resp = client.post(f"/api/v1/payroll/runs/{run_id}/approve", headers=admin_headers)
    assert app_resp.status_code == 200
    assert app_resp.json()["status"] == "Approved"

    lock_resp = client.post(f"/api/v1/payroll/runs/{run_id}/lock", headers=admin_headers)
    assert lock_resp.status_code == 200
    assert lock_resp.json()["status"] == "Locked"

    # 5. Assert Locked Payroll Rejects Recalculation (Immutability Protection)
    re_calc_resp = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    assert re_calc_resp.status_code == 400
    assert re_calc_resp.json()["error_code"] == "PAYROLL_ALREADY_LOCKED"
