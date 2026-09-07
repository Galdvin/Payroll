# Testing & Quality Assurance Guide - Enterprise Payroll Management System

## Automated Pytest Suite Overview
The project includes a comprehensive suite of unit, integration, performance, and E2E automated test scripts located in `tests/payroll/`.

---

## Test Execution Commands

### Run Full Test Suite
```bash
python -m pytest tests/ -v
```

### Run Master E2E System Lifecycle Test
```bash
python -m pytest tests/payroll/test_master_e2e_payroll_system.py -v
```

### Run High Volume Benchmark Test (10,000 Staff)
```bash
python -m pytest tests/payroll/test_payroll_performance_api.py -v
```

---

## Pytest Modules Directory

| Test File | Description |
| :--- | :--- |
| `test_master_e2e_payroll_system.py` | Complete 12-phase enterprise lifecycle E2E test |
| `test_payroll_calculation_engine.py` | Core calculation pipeline & proration logic |
| `test_tax_statutory_engine_api.py` | India PF/ESI/PT and TDS tax slab evaluation |
| `test_financial_extras_api.py` | Loans, advances, bonuses, reimbursements |
| `test_payslip_approval_api.py` | 4-Stage approval workflow & PDF/ZIP streams |
| `test_bank_payments_api.py` | HDFC/ICICI bank adapters & double-entry GL balance |
| `test_reports_api.py` | Master register & India PF ECR return text file |
| `test_self_service_api.py` | ESS & MSS self service profile access |
| `test_audit_security_api.py` | Cryptographic SHA-256 chain integrity verification |
| `test_payroll_performance_api.py` | High volume 10,000 employee performance benchmark |
