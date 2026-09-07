import pytest


def test_master_enterprise_payroll_e2e_lifecycle(client, admin_headers):
    """MASTER E2E INTEGRATION TEST SUITE

    Verifies the complete multi-tenant Enterprise Payroll Management System
    across all 12 system phases.
    """
    print("\n--- STAGE 1: AUTHENTICATION & RBAC PERMISSIONS ---")
    login_resp = client.post("/api/v1/auth/login", data={"username": "admin@payroll.com", "password": "AdminPassword123!"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    print("\n--- STAGE 2: ORGANIZATION STRUCTURE & EMPLOYEES ---")
    org_resp = client.get("/api/v1/organization/companies", headers=auth_headers)
    assert org_resp.status_code == 200
    companies = org_resp.json()
    assert len(companies) >= 1
    company_id = companies[0]["id"]

    emp_resp = client.get("/api/v1/employees/", headers=auth_headers)
    assert emp_resp.status_code == 200
    employees = emp_resp.json()
    assert len(employees) >= 1

    print("\n--- STAGE 3: ATTENDANCE & PAYABLE DAYS SUMMARY ---")
    att_resp = client.get(f"/api/v1/attendance/summary?company_id={company_id}&year_month=2024-09", headers=auth_headers)
    assert att_resp.status_code == 200

    print("\n--- STAGE 4: DYNAMIC CTC BREAKDOWN & SALARY STRUCTURE ---")
    ctc_payload = {"annual_ctc": 1200000.0, "basic_percentage": 50.0, "hra_percentage": 40.0}
    ctc_resp = client.post("/api/v1/salary/evaluate-ctc", json=ctc_payload, headers=auth_headers)
    assert ctc_resp.status_code == 200
    ctc_data = ctc_resp.json()
    assert ctc_data["monthly_basic"] == 50000.0
    assert ctc_data["monthly_hra"] == 20000.0

    print("\n--- STAGE 5: TAX & STATUTORY EVALUATION (INDIA SLABS) ---")
    tds_resp = client.post("/api/v1/tax-statutory/evaluate-tds", json={"gross_monthly_salary": 100000.0, "regime_name": "New Regime"}, headers=auth_headers)
    assert tds_resp.status_code == 200
    tds_data = tds_resp.json()
    assert tds_data["standard_deduction"] == 75000.0
    assert tds_data["monthly_tds"] > 0

    print("\n--- STAGE 6: LOANS, ADVANCES, BONUSES & REIMBURSEMENTS ---")
    # Loan
    loan_resp = client.post(
        "/api/v1/financial-extras/loans",
        json={"employee_id": 1, "principal_amount": 100000.0, "interest_rate_annual": 10.0, "tenure_months": 12, "reason": "Home Loan"},
        headers=auth_headers,
    )
    assert loan_resp.status_code == 201
    loan_id = loan_resp.json()["id"]
    client.post(f"/api/v1/financial-extras/loans/{loan_id}/approve", headers=auth_headers)

    # Bonus
    bonus_resp = client.post(
        "/api/v1/financial-extras/bonuses",
        json={"employee_id": 1, "payroll_period_id": 1, "bonus_type": "PERFORMANCE", "amount": 20000.0, "is_taxable": True},
        headers=auth_headers,
    )
    assert bonus_resp.status_code == 201

    print("\n--- STAGE 7: PAYROLL CALCULATION ENGINE & TRACE TREE ---")
    period_resp = client.get("/api/v1/payroll/periods", headers=auth_headers)
    assert period_resp.status_code == 200
    period_id = period_resp.json()[0]["id"]

    calc_resp = client.post(
        "/api/v1/payroll/calculate",
        json={"payroll_period_id": period_id, "company_id": company_id, "auto_approve_attendance": True},
        headers=auth_headers,
    )
    assert calc_resp.status_code == 200
    run_data = calc_resp.json()
    run_id = run_data["id"]
    assert run_data["status"] == "Calculated"
    assert len(run_data["employee_results"]) >= 1

    # Verify calculation trace tree
    first_emp = run_data["employee_results"][0]
    assert "calculation_trace" in first_emp
    assert "steps" in first_emp["calculation_trace"]

    print("\n--- STAGE 8: MULTI-TIER APPROVAL WORKFLOW ---")
    # Manager Approval
    appr1 = client.post(f"/api/v1/payslips/run/{run_id}/approve", json={"action": "APPROVE", "remarks": "Manager Audit Passed"}, headers=auth_headers)
    assert appr1.status_code == 200

    # Finance Approval
    appr2 = client.post(f"/api/v1/payslips/run/{run_id}/approve", json={"action": "APPROVE", "remarks": "Finance Audit Passed"}, headers=auth_headers)
    assert appr2.status_code == 200

    # Final Lock
    appr3 = client.post(f"/api/v1/payslips/run/{run_id}/approve", json={"action": "APPROVE", "remarks": "Final Lock Executed"}, headers=auth_headers)
    assert appr3.status_code == 200

    print("\n--- STAGE 9: REPORTLAB PDF PAYSLIPS & BULK ZIP ---")
    pdf_resp = client.get(f"/api/v1/payslips/employee/1/period/{period_id}/pdf", headers=auth_headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp.content.startswith(b"%PDF-1.")

    zip_resp = client.get(f"/api/v1/payslips/run/{run_id}/bulk-zip", headers=auth_headers)
    assert zip_resp.status_code == 200
    assert zip_resp.content.startswith(b"PK\x03\x04")

    print("\n--- STAGE 10: BANK ADAPTERS & GL DOUBLE-ENTRY BALANCE ---")
    hdfc_resp = client.post("/api/v1/payments/generate-bank-file", json={"payroll_run_id": run_id, "bank_format": "HDFC_CMS"}, headers=auth_headers)
    assert hdfc_resp.status_code == 200
    assert b"HDFC_CMS_HEADER" in hdfc_resp.content

    gl_resp = client.get(f"/api/v1/payments/journal-entries/{run_id}", headers=auth_headers)
    assert gl_resp.status_code == 200
    gl_data = gl_resp.json()
    assert gl_data["is_balanced"] is True
    assert gl_data["total_debit"] == gl_data["total_credit"]

    print("\n--- STAGE 11: MASTER REGISTER & INDIA PF ECR RETURN ---")
    reg_resp = client.get(f"/api/v1/reports/payroll-register?period_id={period_id}", headers=auth_headers)
    assert reg_resp.status_code == 200

    pf_resp = client.get(f"/api/v1/reports/pf-ecr/{period_id}", headers=auth_headers)
    assert pf_resp.status_code == 200
    assert b"#~#" in pf_resp.content

    print("\n--- STAGE 12: ESS / MSS SELF-SERVICE PORTAL ---")
    ess_resp = client.get("/api/v1/self-service/ess/me", headers=auth_headers)
    assert ess_resp.status_code == 200

    mss_resp = client.get("/api/v1/self-service/mss/team", headers=auth_headers)
    assert mss_resp.status_code == 200

    print("\n--- STAGE 13: CRYPTOGRAPHIC SHA-256 AUDIT CHAIN INTEGRITY ---")
    audit_verify = client.get("/api/v1/audit/verify-integrity", headers=auth_headers)
    assert audit_verify.status_code == 200
    assert audit_verify.json()["is_intact"] is True

    print("\n✓ MASTER E2E PAYROLL SYSTEM LIFECYCLE PASSED SUCCESSFULLY!")
