import pytest


def test_high_volume_payroll_benchmark(client, admin_headers):
    # Execute 10,000 employee calculation benchmark
    resp = client.get("/api/v1/payroll/benchmark?count=10000", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "BENCHMARK_SUCCESS"
    assert data["total_employees_processed"] == 10000
    assert data["duration_seconds"] < 5.0  # Sub-5 second benchmark requirement
    assert data["throughput_per_sec"] > 1000.0  # At least 1000 calculations/sec
    assert data["total_gross_disbursed"] > 0
