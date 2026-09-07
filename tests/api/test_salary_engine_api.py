def test_salary_components_and_ctc_breakdown_engine(client, admin_headers, employee_user):
    # 1. Fetch Salary Components Catalog
    comp_resp = client.get("/api/v1/salary/components", headers=admin_headers)
    assert comp_resp.status_code == 200
    components = comp_resp.json()
    assert len(components) >= 5 # BASIC, HRA, TRANSPORT, MEDICAL, SPECIAL_ALLOWANCE

    # 2. Assign Annual CTC of 600,000 INR (50,000 / month)
    assign_payload = {
        "employee_id": employee_user.id,
        "total_ctc": 600000.0,
        "effective_date": "2024-01-01",
        "currency": "INR"
    }
    assign_resp = client.post("/api/v1/salary/assign", json=assign_payload, headers=admin_headers)
    assert assign_resp.status_code == 200
    sal_data = assign_resp.json()
    assert sal_data["total_ctc"] == 600000.0
    assert sal_data["gross_salary"] == 50000.0  # Monthly Gross
    assert sal_data["net_salary"] == 48000.0    # Gross (50,000) - PF (1800) - PT (200)

    # 3. Perform Salary Revision to 720,000 INR (+20% increment)
    revision_payload = {
        "employee_id": employee_user.id,
        "new_ctc": 720000.0,
        "effective_date": "2024-10-01",
        "revision_reason": "Annual Performance Appraisal"
    }
    rev_resp = client.post("/api/v1/salary/revisions", json=revision_payload, headers=admin_headers)
    assert rev_resp.status_code == 201
    rev_data = rev_resp.json()
    assert rev_data["old_ctc"] == 600000.0
    assert rev_data["new_ctc"] == 720000.0
    assert rev_data["increment_percentage"] == 20.0
