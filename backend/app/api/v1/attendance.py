from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.attendance import (
    ShiftCreate,
    ShiftResponse,
    CheckInRequest,
    CheckOutRequest,
    AttendanceResponse,
    AttendanceSummaryResponse,
)
from app.services.attendance_service import AttendanceService
from app.security.permissions import RequirePermission, get_current_user
from app.models.user import User

router = APIRouter(prefix="/attendance", tags=["Attendance & Shifts"])


@router.get("/shifts", response_model=List[ShiftResponse], status_code=status.HTTP_200_OK)
def list_shifts(company_id: int = 1, db: Session = Depends(get_db), _: User = Depends(RequirePermission("attendance.view"))):
    return AttendanceService.get_shifts(db, company_id)


@router.post("/shifts", response_model=ShiftResponse, status_code=status.HTTP_201_CREATED)
def create_shift(body: ShiftCreate, db: Session = Depends(get_db), _: User = Depends(RequirePermission("attendance.manage"))):
    return AttendanceService.create_shift(db, body)


@router.post("/check-in", response_model=AttendanceResponse, status_code=status.HTTP_200_OK)
def check_in(body: CheckInRequest, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return AttendanceService.check_in(db, body)


@router.post("/check-out", response_model=AttendanceResponse, status_code=status.HTTP_200_OK)
def check_out(body: CheckOutRequest, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return AttendanceService.check_out(db, body)


@router.get("", response_model=List[AttendanceResponse], status_code=status.HTTP_200_OK)
def list_attendance(
    employee_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("attendance.view")),
):
    return AttendanceService.get_attendance_records(db, employee_id=employee_id, start_date=start_date, end_date=end_date)


@router.get("/summary", response_model=AttendanceSummaryResponse, status_code=status.HTTP_200_OK)
def get_attendance_summary(
    employee_id: int,
    year_month: str = Query(..., example="2024-09"),
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("attendance.view")),
):
    """Aggregate monthly attendance data as payable days input for the payroll calculation engine."""
    return AttendanceService.generate_attendance_summary(db, employee_id=employee_id, year_month=year_month)
