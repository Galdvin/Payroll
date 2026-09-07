import pytest


def test_ess_and_mss_self_service_endpoints(client, admin_headers):
    # 1. Fetch logged-in ESS profile
    profile_resp = client.get("/api/v1/self-service/ess/me", headers=admin_headers)
    assert profile_resp.status_code == 200
    prof = profile_resp.json()
    assert "employee_code" in prof
    assert "leave_balances" in prof

    # 2. Fetch ESS personal payslips list
    slips_resp = client.get("/api/v1/self-service/ess/my-payslips", headers=admin_headers)
    assert slips_resp.status_code == 200
    assert isinstance(slips_resp.json(), list)

    # 3. Fetch MSS direct report team members
    team_resp = client.get("/api/v1/self-service/mss/team", headers=admin_headers)
    assert team_resp.status_code == 200
    team = team_resp.json()
    assert isinstance(team, list)

    # 4. Fetch MSS team pending leaves approval queue
    leaves_resp = client.get("/api/v1/self-service/mss/team-leaves", headers=admin_headers)
    assert leaves_resp.status_code == 200
    assert isinstance(leaves_resp.json(), list)
