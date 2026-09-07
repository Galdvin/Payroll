# API Endpoints Specification - Enterprise Payroll Management System

## Base URL
`/api/v1`

---

## Authentication & RBAC
- `POST /auth/login`: Form-encoded OAuth2 login returning Bearer JWT & Refresh token.
- `POST /auth/refresh`: Refreshes expired access token.
- `GET /auth/me`: Returns current user profile & permissions list.

---

## Employee & Organization Management
- `GET /organization/companies`: List corporate entities.
- `GET /employees/`: List employee master directory.
- `GET /employees/{id}`: Detailed employee profile with CTC & document repository.

---

## Attendance & Leave
- `GET /attendance/summary`: Monthly attendance summary & payable days.
- `GET /leaves/balances`: Employee leave quota balances.
- `POST /leaves/requests`: Submit leave request.

---

## Salary & Tax Statutory Engine
- `POST /salary/evaluate-ctc`: Evaluates CTC breakdown into Basic, HRA, Transport, Special Allowance.
- `GET /tax-statutory/statutory-rules`: Catalog of statutory rules (India PF, ESI, PT, UAE Pension).
- `POST /tax-statutory/evaluate-tds`: Evaluates monthly income tax TDS withholding.

---

## Payroll Batch Execution & Tracing
- `GET /payroll/periods`: List payroll periods.
- `POST /payroll/calculate`: Executes batch calculation pipeline for a pay period.
- `GET /payroll/runs/{id}`: Fetch payroll run totals.
- `GET /payroll/runs/{id}/trace/{employee_id}`: Fetch explainable calculation trace tree.
- `GET /payroll/benchmark`: High-volume 10,000 employee benchmark execution.

---

## Payslips & Multi-Tier Approval Workflow
- `POST /payslips/run/{id}/approve`: Advances approval stage (`Calculated` -> `Manager Approved` -> `Finance Approved` -> `Locked`).
- `GET /payslips/employee/{employee_id}/period/{period_id}/pdf`: Streams ReportLab PDF payslip.
- `GET /payslips/run/{id}/bulk-zip`: Streams bulk ZIP archive of all employee payslips.

---

## Bank Payments & Accounting Journal Entries
- `POST /payments/generate-bank-file`: Generates corporate bank file payload (HDFC_CMS, ICICI_CIB, SBI_CMP, ISO20022).
- `GET /payments/journal-entries/{run_id}`: Returns double-entry GL journal entries (\(\sum Debit = \sum Credit\)).
- `GET /payments/journal-entries/{run_id}/export`: Exports GL entries CSV for SAP/Tally.

---

## Reports & Analytics
- `GET /reports/payroll-register`: Master payroll register dataset.
- `GET /reports/pf-ecr/{period_id}`: Streams India PF ECR return text file (`#~#` formatted).
- `GET /reports/cost-center`: Department & Cost Center summary.
- `GET /reports/executive-analytics`: Executive level financial KPIs.

---

## ESS & MSS Self-Service
- `GET /self-service/ess/me`: Personal ESS profile, YTD earnings, leave balances.
- `GET /self-service/ess/my-payslips`: Personal historical payslip list.
- `GET /self-service/mss/team`: Direct report team members.
- `GET /self-service/mss/team-leaves`: Manager pending leave approval queue.

---

## Cryptographic Security & Audit
- `GET /audit/logs`: Filterable audit trail log stream.
- `GET /audit/verify-integrity`: SHA-256 chain verification status.
