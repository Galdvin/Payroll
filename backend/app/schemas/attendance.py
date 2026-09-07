from datetime import date, time, datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ShiftCreate(BaseModel):
    company_id: int
    name: str
    code: str
    start_time: time
    end_time: time
    grace_period_minutes: int = 15
    break_duration_minutes: int = 60
    is_night_shift: bool = False
    overtime_start_after_minutes: int = 30


class ShiftResponse(ShiftCreate):
    id: int

    model_config = {"from_attributes": True}


class CheckInRequest(BaseModel):
    employee_id: int
    date: date
    check_in_time: datetime
    source: str = "Manual"


class CheckOutRequest(BaseModel):
    employee_id: int
    date: date
    check_out_time: datetime


class AttendanceResponse(BaseModel):
    id: int
    employee_id: int
    date: date
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    status: str
    late_minutes: int
    early_departure_minutes: int
    overtime_hours: float
    source: str

    model_config = {"from_attributes": True}


class AttendanceSummaryResponse(BaseModel):
    id: int
    employee_id: int
    year_month: str
    total_days: int
    present_days: float
    absent_days: float
    paid_leave_days: float
    unpaid_leave_days: float
    weekly_off_days: int
    holiday_days: int
    payable_days: float
    overtime_hours: float

    model_config = {"from_attributes": True}
