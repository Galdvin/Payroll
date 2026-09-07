from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.financial_extras import (
    LoanRequestCreate,
    LoanResponse,
    AdvanceRequestCreate,
    AdvanceResponse,
    BonusIncentiveCreate,
    BonusIncentiveResponse,
    ReimbursementCreate,
    ReimbursementResponse,
    ReimbursementApprovalRequest,
)
from app.services.financial_extras_service import FinancialExtrasService
from app.security.permissions import RequirePermission, get_current_user
from app.models.user import User

router = APIRouter(prefix="/financial-extras", tags=["Loans, Bonuses & Reimbursements"])


# --- Loans ---
@router.get("/loans", response_model=List[LoanResponse], status_code=status.HTTP_200_OK)
def list_loans(employee_id: Optional[int] = None, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return FinancialExtrasService.get_loans(db, employee_id=employee_id)


@router.post("/loans", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
def request_loan(body: LoanRequestCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return FinancialExtrasService.request_loan(db, body)


@router.post("/loans/{loan_id}/approve", response_model=LoanResponse, status_code=status.HTTP_200_OK)
def approve_loan(loan_id: int, db: Session = Depends(get_db), _: User = Depends(RequirePermission("payroll.approve"))):
    return FinancialExtrasService.approve_loan(db, loan_id=loan_id)


@router.post("/loans/{loan_id}/cancel", response_model=LoanResponse, status_code=status.HTTP_200_OK)
def cancel_loan(loan_id: int, db: Session = Depends(get_db), _: User = Depends(RequirePermission("payroll.create"))):
    return FinancialExtrasService.cancel_loan(db, loan_id=loan_id)


@router.post("/loans/{loan_id}/repay", response_model=LoanResponse, status_code=status.HTTP_200_OK)
def record_repayment(loan_id: int, body: LoanRepaymentRequest, db: Session = Depends(get_db), _: User = Depends(RequirePermission("payroll.create"))):
    return FinancialExtrasService.record_repayment(db, loan_id=loan_id, req=body)



# --- Advances ---
@router.get("/advances", response_model=List[AdvanceResponse], status_code=status.HTTP_200_OK)
def list_advances(employee_id: Optional[int] = None, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return FinancialExtrasService.get_advances(db, employee_id=employee_id)


@router.post("/advances", response_model=AdvanceResponse, status_code=status.HTTP_201_CREATED)
def request_advance(body: AdvanceRequestCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return FinancialExtrasService.request_advance(db, body)


# --- Bonuses ---
@router.get("/bonuses", response_model=List[BonusIncentiveResponse], status_code=status.HTTP_200_OK)
def list_bonuses(employee_id: Optional[int] = None, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return FinancialExtrasService.get_bonuses(db, employee_id=employee_id)


@router.post("/bonuses", response_model=BonusIncentiveResponse, status_code=status.HTTP_201_CREATED)
def create_bonus(body: BonusIncentiveCreate, db: Session = Depends(get_db), _: User = Depends(RequirePermission("payroll.create"))):
    return FinancialExtrasService.create_bonus(db, body)


@router.post("/bonuses/{bonus_id}/cancel", response_model=BonusIncentiveResponse, status_code=status.HTTP_200_OK)
def cancel_bonus(bonus_id: int, db: Session = Depends(get_db), _: User = Depends(RequirePermission("payroll.create"))):
    return FinancialExtrasService.cancel_bonus(db, bonus_id=bonus_id)



# --- Reimbursements ---
@router.get("/reimbursements", response_model=List[ReimbursementResponse], status_code=status.HTTP_200_OK)
def list_reimbursements(employee_id: Optional[int] = None, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return FinancialExtrasService.get_reimbursements(db, employee_id=employee_id)


@router.post("/reimbursements", response_model=ReimbursementResponse, status_code=status.HTTP_201_CREATED)
def create_reimbursement(body: ReimbursementCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return FinancialExtrasService.create_reimbursement(db, body)


@router.post("/reimbursements/{reimb_id}/approve", response_model=ReimbursementResponse, status_code=status.HTTP_200_OK)
def approve_reimbursement(
    reimb_id: int,
    body: ReimbursementApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FinancialExtrasService.approve_reimbursement(db, reimb_id=reimb_id, user_id=current_user.id, data=body)
