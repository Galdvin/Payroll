import pytest


def test_high_volume_payroll_benchmark(client, admin_headers):
    # Execute 10,000 employee calculation benchmark
    resp = client.get("/api/v1/payroll/benchmark?count=10000", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "BENCHMARK_SUCCESS"
    assert data["total_employees_processed"] == 10000
    assert data["payroll_history_months"] == 12
    assert data["total_monthly_runs_evaluated"] == 120000
    assert data["total_attendance_days_simulated"] == 3650000
    assert data["departments_count"] == 6
    assert data["salary_structures_count"] == 5
    assert data["duration_seconds"] < 5.0  # Sub-5 second benchmark requirement
    assert data["throughput_evaluations_per_sec"] > 5000.0  # High-volume throughput
    assert data["total_gross_disbursed_ytd"] > 0


def test_payroll_benchmark_scaling_tiers(client, admin_headers):
    """Test performance scaling across 1, 100, 1,000, 5,000, and 10,000 employee tiers."""
    for count in [1, 100, 1000, 5000, 10000]:
        resp = client.get(f"/api/v1/payroll/benchmark?count={count}", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "BENCHMARK_SUCCESS"
        assert data["total_employees_processed"] == count
        assert data["duration_seconds"] < 5.0

