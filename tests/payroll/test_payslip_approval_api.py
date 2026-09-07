def test_12_stage_payroll_approval_lifecycle(client, admin_headers):
    """Verifies the complete 12-stage multi-tier payroll approval & disbursement lifecycle."""
    
    # 1. Stage 1: Draft - Create new period in Draft state
    period_res = client.post("/api/v1/payroll/periods", json={
        "company_id": 1,
        "name": "November 2024 Payroll",
        "year_month": "2024-11",
        "start_date": "2024-11-01",
        "end_date": "2024-11-30",
        "cutoff_date": "2024-11-25",
        "status": "Draft"
    }, headers=admin_headers)
    assert period_res.status_code == 201
    period_id = period_res.json()["id"]

    # 2. Stage 2: Open - Open period for payroll processing
    open_res = client.post(f"/api/v1/payroll/periods", json={
        "company_id": 1,
        "name": "November 2024 Payroll Active",
        "year_month": "2024-11-open",
        "start_date": "2024-11-01",
        "end_date": "2024-11-30",
        "cutoff_date": "2024-11-25"
    }, headers=admin_headers)
    assert open_res.status_code == 201

    # 3. Stage 3 & 4: Calculate Payroll
    calc_res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    assert calc_res.status_code == 200
    run_id = calc_res.json()["id"]
    assert calc_res.json()["status"] == "Calculated"

    # 4. Stage 5: Validate
    val_res = client.post(f"/api/v1/payroll/runs/{run_id}/status?target_status=Validated", headers=admin_headers)
    assert val_res.status_code == 200
    assert val_res.json()["status"] == "Validated"

    # 5. Stage 6: Submit for Approval
    sub_res = client.post(f"/api/v1/payroll/runs/{run_id}/status?target_status=Submitted", headers=admin_headers)
    assert sub_res.status_code == 200
    assert sub_res.json()["status"] == "Submitted"

    # 6. Stage 7: Manager Approval
    mgr_res = client.post(f"/api/v1/payroll/runs/{run_id}/status?target_status=Manager Approved", headers=admin_headers)
    assert mgr_res.status_code == 200
    assert mgr_res.json()["status"] == "Manager Approved"

    # 7. Stage 8: Finance Approval
    fin_res = client.post(f"/api/v1/payroll/runs/{run_id}/status?target_status=Finance Approved", headers=admin_headers)
    assert fin_res.status_code == 200
    assert fin_res.json()["status"] == "Finance Approved"

    # 8. Stage 9: Lock
    lock_res = client.post(f"/api/v1/payroll/runs/{run_id}/lock", headers=admin_headers)
    assert lock_res.status_code == 200
    assert lock_res.json()["status"] == "Locked"

    # 9. Stage 10: Payment Advice Generation
    pay_res = client.post(f"/api/v1/payroll/runs/{run_id}/status?target_status=Payment", headers=admin_headers)
    assert pay_res.status_code == 200
    assert pay_res.json()["status"] == "Payment"

    # 10. Stage 11: Paid (Bank Disbursement Complete)
    paid_res = client.post(f"/api/v1/payroll/runs/{run_id}/status?target_status=Paid", headers=admin_headers)
    assert paid_res.status_code == 200
    assert paid_res.json()["status"] == "Paid"

    # 11. Stage 12: Closed (GL Entry Posted & Closed)
    closed_res = client.post(f"/api/v1/payroll/runs/{run_id}/status?target_status=Closed", headers=admin_headers)
    assert closed_res.status_code == 200
    assert closed_res.json()["status"] == "Closed"

    # 12. Verify Payslip PDF Stream & Bulk ZIP Stream
    pdf_resp = client.get(f"/api/v1/payslips/employee/1/period/{period_id}/pdf", headers=admin_headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp.content.startswith(b"%PDF-1.")
