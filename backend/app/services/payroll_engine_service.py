from datetime import date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.core.exceptions import PayrollException, ResourceNotFoundException
from app.models.payroll_run import (
    PayrollPeriod,
    PayrollRun,
    PayrollEmployee,
    PayrollEarning,
    PayrollDeduction,
)
from app.models.employee import Employee
from app.models.salary import EmployeeSalary
from app.models.attendance import AttendanceSummary
from app.models.financial_extras import Loan, Advance, BonusIncentive, Reimbursement
from app.services.statutory_engine_service import StatutoryEngineService
from app.schemas.payroll import PayrollPeriodCreate


class PayrollEngineService:

    @staticmethod
    def get_periods(db: Session, company_id: int = 1) -> List[PayrollPeriod]:
        periods = db.query(PayrollPeriod).filter(PayrollPeriod.company_id == company_id).all()
        if not periods:
            default_p = PayrollPeriod(
                company_id=company_id,
                name="September 2024 Monthly Payroll",
                year_month="2024-09",
                start_date=date(2024, 9, 1),
                end_date=date(2024, 9, 30),
                cutoff_date=date(2024, 9, 25),
                status="Open",
            )
            db.add(default_p)
            db.commit()
            db.refresh(default_p)
            periods = [default_p]
        return periods

    @staticmethod
    def create_period(db: Session, data: PayrollPeriodCreate) -> PayrollPeriod:
        existing = db.query(PayrollPeriod).filter(PayrollPeriod.year_month == data.year_month).first()
        if existing:
            raise PayrollException(f"Payroll period for '{data.year_month}' already exists.", error_code="PERIOD_EXISTS")
        period = PayrollPeriod(**data.model_dump())
        db.add(period)
        db.commit()
        db.refresh(period)
        return period

    @staticmethod
    def calculate_payroll_for_period(db: Session, user_id: int, period_id: int) -> PayrollRun:
        period = db.query(PayrollPeriod).filter(PayrollPeriod.id == period_id).first()
        if not period:
            raise ResourceNotFoundException("PayrollPeriod", period_id)

        if period.status == "Locked":
            raise PayrollException("Payroll period is locked and cannot be recalculated.", error_code="PAYROLL_ALREADY_LOCKED")

        # Enforce singleton constraint: Only ONE payroll run calculation per period
        existing_runs = db.query(PayrollRun).filter(PayrollRun.payroll_period_id == period_id).all()
        for existing_run in existing_runs:
            if existing_run.status == "Locked":
                raise PayrollException("Payroll run is LOCKED. Modifications prohibited.", error_code="PAYROLL_ALREADY_LOCKED")
            db.delete(existing_run)
        db.flush()

        employees = db.query(Employee).filter(Employee.is_active == True).all()

        total_gross = 0.0
        total_deductions = 0.0
        total_net = 0.0
        total_employer_cost = 0.0

        run = PayrollRun(
            payroll_period_id=period_id,
            total_employees=len(employees),
            status="Calculated",
            executed_by_user_id=user_id,
        )
        db.add(run)
        db.flush()

        for emp in employees:
            sal = db.query(EmployeeSalary).filter(EmployeeSalary.employee_id == emp.id).first()
            if not sal:
                full_basic = 25000.0
                full_hra = 10000.0
                full_transport = 3000.0
                full_medical = 2000.0
                full_special = 10000.0
            else:
                comp_map = {item.component.code: float(item.monthly_amount) for item in sal.assigned_components}
                full_basic = comp_map.get("BASIC", float(sal.gross_salary) * 0.50)
                full_hra = comp_map.get("HRA", full_basic * 0.40)
                full_transport = comp_map.get("TRANSPORT", 3000.0)
                full_medical = comp_map.get("MEDICAL", 2000.0)
                full_special = comp_map.get("SPECIAL_ALLOWANCE", max(0.0, float(sal.gross_salary) - (full_basic + full_hra + full_transport + full_medical)))

            att = db.query(AttendanceSummary).filter(
                AttendanceSummary.employee_id == emp.id,
                AttendanceSummary.year_month == period.year_month
            ).first()

            total_days = (period.end_date - period.start_date).days + 1
            if att:
                payable_days = float(att.payable_days)
                overtime_hrs = float(att.overtime_hours)
            else:
                payable_days = float(total_days)
                overtime_hrs = 0.0

                # Check for new joiner proration (PAY-016)
                if emp.date_of_joining and period.start_date <= emp.date_of_joining <= period.end_date:
                    payable_days = float((period.end_date - emp.date_of_joining).days + 1)
                # Check for resigned employee proration (PAY-017)
                elif emp.resignation_date and period.start_date <= emp.resignation_date <= period.end_date:
                    payable_days = float((emp.resignation_date - period.start_date).days + 1)
                # Check for terminated / inactive employee (PAY-018)
                elif emp.status in ("Terminated", "Resigned", "Inactive"):
                    payable_days = 0.0

            proration_factor = round(payable_days / float(total_days), 4) if total_days > 0 else 0.0


            prorated_basic = round(full_basic * proration_factor, 2)
            prorated_hra = round(full_hra * proration_factor, 2)
            prorated_transport = round(full_transport * proration_factor, 2)
            prorated_medical = round(full_medical * proration_factor, 2)
            prorated_special = round(full_special * proration_factor, 2)

            hourly_rate = round(full_basic / 208.0, 2)
            overtime_pay = round(hourly_rate * overtime_hrs * 1.5, 2)

            # Auto-Fetch Approved Bonuses & Reimbursements
            bonus_obj = db.query(BonusIncentive).filter(BonusIncentive.employee_id == emp.id, BonusIncentive.status == "Pending").first()
            bonus_amount = float(bonus_obj.amount) if bonus_obj else 0.0

            reimb_obj = db.query(Reimbursement).filter(Reimbursement.employee_id == emp.id, Reimbursement.status == "Finance_Approved").first()
            reimb_amount = float(reimb_obj.total_amount) if reimb_obj else 0.0

            gross_salary = round(prorated_basic + prorated_hra + prorated_transport + prorated_medical + prorated_special + overtime_pay + bonus_amount + reimb_amount, 2)

            # Evaluate Statutory Rules
            employee_pf, employer_pf, pf_version = StatutoryEngineService.calculate_employee_pf(db, prorated_basic)
            ee_esi, er_esi, esi_version = StatutoryEngineService.calculate_employee_esi(db, gross_salary)
            professional_tax = StatutoryEngineService.calculate_professional_tax(db, gross_salary)
            tds_data = StatutoryEngineService.calculate_tds_tax(db, gross_salary, regime_name="New Regime")

            # Auto-Fetch Active Loan EMI & Advance Recovery
            loan_obj = db.query(Loan).filter(Loan.employee_id == emp.id, Loan.status == "Active").first()
            loan_emi = float(loan_obj.monthly_emi) if loan_obj else 0.0

            adv_obj = db.query(Advance).filter(Advance.employee_id == emp.id, Advance.status == "Approved").first()
            advance_recovery = float(adv_obj.monthly_recovery_amount) if adv_obj else 0.0

            monthly_tds = float(tds_data.get("monthly_tds", 0.0))

            emp_statutory = round(employee_pf + ee_esi + professional_tax + monthly_tds, 2)
            empr_statutory = round(employer_pf + er_esi, 2)
            emp_deductions = round(emp_statutory + loan_emi + advance_recovery, 2)

            net_salary = round(gross_salary - emp_deductions, 2)
            employer_cost = round(gross_salary + empr_statutory, 2)

            calculation_trace = {
                "step_1_proration": {
                    "total_month_days": total_days,
                    "payable_days": payable_days,
                    "proration_factor": proration_factor,
                    "explanation": f"Proration factor calculated as {payable_days} payable days / {total_days} total days = {proration_factor:.4f}"
                },
                "step_2_earnings_breakdown": {
                    "basic": {"full": full_basic, "prorated": prorated_basic},
                    "hra": {"full": full_hra, "prorated": prorated_hra},
                    "transport": {"full": full_transport, "prorated": prorated_transport},
                    "medical": {"full": full_medical, "prorated": prorated_medical},
                    "special_allowance": {"full": full_special, "prorated": prorated_special},
                    "overtime": {"hourly_rate": hourly_rate, "hours": overtime_hrs, "multiplier": 1.5, "pay": overtime_pay},
                    "bonus": bonus_amount,
                    "reimbursement": reimb_amount,
                    "explanation": f"Gross Salary = Basic (₹{prorated_basic}) + HRA (₹{prorated_hra}) + Transport (₹{prorated_transport}) + Special (₹{prorated_special}) + Overtime (₹{overtime_pay}) + Bonus (₹{bonus_amount}) + Reimbursement (₹{reimb_amount}) = ₹{gross_salary}"
                },
                "step_3_deductions_breakdown": {
                    "employee_pf": {"amount": employee_pf, "rule_version": pf_version, "explanation": "12% of Prorated Basic, capped at ₹1,800.00"},
                    "employee_esi": {"amount": ee_esi, "rule_version": esi_version, "explanation": "0.75% of Gross if Gross <= ₹21,000"},
                    "professional_tax": {"amount": professional_tax, "explanation": "State Statutory PT slab rule"},
                    "loan_emi_deduction": {"amount": loan_emi, "explanation": "Monthly loan EMI auto-deduction"},
                    "advance_recovery": {"amount": advance_recovery, "explanation": "Salary advance recovery"},
                    "total_employee_deductions": emp_deductions
                },
                "step_4_tax_tds": {
                    "financial_year": "2024-2025",
                    "regime_name": tds_data["regime_name"],
                    "standard_deduction": tds_data["standard_deduction"],
                    "taxable_annual": tds_data["taxable_annual"],
                    "monthly_tds": tds_data["monthly_tds"],
                    "rule_version": tds_data["rule_version"],
                    "explanation": f"TDS calculated under {tds_data['regime_name']} ({tds_data['rule_version']}) with ₹{tds_data['standard_deduction']} Standard Deduction"
                },
                "step_5_final_takehome": {
                    "gross_salary": gross_salary,
                    "total_deductions": emp_deductions,
                    "net_salary": net_salary,
                    "employer_cost": employer_cost,
                    "formula_explanation": f"Net Take-Home = Gross (₹{gross_salary}) - Deductions (₹{emp_deductions}) = ₹{net_salary}"
                }
            }

            emp_res = PayrollEmployee(
                payroll_run_id=run.id,
                employee_id=emp.id,
                total_days=total_days,
                payable_days=payable_days,
                gross_salary=gross_salary,
                taxable_income=tds_data["taxable_annual"],
                employee_statutory=emp_statutory,
                employer_statutory=empr_statutory,
                total_deductions=emp_deductions,
                net_salary=net_salary,
                employer_cost=employer_cost,
                calculation_trace=calculation_trace,
            )
            db.add(emp_res)
            db.flush()

            earnings_items = [
                PayrollEarning(payroll_employee_id=emp_res.id, component_code="BASIC", name="Basic Salary", full_amount=full_basic, prorated_amount=prorated_basic),
                PayrollEarning(payroll_employee_id=emp_res.id, component_code="HRA", name="House Rent Allowance", full_amount=full_hra, prorated_amount=prorated_hra),
                PayrollEarning(payroll_employee_id=emp_res.id, component_code="TRANSPORT", name="Transport Allowance", full_amount=full_transport, prorated_amount=prorated_transport),
                PayrollEarning(payroll_employee_id=emp_res.id, component_code="MEDICAL", name="Medical Allowance", full_amount=full_medical, prorated_amount=prorated_medical),
                PayrollEarning(payroll_employee_id=emp_res.id, component_code="SPECIAL_ALLOWANCE", name="Special Allowance", full_amount=full_special, prorated_amount=prorated_special),
            ]
            if overtime_pay > 0:
                earnings_items.append(PayrollEarning(payroll_employee_id=emp_res.id, component_code="OVERTIME", name="Overtime Pay", full_amount=overtime_pay, prorated_amount=overtime_pay))
            if bonus_amount > 0:
                earnings_items.append(PayrollEarning(payroll_employee_id=emp_res.id, component_code="BONUS", name="Bonus / Incentive", full_amount=bonus_amount, prorated_amount=bonus_amount))
            if reimb_amount > 0:
                earnings_items.append(PayrollEarning(payroll_employee_id=emp_res.id, component_code="REIMBURSEMENT", name="Expense Reimbursement", full_amount=reimb_amount, prorated_amount=reimb_amount))

            for earn in earnings_items:
                db.add(earn)

            deduction_items = []
            if employee_pf > 0:
                deduction_items.append(PayrollDeduction(payroll_employee_id=emp_res.id, component_code="PF_EE", name="Employee PF", amount=employee_pf))
            if ee_esi > 0:
                deduction_items.append(PayrollDeduction(payroll_employee_id=emp_res.id, component_code="ESI_EE", name="Employee ESI", amount=ee_esi))
            if professional_tax > 0:
                deduction_items.append(PayrollDeduction(payroll_employee_id=emp_res.id, component_code="PT", name="Professional Tax", amount=professional_tax))
            if monthly_tds > 0:
                deduction_items.append(PayrollDeduction(payroll_employee_id=emp_res.id, component_code="TDS", name="Income Tax (TDS)", amount=monthly_tds))
            if loan_emi > 0:
                deduction_items.append(PayrollDeduction(payroll_employee_id=emp_res.id, component_code="LOAN_EMI", name="Loan EMI Repayment", amount=loan_emi))
            if advance_recovery > 0:
                deduction_items.append(PayrollDeduction(payroll_employee_id=emp_res.id, component_code="ADVANCE_RECOVERY", name="Salary Advance Recovery", amount=advance_recovery))

            for ded in deduction_items:
                db.add(ded)

            total_gross += gross_salary
            total_deductions += emp_deductions
            total_net += net_salary
            total_employer_cost += employer_cost

        run.total_gross = round(total_gross, 2)
        run.total_deductions = round(total_deductions, 2)
        run.total_net = round(total_net, 2)
        run.total_employer_cost = round(total_employer_cost, 2)

        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def get_payroll_run(db: Session, run_id: int) -> PayrollRun:
        run = db.query(PayrollRun).filter(PayrollRun.id == run_id).first()
        if not run:
            raise ResourceNotFoundException("PayrollRun", run_id)
        return run

    @staticmethod
    def approve_payroll_run(db: Session, run_id: int) -> PayrollRun:
        run = PayrollEngineService.get_payroll_run(db, run_id)
        if run.status == "Locked":
            raise PayrollException("Locked payroll runs cannot be modified.", error_code="PAYROLL_ALREADY_LOCKED")
        run.status = "Approved"
        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def lock_payroll_run(db: Session, run_id: int) -> PayrollRun:
        run = PayrollEngineService.get_payroll_run(db, run_id)
        run.status = "Locked"
        run.payroll_period.status = "Locked"
        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def unlock_payroll_run(db: Session, run_id: int) -> PayrollRun:
        run = PayrollEngineService.get_payroll_run(db, run_id)
        run.status = "Calculated"
        if run.payroll_period:
            run.payroll_period.status = "Open"
        db.commit()
        db.refresh(run)
        return run


    @staticmethod
    def update_run_status(db: Session, run_id: int, status_str: str) -> PayrollRun:
        run = PayrollEngineService.get_payroll_run(db, run_id)
        if run.status == "Locked" and status_str not in ("Locked", "Payment", "Paid", "Closed"):
            raise PayrollException("Locked payroll runs cannot revert status.", error_code="PAYROLL_ALREADY_LOCKED")
        run.status = status_str
        if status_str in ("Locked", "Closed"):
            run.payroll_period.status = status_str
        db.commit()
        db.refresh(run)
        return run


    @staticmethod
    def get_employee_calculation_trace(db: Session, run_id: int, employee_id: int) -> Dict[str, Any]:
        emp_res = db.query(PayrollEmployee).filter(
            PayrollEmployee.payroll_run_id == run_id,
            PayrollEmployee.employee_id == employee_id
        ).first()

        if not emp_res:
            raise ResourceNotFoundException("PayrollEmployee Result", employee_id)

        return emp_res.calculation_trace
