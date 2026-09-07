def test_create_organization_and_company_flow(client, admin_headers):
    # 1. Create Organization
    org_payload = {
        "name": "Acme Global Enterprise",
        "code": "ACME_GLOBAL",
        "tax_identifier": "PAN1234567",
        "currency": "INR",
        "country": "India"
    }
    org_resp = client.post("/api/v1/organization", json=org_payload, headers=admin_headers)
    assert org_resp.status_code == 201
    org_data = org_resp.json()
    assert org_data["code"] == "ACME_GLOBAL"
    org_id = org_data["id"]

    # 2. Create Company under Organization
    comp_payload = {
        "organization_id": org_id,
        "name": "Acme Technologies Pvt Ltd",
        "code": "ACME_TECH",
        "registration_number": "REG-889900"
    }
    comp_resp = client.post("/api/v1/organization/companies", json=comp_payload, headers=admin_headers)
    assert comp_resp.status_code == 201
    comp_data = comp_resp.json()
    assert comp_data["name"] == "Acme Technologies Pvt Ltd"
    comp_id = comp_data["id"]

    # 3. Create Department under Company
    dept_payload = {
        "company_id": comp_id,
        "name": "Engineering & Technology",
        "code": "ENG"
    }
    dept_resp = client.post("/api/v1/organization/departments", json=dept_payload, headers=admin_headers)
    assert dept_resp.status_code == 201
    assert dept_resp.json()["name"] == "Engineering & Technology"
