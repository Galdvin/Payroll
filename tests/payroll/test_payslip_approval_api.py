import pytest


def test_payslip_pdf_and_approval_workflow(client, admin_headers):
    # 1. Execute a Payroll Run first to generate results
    period_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    assert period_resp.status_code == 200
    periods = period_resp.json()
    period_id = periods[0]["id"]

    run_payload = {
        "payroll_period_id": period_id,
        "company_id": 1,
        "auto_approve_attendance": True,
    }
    calc_resp = client.post("/api/v1/payroll/calculate", json=run_payload, headers=admin_headers)
    assert calc_resp.status_code == 200
    run_data = calc_resp.json()
    run_id = run_data["id"]
    assert run_data["status"] == "Calculated"

    # 2. Test Individual Payslip PDF Stream
    pdf_resp = client.get(f"/api/v1/payslips/employee/1/period/{period_id}/pdf", headers=admin_headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert pdf_resp.content.startswith(b"%PDF-1.")

    # 3. Test Step-by-Step Approval Workflow Transitions
    # Step 3a: Manager Approval
    appr1_resp = client.post(
        f"/api/v1/payslips/run/{run_id}/approve",
        json={"action": "APPROVE", "remarks": "Manager audit passed cleanly"},
        headers=admin_headers,
    )
    assert appr1_resp.status_code == 200
    assert appr1_resp.json()["status"] == "APPROVED"

    # Step 3b: Finance Approval
    appr2_resp = client.post(
        f"/api/v1/payslips/run/{run_id}/approve",
        json={"action": "APPROVE", "remarks": "Finance budget verified"},
        headers=admin_headers,
    )
    assert appr2_resp.status_code == 200
    assert appr2_resp.json()["status"] == "APPROVED"

    # Step 3c: Final Lock
    appr3_resp = client.post(
        f"/api/v1/payslips/run/{run_id}/approve",
        json={"action": "APPROVE", "remarks": "Final Org Lock executed"},
        headers=admin_headers,
    )
    assert appr3_resp.status_code == 200
    assert appr3_resp.json()["status"] == "APPROVED"

    # 4. Fetch Approval Log
    log_resp = client.get(f"/api/v1/payslips/run/{run_id}/approvals", headers=admin_headers)
    assert log_resp.status_code == 200
    logs = log_resp.json()
    assert len(logs) == 3

    # 5. Test Bulk Payslips ZIP Stream
    zip_resp = client.get(f"/api/v1/payslips/run/{run_id}/bulk-zip", headers=admin_headers)
    assert zip_resp.status_code == 200
    assert zip_resp.headers["content-type"] == "application/zip"
    assert zip_resp.content.startswith(b"PK\x03\x04")
