# Database Schema Reference - Enterprise Payroll Management System

## Overview
The database schema consists of 25+ normalized tables managed via SQLAlchemy 2.0 and Alembic migrations.

---

## Core Entities & Relationships

### 1. Multi-Tenant Organization Master
- `organizations`: Root enterprise entity.
- `companies`: Multi-tenant companies linked to an organization.
- `branches`: Physical locations/branches.
- `departments`: Hierarchical department structure.
- `designations`: Corporate job titles.

### 2. Employee Master & History
- `employees`: Core employee master record (PAN, Bank A/C, PF UAN, ESI, Joining Date).
- `employee_history`: Audit trail for salary revisions, department transfers, and designation changes.

### 3. Attendance, Shifts & Leaves
- `shifts`: Work shifts with flexible/fixed hours.
- `attendance`: Daily punch-in/out records with calculated overtime hours.
- `leave_types`, `leave_policies`, `leave_balances`, `leave_requests`: Complete leave quota & approval engine.

### 4. Configurable Salary Structure Engine
- `salary_components`: Component catalog (`BASIC`, `HRA`, `TRANSPORT`, `SPECIAL_ALLOWANCE`, `IN_PF`, `IN_ESI`, `IN_TDS`, `IN_PT`).
- `salary_structures`: Base structure blueprints.
- `employee_salaries`: Employee assigned CTC breakdowns.

### 5. Core Payroll Batch Execution & Calculation Trace
- `payroll_periods`: Pay period definition (e.g. `2024-09`).
- `payroll_runs`: Batch run status (`Draft` -> `Calculated` -> `Manager Approved` -> `Finance Approved` -> `Locked`).
- `payroll_employees`: Calculated payroll line per employee containing **`calculation_trace` JSONB tree**.
- `payroll_earnings`: Itemized earning components per employee.
- `payroll_deductions`: Itemized deduction components per employee.

### 6. Statutory & Tax Rules
- `statutory_rules`: Country-specific rules (India PF 12%/₹1,800 cap, ESI 0.75%/3.25%, PT, UAE Pension).
- `tax_rules` & `tax_slabs`: Versioned progressive income tax slabs (India FY 2024-2025 New Regime).

### 7. Financial Extras & Variable Pay
- `loans` & `loan_transactions`: Loan principal, interest rate, tenure, and reducing-balance EMI amortization.
- `advances`: Emergency salary advances with recovery period tracking.
- `bonuses`: Festive, performance, retention, and commission variable bonuses.
- `reimbursements` & `reimbursement_items`: Multi-item expense claims with manager approval.

### 8. Bank Payments & Accounting Journal Entries
- `bank_payment_batches`: Batch disbursement files (HDFC CMS, ICICI CIB, SBI CMP, ISO20022) with SHA-256 checksums.
- `journal_entries`: Double-entry General Ledger records (\(\sum Debit = \sum Credit\)).

### 9. Cryptographic Audit Log
- `audit_logs`: Immutable action audit log with SHA-256 hash chaining (`prev_hash` & `hash_checksum`).
