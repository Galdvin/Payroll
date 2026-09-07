# Payroll Rule Engine & Calculation Specifications

## 1. Engine Philosophy
The Payroll Calculation Engine is designed as a standalone, deterministic calculation pipeline.
It decouples **Salary Component Evaluation**, **Proration Logic**, **Tax Engine Rules**, and **Statutory Calculations**.

## 2. Calculation Pipeline Lifecycle
1. **Input Phase**: Gather Employee, Attendance (Days Present/Absent), Salary Structure, Loans, Advances, Overtime, and Active Tax/Statutory Rule version.
2. **Proration Phase**: Compute Prorated Basic and fixed allowances based on Working Days vs Payable Days.
3. **Earnings Phase**: Calculate Gross Salary = Prorated Basic + Allowances + Overtime + Bonuses + Reimbursements.
4. **Tax & Statutory Phase**: Execute country specific rule engine (India PF/ESI/PT/TDS, UAE Pension/Gratuity) returning exact employee & employer shares.
5. **Deductions Phase**: Compute Total Deductions = Employee Statutory + Tax + Loans + Advances + Unpaid Leave.
6. **Net & Employer Cost**: Net Salary = Gross - Deductions; Employer Cost = Gross + Employer Contributions.
7. **Trace Generation**: Output detailed calculation trace tree stored in `payroll_employees.calculation_trace`.
