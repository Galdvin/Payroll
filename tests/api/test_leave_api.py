def test_leave_apply_and_approval_workflow(client, admin_headers, employee_user):
    # 1. Fetch Leave Types
    types_resp = client.get("/api/v1/leaves/types", headers=admin_headers)
    assert types_resp.status_code == 200
    leave_types = types_resp.json()
    assert len(leave_types) >= 1
    annual_leave_id = leave_types[0]["id"]

    # 2. Apply for Leave
    apply_payload = {
        "employee_id": employee_user.id,
        "leave_type_id": annual_leave_id,
        "start_date": "2024-10-01",
        "end_date": "2024-10-03",
        "reason": "Personal vacation"
    }
    apply_resp = client.post("/api/v1/leaves/requests", json=apply_payload, headers=admin_headers)
    assert apply_resp.status_code == 201
    req_data = apply_resp.json()
    assert req_data["status"] == "Pending"
    assert req_data["total_days"] == 3.0
    request_id = req_data["id"]

    # 3. Approve Leave Request as Manager
    approve_payload = {
        "status": "Approved",
        "approval_comments": "Approved. Have a great vacation!"
    }
    app_resp = client.post(f"/api/v1/leaves/requests/{request_id}/approve", json=approve_payload, headers=admin_headers)
    assert app_resp.status_code == 200
    assert app_resp.json()["status"] == "Approved"
