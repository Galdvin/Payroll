from datetime import date
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.models.payroll_run import PayrollRun, PayrollEmployee
from app.models.bank_payment import JournalEntry
from app.schemas.bank_payment import JournalEntrySummary, JournalEntryResponse
from app.core.exceptions import PayrollException


class AccountingJournalService:

    @staticmethod
    def generate_journal_entries(db: Session, payroll_run_id: int) -> JournalEntrySummary:
        """Generates balanced double-entry General Ledger (GL) records for a payroll run."""
        run = db.query(PayrollRun).filter(PayrollRun.id == payroll_run_id).first()
        if not run:
            raise PayrollException("RUN_NOT_FOUND", f"Payroll run {payroll_run_id} not found")

        # Existing check
        existing = db.query(JournalEntry).filter(JournalEntry.payroll_run_id == payroll_run_id).all()
        if existing:
            total_deb = sum(e.debit_amount for e in existing)
            total_cred = sum(e.credit_amount for e in existing)
            return JournalEntrySummary(
                entries=[JournalEntryResponse.model_validate(e) for e in existing],
                total_debit=round(total_deb, 2),
                total_credit=round(total_cred, 2),
                is_balanced=abs(total_deb - total_cred) < 0.01
            )

        employees: List[PayrollEmployee] = run.employee_results
        entry_date = date.today()
        period_name = run.payroll_period.name if run.payroll_period else "Pay Period"

        # Aggregation buckets
        tot_gross = 0.0
        tot_employer_pf = 0.0
        tot_employer_esi = 0.0

        tot_net = round(run.total_net, 2)
        tot_pf = 0.0
        tot_esi = 0.0
        tot_tds = 0.0
        tot_pt = 0.0
        tot_loan_emi = 0.0

        for emp in employees:
            tot_gross += emp.gross_salary
            tot_employer_pf += emp.employer_statutory  # Approximate split

            for d in emp.deductions:
                c = d.component_code.upper()
                if "PF" in c:
                    tot_pf += d.amount
                elif "ESI" in c:
                    tot_esi += d.amount
                elif "TDS" in c or "TAX" in c:
                    tot_tds += d.amount
                elif "PT" in c:
                    tot_pt += d.amount
                elif "LOAN" in c or "EMI" in c:
                    tot_loan_emi += d.amount

        # Round totals
        tot_gross = round(tot_gross, 2)
        tot_employer_pf = round(tot_employer_pf, 2)

        # Build Debit & Credit entries
        raw_entries = []

        # 1. DEBITS
        raw_entries.append(JournalEntry(
            payroll_run_id=payroll_run_id,
            entry_date=entry_date,
            account_code="50100",
            account_name="Salaries & Wages Gross Expense",
            debit_amount=tot_gross,
            credit_amount=0.0,
            narration=f"Gross salary expense for {period_name}"
        ))

        if tot_employer_pf > 0:
            raw_entries.append(JournalEntry(
                payroll_run_id=payroll_run_id,
                entry_date=entry_date,
                account_code="50200",
                account_name="Employer Statutory PF Expense",
                debit_amount=tot_employer_pf,
                credit_amount=0.0,
                narration=f"Employer PF matching expense for {period_name}"
            ))

        # 2. CREDITS
        raw_entries.append(JournalEntry(
            payroll_run_id=payroll_run_id,
            entry_date=entry_date,
            account_code="20100",
            account_name="Net Salary Payable Account",
            debit_amount=0.0,
            credit_amount=tot_net,
            narration=f"Net salary payable to employees for {period_name}"
        ))

        tot_deductions_accounted = tot_pf + tot_esi + tot_tds + tot_pt + tot_loan_emi
        remaining_deductions = round(run.total_deductions - tot_deductions_accounted, 2)

        if tot_pf > 0:
            raw_entries.append(JournalEntry(
                payroll_run_id=payroll_run_id,
                entry_date=entry_date,
                account_code="20200",
                account_name="Employee Provident Fund (PF) Liability",
                debit_amount=0.0,
                credit_amount=round(tot_pf, 2),
                narration="PF deduction liability"
            ))

        if tot_employer_pf > 0:
            raw_entries.append(JournalEntry(
                payroll_run_id=payroll_run_id,
                entry_date=entry_date,
                account_code="20210",
                account_name="Employer Provident Fund (PF) Liability",
                debit_amount=0.0,
                credit_amount=tot_employer_pf,
                narration="Employer PF matching liability"
            ))

        if tot_tds > 0:
            raw_entries.append(JournalEntry(
                payroll_run_id=payroll_run_id,
                entry_date=entry_date,
                account_code="20400",
                account_name="TDS Income Tax Payable",
                debit_amount=0.0,
                credit_amount=round(tot_tds, 2),
                narration="Income tax TDS withholding liability"
            ))

        if tot_pt > 0:
            raw_entries.append(JournalEntry(
                payroll_run_id=payroll_run_id,
                entry_date=entry_date,
                account_code="20500",
                account_name="Professional Tax (PT) Payable",
                debit_amount=0.0,
                credit_amount=round(tot_pt, 2),
                narration="State professional tax withholding"
            ))

        if tot_loan_emi > 0:
            raw_entries.append(JournalEntry(
                payroll_run_id=payroll_run_id,
                entry_date=entry_date,
                account_code="10300",
                account_name="Employee Loan Principal Asset",
                debit_amount=0.0,
                credit_amount=round(tot_loan_emi, 2),
                narration="Loan EMI recovery principal reduction"
            ))

        if remaining_deductions > 0:
            raw_entries.append(JournalEntry(
                payroll_run_id=payroll_run_id,
                entry_date=entry_date,
                account_code="20900",
                account_name="Other Payroll Deductions Clearing",
                debit_amount=0.0,
                credit_amount=remaining_deductions,
                narration="Miscellaneous payroll deductions"
            ))

        # Save to DB
        db.add_all(raw_entries)
        db.commit()

        total_deb = sum(e.debit_amount for e in raw_entries)
        total_cred = sum(e.credit_amount for e in raw_entries)

        return JournalEntrySummary(
            entries=[JournalEntryResponse.model_validate(e) for e in raw_entries],
            total_debit=round(total_deb, 2),
            total_credit=round(total_cred, 2),
            is_balanced=abs(total_deb - total_cred) < 0.01
        )

    @staticmethod
    def export_gl_csv(db: Session, payroll_run_id: int) -> bytes:
        """Exports GL journal entries as a formatted CSV file for SAP/Tally/QuickBooks."""
        summary = AccountingJournalService.generate_journal_entries(db, payroll_run_id)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Entry Date", "Account Code", "Account Name", "Debit Amount (INR)", "Credit Amount (INR)", "Narration"])
        for e in summary.entries:
            writer.writerow([e.entry_date, e.account_code, e.account_name, f"{e.debit_amount:.2f}", f"{e.credit_amount:.2f}", e.narration or ""])
        writer.writerow([])
        writer.writerow(["TOTALS", "", "", f"{summary.total_debit:.2f}", f"{summary.total_credit:.2f}", "BALANCED" if summary.is_balanced else "UNBALANCED"])
        return output.getvalue().encode('utf-8')
