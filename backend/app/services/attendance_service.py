from datetime import date, datetime, timedelta, time
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import extract
from app.core.exceptions import PayrollException, ResourceNotFoundException
from app.models.attendance import Attendance, AttendanceSummary
from app.models.employee import Employee
from app.models.shift import Shift, ShiftAssignment
from app.schemas.attendance import (
    ShiftCreate,
    CheckInRequest,
    CheckOutRequest,
    MarkAttendanceRequest,
    BulkImportItem,
    AttendanceCorrectionRequest,
)
from app.services.audit_service import AuditService


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
    def mark_attendance(db: Session, data: MarkAttendanceRequest, prevent_duplicate: bool = False) -> Attendance:
        if data.overtime_hours < 0:
            raise PayrollException("Overtime hours cannot be negative.", error_code="INVALID_OVERTIME")
        if data.overtime_hours > 12.0:
            raise PayrollException("Overtime hours exceed maximum configured daily limit of 12 hours.", error_code="OT_LIMIT_EXCEEDED")

        # Check employee validity
        emp = db.query(Employee).filter(Employee.id == data.employee_id).first()
        if not emp:
            raise ResourceNotFoundException("Employee", data.employee_id)


        existing = db.query(Attendance).filter(
            Attendance.employee_id == data.employee_id,
            Attendance.date == data.date
        ).first()

        if existing:
            if prevent_duplicate:
                raise PayrollException(f"Duplicate attendance record for employee {data.employee_id} on date {data.date}")
            att = existing
            att.status = data.status
            if data.check_in:
                att.check_in = data.check_in
            if data.check_out:
                att.check_out = data.check_out
            att.late_minutes = data.late_minutes
            att.early_departure_minutes = data.early_departure_minutes
            att.overtime_hours = data.overtime_hours
            att.source = data.source
        else:
            att = Attendance(
                employee_id=data.employee_id,
                date=data.date,
                status=data.status,
                check_in=data.check_in,
                check_out=data.check_out,
                late_minutes=data.late_minutes,
                early_departure_minutes=data.early_departure_minutes,
                overtime_hours=data.overtime_hours,
                source=data.source,
            )
            db.add(att)

        db.commit()
        db.refresh(att)
        return att

    @staticmethod
    def check_in(db: Session, data: CheckInRequest, prevent_duplicate: bool = False) -> Attendance:
        existing = db.query(Attendance).filter(
            Attendance.employee_id == data.employee_id,
            Attendance.date == data.date
        ).first()

        if existing:
            if prevent_duplicate or existing.check_in is not None:
                raise PayrollException(f"Duplicate attendance check-in for employee {data.employee_id} on {data.date}")
            existing.check_in = data.check_in_time
            existing.source = data.source
            att = existing
        else:
            # Check for late arrival against standard shift start (09:00:00)
            late_mins = 0
            if data.check_in_time and data.check_in_time.time() > time(9, 15):
                shift_start = datetime.combine(data.date, time(9, 0))
                check_in_naive = data.check_in_time.replace(tzinfo=None) if data.check_in_time.tzinfo else data.check_in_time
                late_mins = max(0, int((check_in_naive - shift_start).total_seconds() / 60))

            att = Attendance(
                employee_id=data.employee_id,
                date=data.date,
                check_in=data.check_in_time,
                status="Present",
                late_minutes=late_mins,
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

        # Calculate early departure and overtime hours if check-in and check-out exist
        if att.check_in and att.check_out:
            check_in_naive = att.check_in.replace(tzinfo=None) if att.check_in.tzinfo else att.check_in
            check_out_naive = att.check_out.replace(tzinfo=None) if att.check_out.tzinfo else att.check_out
            
            duration_seconds = (check_out_naive - check_in_naive).total_seconds()
            hours_worked = duration_seconds / 3600.0

            # Early departure check (standard shift end = 18:00)
            shift_end = datetime.combine(data.date, time(18, 0))
            if check_out_naive < shift_end:
                att.early_departure_minutes = max(0, int((shift_end - check_out_naive).total_seconds() / 60))

            # Standard workday = 8.0 hours. Overtime = worked - 8.0
            if hours_worked > 8.0:
                att.overtime_hours = round(hours_worked - 8.0, 2)

        db.commit()
        db.refresh(att)
        return att

    @staticmethod
    def bulk_import(db: Session, items: List[BulkImportItem]) -> List[Attendance]:
        # Validate all employee IDs upfront
        emp_ids = {item.employee_id for item in items}
        existing_emps = {e.id for e in db.query(Employee.id).filter(Employee.id.in_(emp_ids)).all()}
        
        invalid_ids = emp_ids - existing_emps
        if invalid_ids:
            sorted_invalid = sorted(list(invalid_ids))
            raise PayrollException(f"Invalid employee ID in import: {sorted_invalid[0]}")

        imported = []
        for item in items:
            record = AttendanceService.mark_attendance(
                db,
                MarkAttendanceRequest(
                    employee_id=item.employee_id,
                    date=item.date,
                    status=item.status,
                    check_in=item.check_in,
                    check_out=item.check_out,
                    source=item.source,
                ),
            )
            imported.append(record)

        return imported

    @staticmethod
    def correct_attendance(
        db: Session,
        attendance_id: int,
        req: AttendanceCorrectionRequest,
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
    ) -> Attendance:
        att = db.query(Attendance).filter(Attendance.id == attendance_id).first()
        if not att:
            raise ResourceNotFoundException("Attendance record", attendance_id)

        old_values = {
            "status": att.status,
            "check_in": str(att.check_in) if att.check_in else None,
            "check_out": str(att.check_out) if att.check_out else None,
            "late_minutes": att.late_minutes,
            "early_departure_minutes": att.early_departure_minutes,
            "overtime_hours": float(att.overtime_hours),
        }

        if req.status is not None:
            att.status = req.status
        if req.check_in is not None:
            att.check_in = req.check_in
        if req.check_out is not None:
            att.check_out = req.check_out
        if req.late_minutes is not None:
            att.late_minutes = req.late_minutes
        if req.early_departure_minutes is not None:
            att.early_departure_minutes = req.early_departure_minutes
        if req.overtime_hours is not None:
            att.overtime_hours = req.overtime_hours

        db.commit()
        db.refresh(att)

        new_values = {
            "status": att.status,
            "check_in": str(att.check_in) if att.check_in else None,
            "check_out": str(att.check_out) if att.check_out else None,
            "late_minutes": att.late_minutes,
            "early_departure_minutes": att.early_departure_minutes,
            "overtime_hours": float(att.overtime_hours),
            "reason": req.reason,
        }

        # Cryptographic Audit Log entry
        AuditService.log_action(
            db=db,
            action="ATTENDANCE_CORRECTION",
            module="Attendance",
            user_id=user_id,
            user_email=user_email,
            record_id=str(attendance_id),
            old_values=old_values,
            new_values=new_values,
        )

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

    @staticmethod
    def delete_attendance(db: Session, attendance_id: int) -> dict:
        att = db.query(Attendance).filter(Attendance.id == attendance_id).first()
        if not att:
            raise ResourceNotFoundException("Attendance record", attendance_id)
        db.delete(att)
        db.commit()
        return {"success": True, "message": f"Attendance record {attendance_id} deleted successfully."}

    @staticmethod
    def delete_shift(db: Session, shift_id: int) -> dict:
        shift = db.query(Shift).filter(Shift.id == shift_id).first()
        if not shift:
            raise ResourceNotFoundException("Shift", shift_id)
        db.delete(shift)
        db.commit()
        return {"success": True, "message": f"Shift {shift_id} deleted successfully."}

