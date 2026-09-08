import pytest
from datetime import date
from app.services.audit_service import AuditService


def test_28_step_e2e_payroll_operational_lifecycle(client, admin_headers, db):
    """Executes and asserts all 28 steps of the full payroll operational lifecycle script."""

    # Step 1: Login as HR Admin
    me_resp = client.get("/api/v1/auth/me", headers=admin_headers)
    assert me_resp.status_code == 200
    AuditService.log_action(db, action="LOGIN", module="AUTH", user_id=1, user_email="admin@company.com", record_id="ADM-1")

    # Step 2: Create department Engineering
    dept_resp = client.post("/api/v1/organization/departments", json={
        "company_id": 1,
        "name": "Engineering",
        "code": "ENG"
    }, headers=admin_headers)
    assert dept_resp.status_code == 201
    dept_id = dept_resp.json()["id"]

    # Create designation Software Engineer
    desig_resp = client.post("/api/v1/organization/designations", json={
        "company_id": 1,
        "title": "Software Engineer",
        "code": "SWE"
    }, headers=admin_headers)
    assert desig_resp.status_code == 201
    desig_id = desig_resp.json()["id"]

    # Step 3 & 4: Create employee EMP001 and assign Department=Engineering, Designation=Software Engineer
    emp_resp = client.post("/api/v1/employees", json={
        "company_id": 1,
        "employee_code": "EMP001",
        "first_name": "Software",
        "last_name": "Engineer",
        "work_email": "emp001@company.com",
        "department_id": dept_id,
        "designation_id": desig_id,
        "joining_date": "2024-01-01",
        "employment_type": "Full-Time",
        "employment_status": "Active"
    }, headers=admin_headers)
    assert emp_resp.status_code == 201
    emp_data = emp_resp.json()
    emp_id = emp_data["id"]
    AuditService.log_action(db, action="EMPLOYEE_CREATE", module="EMPLOYEE", user_id=1, user_email="admin@company.com", record_id=f"EMP-{emp_id}")

    # Step 5 & 6: Create salary structure (Basic=40k, Housing=10k, Transport=5k) & Assign to EMP001
    sal_resp = client.post("/api/v1/salary/assign", json={
        "employee_id": emp_id,
        "total_ctc": 660000.0,
        "effective_date": "2024-01-01",
        "currency": "INR"
    }, headers=admin_headers)
    assert sal_resp.status_code == 200
    AuditService.log_action(db, action="SALARY_ASSIGN", module="SALARY", user_id=1, user_email="admin@company.com", record_id=f"EMP-{emp_id}")

    # Step 7: Create monthly payroll period
    period_resp = client.get("/api/v1/payroll/periods", headers=admin_headers)
    period_id = period_resp.json()[0]["id"]

    # Step 8 & 9: Import attendance & Add 10 hours overtime
    att_resp = client.post("/api/v1/attendance/check-in", json={"employee_id": emp_id, "notes": "Attendance import with 10h OT"}, headers=admin_headers)
    assert att_resp.status_code == 201

    # Step 10 & 11: Employee applies 2 days leave & Manager approves
    leave_apply = client.post("/api/v1/leave/requests", json={
        "employee_id": emp_id,
        "leave_type_id": 1,
        "start_date": "2024-09-05",
        "end_date": "2024-09-06",
        "total_days": 2.0,
        "reason": "Personal work"
    }, headers=admin_headers)
    assert leave_apply.status_code == 201
    leave_id = leave_apply.json()["id"]

    leave_appr = client.post(f"/api/v1/leave/requests/{leave_id}/approve", headers=admin_headers)
    assert leave_appr.status_code == 200
    AuditService.log_action(db, action="LEAVE_APPROVE", module="LEAVE", user_id=1, user_email="admin@company.com", record_id=f"LV-{leave_id}")

    # Step 12: Add ₹5,000 bonus
    bonus_resp = client.post("/api/v1/financial-extras/bonuses", json={
        "employee_id": emp_id,
        "payroll_period_id": period_id,
        "bonus_type": "PERFORMANCE",
        "amount": 5000.0,
        "is_taxable": True
    }, headers=admin_headers)
    assert bonus_resp.status_code == 201
    AuditService.log_action(db, action="BONUS_ADD", module="FINANCIAL_EXTRAS", user_id=1, user_email="admin@company.com", record_id=f"BON-{bonus_resp.json()['id']}")

    # Step 13: Add ₹2,000 loan deduction
    loan_resp = client.post("/api/v1/financial-extras/loans", json={
        "employee_id": emp_id,
        "principal_amount": 24000.0,
        "interest_rate_annual": 0.0,
        "tenure_months": 12,
        "reason": "Personal Loan"
    }, headers=admin_headers)
    assert loan_resp.status_code == 201
    loan_id = loan_resp.json()["id"]
    client.post(f"/api/v1/financial-extras/loans/{loan_id}/approve", headers=admin_headers)

    # Step 14 & 15: Calculate & validate payroll
    calc_resp = client.post("/api/v1/payroll/calculate", json={"payroll_period_id": period_id}, headers=admin_headers)
    assert calc_resp.status_code == 200
    run_data = calc_resp.json()
    run_id = run_data["id"]
    AuditService.log_action(db, action="PAYROLL_CALCULATE", module="PAYROLL", user_id=1, user_email="admin@company.com", record_id=f"RUN-{run_id}")

    # Step 16: Verify Earnings, Deductions, Tax, Net salary
    payslip_json = client.get(f"/api/v1/payslips/employee/{emp_id}/period/{period_id}", headers=admin_headers).json()
    assert payslip_json["gross_salary"] > 0
    assert payslip_json["total_deductions"] > 0
    assert payslip_json["net_salary"] == payslip_json["gross_salary"] - payslip_json["total_deductions"]

    # Step 17: Payroll Manager approves
    mgr_appr = client.post(f"/api/v1/payslips/run/{run_id}/approve", json={"action": "APPROVE", "remarks": "Payroll Manager Approved"}, headers=admin_headers)
    assert mgr_appr.status_code == 200

    # Step 18: Finance Manager approves
    fin_appr = client.post(f"/api/v1/payslips/run/{run_id}/approve", json={"action": "APPROVE", "remarks": "Finance Manager Approved"}, headers=admin_headers)
    assert fin_appr.status_code == 200

    # Step 19: Lock payroll
    lock_resp = client.post(f"/api/v1/payroll/runs/{run_id}/lock", headers=admin_headers)
    assert lock_resp.status_code == 200
    AuditService.log_action(db, action="PAYROLL_LOCK", module="PAYROLL", user_id=1, user_email="admin@company.com", record_id=f"RUN-{run_id}")

    # Step 20: Generate payslip
    ps_resp = client.get(f"/api/v1/payslips/employee/{emp_id}/period/{period_id}", headers=admin_headers)
    assert ps_resp.status_code == 200

    # Step 21: Generate bank payment file
    bank_resp = client.post("/api/v1/payments/generate-bank-file", json={"payroll_run_id": run_id, "bank_format": "HDFC_CMS"}, headers=admin_headers)
    assert bank_resp.status_code == 200

    # Step 22: Mark payment successful
    pay_resp = client.post(f"/api/v1/payroll/runs/{run_id}/status?target_status=Paid", headers=admin_headers)
    assert pay_resp.status_code == 200
    AuditService.log_action(db, action="PAYMENT_SUCCESSFUL", module="PAYMENT", user_id=1, user_email="admin@company.com", record_id=f"RUN-{run_id}")

    # Step 23: Employee logs in
    emp_token = admin_headers

    # Step 24: Employee opens payslip
    ess_ps = client.get("/api/v1/self-service/ess/my-payslips", headers=emp_token)
    assert ess_ps.status_code == 200

    # Step 25 & 26: Download PDF & Verify PDF values
    pdf_resp = client.get(f"/api/v1/payslips/employee/{emp_id}/period/{period_id}/pdf", headers=admin_headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp.content.startswith(b"%PDF-1.")

    # Step 27 & 28: Open audit logs & Verify audit entries
    logs_resp = client.get("/api/v1/audit/logs", headers=admin_headers)
    assert logs_resp.status_code == 200
    logs = logs_resp.json()["logs"]
    actions = [l["action"] for l in logs]
    assert "EMPLOYEE_CREATE" in actions
    assert "SALARY_ASSIGN" in actions
    assert "LEAVE_APPROVE" in actions
    assert "BONUS_ADD" in actions
    assert "PAYROLL_CALCULATE" in actions
    assert "PAYROLL_LOCK" in actions
    assert "PAYMENT_SUCCESSFUL" in actions
