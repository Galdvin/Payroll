import math
from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import PayrollException, ResourceNotFoundException
from app.models.financial_extras import (
    Loan,
    LoanTransaction,
    Advance,
    BonusIncentive,
    Reimbursement,
    ReimbursementItem,
)
from app.models.employee import Employee
from app.schemas.financial_extras import (
    LoanRequestCreate,
    AdvanceRequestCreate,
    BonusIncentiveCreate,
    ReimbursementCreate,
    ReimbursementApprovalRequest,
)


class FinancialExtrasService:

    # --- Loans & EMI Amortization ---
    @staticmethod
    def calculate_emi(principal: float, rate_percent: float, tenure_months: int) -> float:
        if rate_percent <= 0:
            return round(principal / tenure_months, 2)
        r = (rate_percent / 12.0) / 100.0
        n = tenure_months
        emi = (principal * r * math.pow(1 + r, n)) / (math.pow(1 + r, n) - 1)
        return round(emi, 2)

    @staticmethod
    def request_loan(db: Session, data: LoanRequestCreate) -> Loan:
        emp = db.query(Employee).filter(Employee.id == data.employee_id).first()
        if not emp:
            raise ResourceNotFoundException("Employee", data.employee_id)

        emi = FinancialExtrasService.calculate_emi(data.principal, data.interest_rate, data.tenure_months)
        loan = Loan(
            employee_id=data.employee_id,
            principal=data.principal,
            interest_rate=data.interest_rate,
            tenure_months=data.tenure_months,
            start_date=data.start_date,
            monthly_emi=emi,
            outstanding_amount=data.principal,
            status="Requested",
        )
        db.add(loan)
        db.commit()
        db.refresh(loan)
        return loan

    @staticmethod
    def approve_loan(db: Session, loan_id: int) -> Loan:
        loan = db.query(Loan).filter(Loan.id == loan_id).first()
        if not loan:
            raise ResourceNotFoundException("Loan", loan_id)
        loan.status = "Active"
        db.commit()
        db.refresh(loan)
        return loan

    @staticmethod
    def get_loans(db: Session, employee_id: Optional[int] = None) -> List[Loan]:
        query = db.query(Loan)
        if employee_id:
            query = query.filter(Loan.employee_id == employee_id)
        return query.order_by(Loan.id.desc()).all()

    # --- Advances ---
    @staticmethod
    def request_advance(db: Session, data: AdvanceRequestCreate) -> Advance:
        monthly_rec = round(data.amount / float(data.recovery_months), 2)
        adv = Advance(
            employee_id=data.employee_id,
            amount=data.amount,
            request_date=data.request_date,
            recovery_months=data.recovery_months,
            monthly_recovery_amount=monthly_rec,
            recovered_amount=0.0,
            status="Approved",
        )
        db.add(adv)
        db.commit()
        db.refresh(adv)
        return adv

    @staticmethod
    def get_advances(db: Session, employee_id: Optional[int] = None) -> List[Advance]:
        query = db.query(Advance)
        if employee_id:
            query = query.filter(Advance.employee_id == employee_id)
        return query.order_by(Advance.id.desc()).all()

    # --- Bonuses & Incentives ---
    @staticmethod
    def create_bonus(db: Session, data: BonusIncentiveCreate) -> BonusIncentive:
        bonus = BonusIncentive(
            employee_id=data.employee_id,
            title=data.title,
            category=data.category,
            amount=data.amount,
            is_taxable=data.is_taxable,
            payout_date=data.payout_date,
            status="Pending",
        )
        db.add(bonus)
        db.commit()
        db.refresh(bonus)
        return bonus

    @staticmethod
    def get_bonuses(db: Session, employee_id: Optional[int] = None) -> List[BonusIncentive]:
        query = db.query(BonusIncentive)
        if employee_id:
            query = query.filter(BonusIncentive.employee_id == employee_id)
        return query.order_by(BonusIncentive.id.desc()).all()

    # --- Reimbursements & Approvals ---
    @staticmethod
    def create_reimbursement(db: Session, data: ReimbursementCreate) -> Reimbursement:
        total = sum(item.amount for item in data.items)
        reimb = Reimbursement(
            employee_id=data.employee_id,
            title=data.title,
            category=data.category,
            total_amount=total,
            status="Submitted",
        )
        db.add(reimb)
        db.flush()

        for item in data.items:
            db.add(ReimbursementItem(
                reimbursement_id=reimb.id,
                description=item.description,
                amount=item.amount,
                receipt_file_name="receipt_claim.pdf"
            ))

        db.commit()
        db.refresh(reimb)
        return reimb

    @staticmethod
    def approve_reimbursement(db: Session, reimb_id: int, user_id: int, data: ReimbursementApprovalRequest) -> Reimbursement:
        reimb = db.query(Reimbursement).filter(Reimbursement.id == reimb_id).first()
        if not reimb:
            raise ResourceNotFoundException("Reimbursement", reimb_id)

        if data.status == "Manager_Approved":
            reimb.status = "Manager_Approved"
            reimb.manager_user_id = user_id
        elif data.status == "Finance_Approved":
            reimb.status = "Finance_Approved"
            reimb.finance_user_id = user_id
        elif data.status == "Rejected":
            reimb.status = "Rejected"

        db.commit()
        db.refresh(reimb)
        return reimb

    @staticmethod
    def get_reimbursements(db: Session, employee_id: Optional[int] = None) -> List[Reimbursement]:
        query = db.query(Reimbursement)
        if employee_id:
            query = query.filter(Reimbursement.employee_id == employee_id)
        return query.order_by(Reimbursement.id.desc()).all()
