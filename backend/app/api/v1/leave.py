from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.leave import (
    LeaveTypeResponse,
    LeavePolicyCreate,
    LeavePolicyResponse,
    LeaveBalanceResponse,
    LeaveRequestApply,
    LeaveApprovalRequest,
    LeaveRequestResponse,
    HolidayCreate,
    HolidayResponse,
    CarryForwardRequest,
    CarryForwardResponse,
    LeaveEncashmentRequest,
    LeaveEncashmentResponse,
)
from app.services.leave_service import LeaveService
from app.security.permissions import RequirePermission, get_current_user
from app.models.user import User

router = APIRouter(prefix="/leaves", tags=["Leave & Holidays"])


@router.get("/types", response_model=List[LeaveTypeResponse], status_code=status.HTTP_200_OK)
def list_leave_types(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return LeaveService.get_leave_types(db)


@router.post("/policies", response_model=LeavePolicyResponse, status_code=status.HTTP_201_CREATED)
def create_leave_policy(body: LeavePolicyCreate, db: Session = Depends(get_db), _: User = Depends(RequirePermission("attendance.manage"))):
    return LeaveService.create_leave_policy(db, body)


@router.get("/balances", response_model=List[LeaveBalanceResponse], status_code=status.HTTP_200_OK)
def get_leave_balances(employee_id: int, year: int = 2024, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return LeaveService.get_leave_balances(db, employee_id=employee_id, year=year)


@router.post("/requests", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
def apply_leave(body: LeaveRequestApply, db: Session = Depends(get_db), _: User = Depends(RequirePermission("leave.apply"))):
    return LeaveService.apply_leave(db, body)


@router.get("/requests", response_model=List[LeaveRequestResponse], status_code=status.HTTP_200_OK)
def list_leave_requests(employee_id: Optional[int] = None, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return LeaveService.get_leave_requests(db, employee_id=employee_id)


@router.post("/requests/{request_id}/approve", response_model=LeaveRequestResponse, status_code=status.HTTP_200_OK)
def approve_or_reject_leave(
    request_id: int,
    body: LeaveApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("leave.approve")),
):
    return LeaveService.approve_or_reject_leave(db, request_id=request_id, user_id=current_user.id, data=body)


@router.post("/requests/{request_id}/cancel", response_model=LeaveRequestResponse, status_code=status.HTTP_200_OK)
def cancel_leave(
    request_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("leave.apply")),
):
    return LeaveService.cancel_leave(db, request_id=request_id)


@router.post("/carry-forward", response_model=CarryForwardResponse, status_code=status.HTTP_200_OK)
def process_carry_forward(
    body: CarryForwardRequest,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("attendance.manage")),
):
    return LeaveService.process_carry_forward(db, req=body)


@router.post("/encash", response_model=LeaveEncashmentResponse, status_code=status.HTTP_200_OK)
def encash_leave(
    body: LeaveEncashmentRequest,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("leave.apply")),
):
    return LeaveService.encash_leave(db, req=body)


# --- Holidays ---
@router.get("/holidays", response_model=List[HolidayResponse], status_code=status.HTTP_200_OK)
def list_holidays(company_id: int = 1, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return LeaveService.get_holidays(db, company_id=company_id)


@router.post("/holidays", response_model=HolidayResponse, status_code=status.HTTP_201_CREATED)
def create_holiday(body: HolidayCreate, db: Session = Depends(get_db), _: User = Depends(RequirePermission("attendance.manage"))):
    return LeaveService.create_holiday(db, body)


@router.delete("/requests/{request_id}", status_code=status.HTTP_200_OK)
def delete_leave_request(
    request_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("leave.apply")),
):
    return LeaveService.delete_leave_request(db, request_id)


@router.delete("/types/{leave_type_id}", status_code=status.HTTP_200_OK)
def delete_leave_type(
    leave_type_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("attendance.manage")),
):
    return LeaveService.delete_leave_type(db, leave_type_id)


@router.delete("/holidays/{holiday_id}", status_code=status.HTTP_200_OK)
def delete_holiday(
    holiday_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("attendance.manage")),
):
    return LeaveService.delete_holiday(db, holiday_id)

