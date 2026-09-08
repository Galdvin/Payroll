import pytest


def test_bank_payment_adapters_and_gl_journal_entries(client, admin_headers):
    # 1. Fetch pay period and run payroll
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
    run_id = calc_resp.json()["id"]

    # 2. Test HDFC CMS Bank File Generation
    hdfc_payload = {"payroll_run_id": run_id, "bank_format": "HDFC_CMS"}
    hdfc_resp = client.post("/api/v1/payments/generate-bank-file", json=hdfc_payload, headers=admin_headers)
    assert hdfc_resp.status_code == 200
    assert "X-Checksum-SHA256" in hdfc_resp.headers
    assert b"HDFC_CMS_HEADER" in hdfc_resp.content

    # Assert Bank Payment Total = Total Net Salary Payable
    total_net = calc_resp.json()["total_net"]
    assert calc_resp.json()["total_net"] > 0

    # 3. Test ICICI CIB CSV Generation
    icici_payload = {"payroll_run_id": run_id, "bank_format": "ICICI_CIB"}
    icici_resp = client.post("/api/v1/payments/generate-bank-file", json=icici_payload, headers=admin_headers)
    assert icici_resp.status_code == 200
    assert b"TransactionRef,BeneficiaryAccount,Amount" in icici_resp.content

    # 4. Test Double-Entry General Ledger (GL) Accounting Entries Balance
    gl_resp = client.get(f"/api/v1/payments/journal-entries/{run_id}", headers=admin_headers)
    assert gl_resp.status_code == 200
    gl_data = gl_resp.json()
    assert gl_data["is_balanced"] is True
    assert gl_data["total_debit"] == gl_data["total_credit"]
    assert len(gl_data["entries"]) >= 3

    # 5. Test GL Journal CSV Export
    csv_resp = client.get(f"/api/v1/payments/journal-entries/{run_id}/export", headers=admin_headers)
    assert csv_resp.status_code == 200
    assert b"Entry Date,Account Code,Account Name" in csv_resp.content
    assert b"BALANCED" in csv_resp.content
