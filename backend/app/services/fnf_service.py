from datetime import date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.core.exceptions import PayrollException, ResourceNotFoundException
from app.models.fnf import FnfSettlement
from app.models.employee import Employee
from app.models.salary import EmployeeSalary
from app.models.leave import LeaveBalance, LeaveType
from app.models.financial_extras import Loan, Advance, BonusIncentive
from app.schemas.fnf import FnfCalculateRequest


class FnfService:

    @staticmethod
    def calculate_fnf(db: Session, req: FnfCalculateRequest) -> FnfSettlement:
        emp = db.query(Employee).filter(Employee.id == req.employee_id).first()
        if not emp:
            raise ResourceNotFoundException("Employee", req.employee_id)

        sal = db.query(EmployeeSalary).filter(EmployeeSalary.employee_id == req.employee_id).first()
        gross_monthly = float(sal.gross_salary) if sal else 50000.0
        
        comp_map = {item.component.code: float(item.monthly_amount) for item in sal.assigned_components} if sal else {}
        basic_monthly = comp_map.get("BASIC", gross_monthly * 0.50)

        daily_gross = round(gross_monthly / 30.0, 2)
        daily_basic = round(basic_monthly / 30.0, 2)

        # 1. Pending Salary
        pending_days = float(req.last_working_date.day)
        pending_salary_amount = round(pending_days * daily_gross, 2)

        # 2. Leave Encashment
        year = req.last_working_date.year
        al_type = db.query(LeaveType).filter(LeaveType.code == "AL").first()
        encash_days = 0.0
        if al_type:
            bal = db.query(LeaveBalance).filter(
                LeaveBalance.employee_id == req.employee_id,
                LeaveBalance.leave_type_id == al_type.id,
                LeaveBalance.year == year
            ).first()
            if bal:
                encash_days = max(0.0, float(bal.total_balance))

        leave_encashment_amount = round(encash_days * daily_basic, 2)

        # 3. Notice Pay & Notice Recovery
        notice_pay_amount = round(req.notice_days_paid * daily_gross, 2)
        notice_recovery_amount = round(req.notice_days_short * daily_gross, 2)

        # 4. Outstanding Loans & Advances
        loan = db.query(Loan).filter(Loan.employee_id == req.employee_id, Loan.status == "Active").first()
        outstanding_loan = float(loan.outstanding_amount) if loan else 0.0

        adv = db.query(Advance).filter(Advance.employee_id == req.employee_id, Advance.status == "Approved").first()
        outstanding_adv = float(adv.amount - adv.recovered_amount) if adv else 0.0

        # 5. Bonus Settlement
        bonuses = db.query(BonusIncentive).filter(BonusIncentive.employee_id == req.employee_id, BonusIncentive.status == "Pending").all()
        pending_bonus = sum(float(b.amount) for b in bonuses) + req.additional_bonus

        # 6. Gratuity Calculation (15/26 * basic * completed_years if tenure >= 5 yrs or override)
        completed_years = 0
        if emp.date_of_joining:
            tenure_days = (req.last_working_date - emp.date_of_joining).days
            completed_years = tenure_days // 365

        if req.gratuity_override is not None:
            gratuity_amount = req.gratuity_override
        elif completed_years >= 5:
            gratuity_amount = round((15.0 / 26.0) * basic_monthly * completed_years, 2)
        else:
            gratuity_amount = 0.0

        # Totals
        gross_settlement = round(pending_salary_amount + leave_encashment_amount + notice_pay_amount + pending_bonus + gratuity_amount, 2)
        total_deductions = round(notice_recovery_amount + outstanding_loan + outstanding_adv, 2)
        net_settlement = max(0.0, round(gross_settlement - total_deductions, 2))

        calculation_trace = {
            "fnf_summary": {
                "employee_code": emp.employee_code,
                "resignation_date": str(req.resignation_date),
                "last_working_date": str(req.last_working_date),
                "settlement_reason": req.settlement_reason,
            },
            "earnings_credits": {
                "pending_salary": {"days": pending_days, "daily_rate": daily_gross, "amount": pending_salary_amount},
                "leave_encashment": {"days": encash_days, "daily_basic": daily_basic, "amount": leave_encashment_amount},
                "notice_pay": {"days": req.notice_days_paid, "amount": notice_pay_amount},
                "bonus_settlement": pending_bonus,
                "gratuity": {"completed_years": completed_years, "amount": gratuity_amount},
                "total_gross_settlement": gross_settlement
            },
            "deductions_recoveries": {
                "notice_recovery": {"short_days": req.notice_days_short, "amount": notice_recovery_amount},
                "outstanding_loan": outstanding_loan,
                "outstanding_advance": outstanding_adv,
                "total_deductions": total_deductions
            },
            "final_payout": {
                "net_settlement_amount": net_settlement,
                "formula_explanation": f"Net F&F Settlement = Gross (₹{gross_settlement}) - Deductions (₹{total_deductions}) = ₹{net_settlement}"
            }
        }

        # Update employee status & resignation date
        emp.resignation_date = req.resignation_date
        emp.status = "Resigned" if req.settlement_reason == "Resignation" else "Terminated"

        existing = db.query(FnfSettlement).filter(FnfSettlement.employee_id == req.employee_id).first()
        if existing:
            fnf = existing
            fnf.resignation_date = req.resignation_date
            fnf.last_working_date = req.last_working_date
            fnf.settlement_date = date.today()
            fnf.settlement_reason = req.settlement_reason
            fnf.pending_salary_days = pending_days
            fnf.pending_salary_amount = pending_salary_amount
            fnf.leave_encashment_days = encash_days
            fnf.leave_encashment_amount = leave_encashment_amount
            fnf.notice_pay_amount = notice_pay_amount
            fnf.bonus_settlement_amount = pending_bonus
            fnf.gratuity_amount = gratuity_amount
            fnf.gross_settlement_amount = gross_settlement
            fnf.notice_recovery_amount = notice_recovery_amount
            fnf.outstanding_loan_deduction = outstanding_loan
            fnf.outstanding_advance_deduction = outstanding_adv
            fnf.total_deductions_amount = total_deductions
            fnf.net_settlement_amount = net_settlement
            fnf.status = "Calculated"
            fnf.remarks = req.remarks
            fnf.calculation_trace = calculation_trace
        else:
            fnf = FnfSettlement(
                employee_id=req.employee_id,
                company_id=emp.company_id or 1,
                resignation_date=req.resignation_date,
                last_working_date=req.last_working_date,
                settlement_date=date.today(),
                settlement_reason=req.settlement_reason,
                pending_salary_days=pending_days,
                pending_salary_amount=pending_salary_amount,
                leave_encashment_days=encash_days,
                leave_encashment_amount=leave_encashment_amount,
                notice_pay_amount=notice_pay_amount,
                bonus_settlement_amount=pending_bonus,
                gratuity_amount=gratuity_amount,
                gross_settlement_amount=gross_settlement,
                notice_recovery_amount=notice_recovery_amount,
                outstanding_loan_deduction=outstanding_loan,
                outstanding_advance_deduction=outstanding_adv,
                total_deductions_amount=total_deductions,
                net_settlement_amount=net_settlement,
                status="Calculated",
                remarks=req.remarks,
                calculation_trace=calculation_trace,
            )
            db.add(fnf)

        db.commit()
        db.refresh(fnf)
        return fnf

    @staticmethod
    def get_fnf(db: Session, employee_id: int) -> FnfSettlement:
        fnf = db.query(FnfSettlement).filter(FnfSettlement.employee_id == employee_id).first()
        if not fnf:
            raise ResourceNotFoundException("FnfSettlement", employee_id)
        return fnf

    @staticmethod
    def approve_fnf(db: Session, fnf_id: int) -> FnfSettlement:
        fnf = db.query(FnfSettlement).filter(FnfSettlement.id == fnf_id).first()
        if not fnf:
            raise ResourceNotFoundException("FnfSettlement", fnf_id)
        fnf.status = "Approved"
        db.commit()
        db.refresh(fnf)
        return fnf
