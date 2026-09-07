def test_tax_and_statutory_rule_evaluation(client, admin_headers):
    # 1. Fetch Statutory Rules Catalog
    stat_resp = client.get("/api/v1/tax-statutory/statutory-rules?country=India", headers=admin_headers)
    assert stat_resp.status_code == 200
    stat_rules = stat_resp.json()
    assert len(stat_rules) >= 3 # PF, ESI, PT

    # 2. Fetch Versioned Tax Rules & Slabs
    tax_resp = client.get("/api/v1/tax-statutory/tax-rules?country=India", headers=admin_headers)
    assert tax_resp.status_code == 200
    tax_rules = tax_resp.json()
    assert len(tax_rules) >= 1
    assert tax_rules[0]["regime_name"] == "New Regime"
    assert tax_rules[0]["standard_deduction"] == 75000.0

    # 3. Evaluate TDS Tax Engine for 100,000 INR / month gross (12 Lakhs annual)
    tds_resp = client.post("/api/v1/tax-statutory/evaluate-tds", json={"gross_monthly_salary": 100000.0, "regime_name": "New Regime"}, headers=admin_headers)
    assert tds_resp.status_code == 200
    tds_data = tds_resp.json()
    assert tds_data["annual_gross"] == 1200000.0
    assert tds_data["standard_deduction"] == 75000.0
    assert tds_data["taxable_annual"] == 1125000.0
    assert tds_data["monthly_tds"] > 0
