from datetime import date, datetime, timedelta, time
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import extract
from app.core.exceptions import PayrollException, ResourceNotFoundException
from app.models.attendance import Attendance, AttendanceSummary
from app.models.shift import Shift, ShiftAssignment
from app.schemas.attendance import ShiftCreate, CheckInRequest, CheckOutRequest


class AttendanceService:

    # --- Shifts ---
    @staticmethod
    def get_shifts(db: Session, company_id: int) -> List[Shift]:
        return db.query(Shift).filter(Shift.company_id == company_id).all()

    @staticmethod
    def create_shift(db: Session, data: ShiftCreate) -> Shift:
        shift = Shift(**data.model_dump())
        db.add(shift)
        db.commit()
        db.refresh(shift)
        return shift

    # --- Daily Attendance ---
    @staticmethod
    def check_in(db: Session, data: CheckInRequest) -> Attendance:
        existing = db.query(Attendance).filter(
            Attendance.employee_id == data.employee_id,
            Attendance.date == data.date
        ).first()

        if existing:
            existing.check_in = data.check_in_time
            existing.source = data.source
            att = existing
        else:
            att = Attendance(
                employee_id=data.employee_id,
                date=data.date,
                check_in=data.check_in_time,
                status="Present",
                source=data.source,
            )
            db.add(att)

        db.commit()
        db.refresh(att)
        return att

    @staticmethod
    def check_out(db: Session, data: CheckOutRequest) -> Attendance:
        att = db.query(Attendance).filter(
            Attendance.employee_id == data.employee_id,
            Attendance.date == data.date
        ).first()

        if not att:
            raise ResourceNotFoundException("Attendance record for date", data.date)

        att.check_out = data.check_out_time

        # Calculate overtime hours if check-in and check-out exist
        if att.check_in and att.check_out:
            duration_seconds = (att.check_out - att.check_in).total_seconds()
            hours_worked = duration_seconds / 3600.0
            # Standard workday = 8.0 hours. Overtime = worked - 8.0
            if hours_worked > 8.5:
                att.overtime_hours = round(hours_worked - 8.0, 2)

        db.commit()
        db.refresh(att)
        return att

    @staticmethod
    def get_attendance_records(
        db: Session,
        employee_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Attendance]:
        query = db.query(Attendance)
        if employee_id:
            query = query.filter(Attendance.employee_id == employee_id)
        if start_date:
            query = query.filter(Attendance.date >= start_date)
        if end_date:
            query = query.filter(Attendance.date <= end_date)
        return query.order_by(Attendance.date.desc()).all()

    # --- Summary Aggregator for Payroll ---
    @staticmethod
    def generate_attendance_summary(db: Session, employee_id: int, year_month: str) -> AttendanceSummary:
        """Aggregate month's attendance to compute payable days for payroll engine."""
        year, month = map(int, year_month.split("-"))
        records = db.query(Attendance).filter(
            Attendance.employee_id == employee_id,
            extract('year', Attendance.date) == year,
            extract('month', Attendance.date) == month
        ).all()

        total_days = 30  # Standard monthly denominator
        present_days = sum(1.0 for r in records if r.status == "Present")
        half_days = sum(0.5 for r in records if r.status == "Half Day")
        present_days += half_days
        absent_days = sum(1.0 for r in records if r.status == "Absent")
        paid_leave = sum(1.0 for r in records if r.status == "Paid Leave")
        unpaid_leave = sum(1.0 for r in records if r.status == "Unpaid Leave")
        overtime_hrs = sum(float(r.overtime_hours) for r in records)

        # Standard weekly off (8 days) + holidays (2 days) if not explicitly logged
        weekly_off = 8
        holidays = 2
        
        # Payable Days formula: Present + Paid Leave + Weekly Off + Holidays - Unpaid Leave
        payable_days = max(0.0, present_days + paid_leave + weekly_off + holidays - unpaid_leave)

        summary = db.query(AttendanceSummary).filter(
            AttendanceSummary.employee_id == employee_id,
            AttendanceSummary.year_month == year_month
        ).first()

        if not summary:
            summary = AttendanceSummary(
                employee_id=employee_id,
                year_month=year_month,
                total_days=total_days,
                present_days=present_days,
                absent_days=absent_days,
                paid_leave_days=paid_leave,
                unpaid_leave_days=unpaid_leave,
                weekly_off_days=weekly_off,
                holiday_days=holidays,
                payable_days=payable_days,
                overtime_hours=overtime_hrs,
            )
            db.add(summary)
        else:
            summary.present_days = present_days
            summary.absent_days = absent_days
            summary.paid_leave_days = paid_leave
            summary.unpaid_leave_days = unpaid_leave
            summary.payable_days = payable_days
            summary.overtime_hours = overtime_hrs

        db.commit()
        db.refresh(summary)
        return summary
