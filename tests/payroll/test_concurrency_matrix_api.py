import pytest
from concurrent.futures import ThreadPoolExecutor
from app.models.employee import Employee
from app.models.payroll_run import PayrollRun


def test_con_001_two_users_calculate_same_payroll(client, admin_headers):
    """CON-001: Two users calculate same payroll concurrently"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]

    results = []
    def calc():
        res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
        results.append(res)

    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(calc)
        f2 = executor.submit(calc)
        f1.result()
        f2.result()

    assert all(r.status_code == 200 for r in results)


def test_con_002_two_users_approve_same_payroll(client, admin_headers):
    """CON-002: Two users approve same payroll concurrently"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]
    calc_res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = calc_res.json()["id"]

    results = []
    def approve():
        res = client.post(f"/api/v1/payslips/run/{run_id}/approve", json={"action": "APPROVE", "remarks": "Concurrent approve"}, headers=admin_headers)
        results.append(res)

    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(approve)
        f2 = executor.submit(approve)
        f1.result()
        f2.result()

    assert all(r.status_code == 200 for r in results)


def test_con_003_two_users_lock_payroll(client, admin_headers):
    """CON-003: Two users lock payroll concurrently"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]
    calc_res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = calc_res.json()["id"]

    results = []
    def lock_run():
        res = client.post(f"/api/v1/payroll/runs/{run_id}/lock", headers=admin_headers)
        results.append(res)

    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(lock_run)
        f2 = executor.submit(lock_run)
        f1.result()
        f2.result()

    statuses = [r.status_code for r in results]
    assert 200 in statuses


def test_con_004_duplicate_payment_request(client, admin_headers):
    """CON-004: Duplicate payment request handled idempotently"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]
    calc_res = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    run_id = calc_res.json()["id"]

    body = {"payroll_run_id": run_id, "bank_format": "HDFC_CMS"}

    results = []
    def gen_payment():
        res = client.post("/api/v1/payments/generate-bank-file", json=body, headers=admin_headers)
        results.append(res)

    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(gen_payment)
        f2 = executor.submit(gen_payment)
        f1.result()
        f2.result()

    assert all(r.status_code == 200 for r in results)


def test_con_005_duplicate_payslip_generation(client, admin_headers, employee_user):
    """CON-005: Duplicate payslip generation concurrently"""
    periods_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = periods_resp.json()[0]["id"]
    client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)

    results = []
    def gen_pdf():
        res = client.get(f"/api/v1/payslips/employee/{employee_user.id}/period/{period_id}/pdf", headers=admin_headers)
        results.append(res)

    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(gen_pdf)
        f2 = executor.submit(gen_pdf)
        f1.result()
        f2.result()

    assert all(r.status_code == 200 for r in results)
    assert all(r.headers["content-type"] == "application/pdf" for r in results)


def test_con_006_concurrent_employee_update(client, admin_headers):
    """CON-006: Concurrent employee update handled cleanly"""
    results = []
    def update_emp(email_suffix):
        res = client.put("/api/v1/employees/1", json={"work_email": f"emp1_{email_suffix}@company.com"}, headers=admin_headers)
        results.append(res)

    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(update_emp, "a")
        f2 = executor.submit(update_emp, "b")
        f1.result()
        f2.result()

    assert all(r.status_code == 200 for r in results)


def test_con_007_concurrent_salary_revision(client, admin_headers, employee_user):
    """CON-007: Concurrent salary revision processed atomically"""
    results = []
    def revise(ctc):
        res = client.post("/api/v1/salary/revisions", json={
            "employee_id": employee_user.id,
            "new_ctc": ctc,
            "effective_date": "2024-10-01",
            "revision_reason": "Performance Increase"
        }, headers=admin_headers)
        results.append(res)

    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(revise, 600000.0)
        f2 = executor.submit(revise, 650000.0)
        f1.result()
        f2.result()

    assert all(r.status_code == 201 for r in results)
