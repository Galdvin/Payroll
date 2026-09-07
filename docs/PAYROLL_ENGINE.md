# Payroll Calculation Engine & Statutory Mathematics

## Overview
The Payroll Engine operates as a deterministic, stateless calculation pipeline that evaluates attendance proration, dynamic CTC components, statutory contributions, income tax TDS withholding, loan EMIs, and variable bonuses.

---

## Key Calculation Formulas

### 1. Attendance Proration Factor
\[
ProrationRatio = \frac{PayableDays}{TotalDaysInMonth}
\]
Each component marked `is_prorated = True` is multiplied by \(ProrationRatio\).

---

### 2. Statutory Contributions (India Jurisdiction)

#### Employee & Employer Provident Fund (PF)
- **Wage Ceiling**: Standard PF wage cap is ₹15,000 / month.
- **EPF Wage**: \(EPFWage = \min(Basic, 15000)\)
- **Employee PF Contribution (12%)**:
  \[
  PF_{Employee} = \min(Basic \cdot 0.12, 1800)
  \]
- **Employer Pension Scheme (EPS 8.33%) & EPF Matching (3.67%)**:
  \[
  EPS_{Employer} = \min(Basic, 15000) \cdot 0.0833
  \]
  \[
  EPF_{Employer} = PF_{Employee} - EPS_{Employer}
  \]

#### Employee State Insurance (ESI)
- **Applicability Threshold**: Gross salary \(\le\) ₹21,000 / month.
- **Employee ESI (0.75%)**: \(ESI_{Employee} = Gross \cdot 0.0075\)
- **Employer ESI (3.25%)**: \(ESI_{Employer} = Gross \cdot 0.0325\)

#### Professional Tax (PT)
- **State Slabs** (e.g. Maharashtra / Karnataka / Telangana):
  - Gross \(\le\) ₹15,000: ₹0
  - Gross \(>\) ₹15,000: ₹200 / month (₹300 in February)

---

### 3. Income Tax TDS Engine (New Tax Regime FY 2024-2025)
- **Standard Deduction**: ₹75,000 / year.
- **Annual Taxable Income**:
  \[
  Taxable = (Gross \cdot 12) - StandardDeduction
  \]
- **Progressive Tax Slabs**:
  - Up to ₹3,00,000: 0%
  - ₹3,00,001 to ₹7,00,000: 5%
  - ₹7,00,001 to ₹10,00,000: 10%
  - ₹10,00,001 to ₹12,00,000: 15%
  - ₹12,00,001 to ₹15,00,000: 20%
  - Above ₹15,00,000: 30%
- **Rebate u/s 87A**: Full tax rebate if taxable income \(\le\) ₹7,00,000.
- **Health & Education Cess**: 4% applied on calculated tax.
- **Monthly TDS Withholding**:
  \[
  TDS_{Monthly} = \frac{TotalAnnualTax \cdot 1.04}{12}
  \]

---

### 4. Loan Reducing-Balance EMI Formula
\[
EMI = \frac{P \cdot r \cdot (1+r)^n}{(1+r)^n - 1}
\]
Where:
- \(P\) = Principal Loan Amount
- \(r\) = Monthly Interest Rate (\(\frac{AnnualRate}{12 \cdot 100}\))
- \(n\) = Tenure in Months

---

## Calculation Trace Tree Structure
Every calculated row produces a JSONB trace tree stored in `payroll_employees.calculation_trace`:
```json
{
  "step_1_proration": {
    "payable_days": 30.0,
    "total_days": 30.0,
    "ratio": 1.0,
    "explanation": "Full month worked"
  },
  "step_2_earnings_breakdown": {
    "basic": { "full": 50000.0, "prorated": 50000.0 },
    "hra": { "full": 20000.0, "prorated": 20000.0 }
  },
  "step_3_deductions_breakdown": {
    "employee_pf": { "amount": 1800.0 },
    "tds_tax": { "amount": 4333.33 }
  },
  "step_5_final_takehome": {
    "gross": 100000.0,
    "deductions": 6333.33,
    "net": 93666.67
  }
}
```
