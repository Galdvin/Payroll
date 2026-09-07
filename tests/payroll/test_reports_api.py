import pytest


def test_payroll_reports_and_analytics(client, admin_headers):
    # 1. Fetch pay period & execute payroll
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

    # 2. Test Master Payroll Register API
    reg_resp = client.get(f"/api/v1/reports/payroll-register?period_id={period_id}", headers=admin_headers)
    assert reg_resp.status_code == 200
    reg_data = reg_resp.json()
    assert reg_data["total_employees"] >= 1
    assert "records" in reg_data
    assert reg_data["records"][0]["basic"] > 0

    # 3. Test PF ECR Text File Stream
    pf_resp = client.get(f"/api/v1/reports/pf-ecr/{period_id}", headers=admin_headers)
    assert pf_resp.status_code == 200
    assert b"#~#" in pf_resp.content

    # 4. Test Cost Center Breakdown
    cc_resp = client.get(f"/api/v1/reports/cost-center?period_id={period_id}", headers=admin_headers)
    assert cc_resp.status_code == 200
    cc_data = cc_resp.json()
    assert len(cc_data) >= 1

    # 5. Test Executive Analytics KPIs
    exec_resp = client.get("/api/v1/reports/executive-analytics", headers=admin_headers)
    assert exec_resp.status_code == 200
    exec_data = exec_resp.json()
    assert exec_data["total_runs_executed"] >= 1
    assert exec_data["total_ytd_gross"] > 0
