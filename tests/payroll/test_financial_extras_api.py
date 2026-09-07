import pytest


def test_loan_advance_bonus_reimbursement_flow(client, admin_headers):
    # 1. Request a Loan
    loan_payload = {
        "employee_id": 1,
        "principal_amount": 120000.0,
        "interest_rate_annual": 12.0,
        "tenure_months": 12,
        "disbursement_date": "2026-04-01",
        "reason": "Home Renovation",
    }
    loan_resp = client.post("/api/v1/financial-extras/loans", json=loan_payload, headers=admin_headers)
    assert loan_resp.status_code == 201
    loan_data = loan_resp.json()
    assert loan_data["status"] == "PENDING"
    loan_id = loan_data["id"]
    assert loan_data["monthly_emi"] > 10000.0 # Standard 120k loan @ 12% for 12 mos

    # 2. Approve Loan
    approve_loan_resp = client.post(f"/api/v1/financial-extras/loans/{loan_id}/approve", headers=admin_headers)
    assert approve_loan_resp.status_code == 200
    assert approve_loan_resp.json()["status"] == "APPROVED"

    # 3. List Loans
    list_loans_resp = client.get("/api/v1/financial-extras/loans?employee_id=1", headers=admin_headers)
    assert list_loans_resp.status_code == 200
    assert len(list_loans_resp.json()) >= 1

    # 4. Request Advance
    adv_payload = {
        "employee_id": 1,
        "amount": 15000.0,
        "request_date": "2026-04-05",
        "recovery_payroll_period_id": 1,
        "reason": "Emergency travel expense",
    }
    adv_resp = client.post("/api/v1/financial-extras/advances", json=adv_payload, headers=admin_headers)
    assert adv_resp.status_code == 201
    assert adv_resp.json()["amount"] == 15000.0

    # 5. Create Bonus / Incentive
    bonus_payload = {
        "employee_id": 1,
        "payroll_period_id": 1,
        "bonus_type": "PERFORMANCE",
        "amount": 25000.0,
        "is_taxable": True,
        "remarks": "Q1 Excellence Award",
    }
    bonus_resp = client.post("/api/v1/financial-extras/bonuses", json=bonus_payload, headers=admin_headers)
    assert bonus_resp.status_code == 201
    assert bonus_resp.json()["amount"] == 25000.0

    # 6. Create Reimbursement
    reimb_payload = {
        "employee_id": 1,
        "payroll_period_id": 1,
        "claim_date": "2026-04-10",
        "items": [
            {
                "expense_category": "TRAVEL",
                "amount": 4500.0,
                "description": "Flight ticket to client office",
                "receipt_url": "https://storage.payroll.com/receipts/r1.pdf",
            },
            {
                "expense_category": "MEALS",
                "amount": 1200.0,
                "description": "Client dinner meeting",
                "receipt_url": "https://storage.payroll.com/receipts/r2.pdf",
            },
        ],
    }
    reimb_resp = client.post("/api/v1/financial-extras/reimbursements", json=reimb_payload, headers=admin_headers)
    assert reimb_resp.status_code == 201
    reimb_data = reimb_resp.json()
    assert reimb_data["total_amount"] == 5700.0
    assert reimb_data["status"] == "SUBMITTED"
    reimb_id = reimb_data["id"]

    # 7. Approve Reimbursement
    approve_reimb_resp = client.post(
        f"/api/v1/financial-extras/reimbursements/{reimb_id}/approve",
        json={"status": "APPROVED", "remarks": "All receipts verified"},
        headers=admin_headers,
    )
    assert approve_reimb_resp.status_code == 200
    assert approve_reimb_resp.json()["status"] == "APPROVED"
    assert approve_reimb_resp.json()["approved_amount"] == 5700.0
