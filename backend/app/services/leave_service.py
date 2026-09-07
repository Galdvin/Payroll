from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import PayrollException, ResourceNotFoundException
from app.models.leave import LeaveType, LeavePolicy, LeaveBalance, LeaveRequest
from app.models.holiday import Holiday
from app.models.attendance import Attendance
from app.schemas.leave import LeaveTypeCreate, LeavePolicyCreate, LeaveRequestApply, LeaveApprovalRequest, HolidayCreate

DEFAULT_LEAVE_TYPES = [
    ("Annual Leave", "AL", True, True, True),
    ("Sick Leave", "SL", True, False, True),
    ("Casual Leave", "CL", True, False, True),
    ("Unpaid Leave", "UL", False, False, True),
    ("Maternity Leave", "ML", True, False, True),
    ("Paternity Leave", "PL", True, False, True),
]


class LeaveService:

    @staticmethod
    def seed_leave_types(db: Session) -> List[LeaveType]:
        types = []
        for name, code, is_paid, is_encash, req_app in DEFAULT_LEAVE_TYPES:
            existing = db.query(LeaveType).filter(LeaveType.code == code).first()
            if not existing:
                lt = LeaveType(name=name, code=code, is_paid=is_paid, is_encashable=is_encash, requires_approval=req_app)
                db.add(lt)
                types.append(lt)
            else:
                types.append(existing)
        db.commit()
        return types

    @staticmethod
    def get_leave_types(db: Session) -> List[LeaveType]:
        LeaveService.seed_leave_types(db)
        return db.query(LeaveType).all()

    @staticmethod
    def create_leave_policy(db: Session, data: LeavePolicyCreate) -> LeavePolicy:
        policy = LeavePolicy(**data.model_dump())
        db.add(policy)
        db.commit()
        db.refresh(policy)
        return policy

    @staticmethod
    def get_leave_balances(db: Session, employee_id: int, year: int = 2024) -> List[LeaveBalance]:
        LeaveService.seed_leave_types(db)
        l_types = db.query(LeaveType).all()

        balances = []
        for lt in l_types:
            bal = db.query(LeaveBalance).filter(
                LeaveBalance.employee_id == employee_id,
                LeaveBalance.leave_type_id == lt.id,
                LeaveBalance.year == year
            ).first()

            if not bal:
                bal = LeaveBalance(
                    employee_id=employee_id,
                    leave_type_id=lt.id,
                    year=year,
                    accrued=12.0 if lt.is_paid else 0.0,
                    used=0.0,
                    pending=0.0,
                    total_balance=12.0 if lt.is_paid else 0.0,
                )
                db.add(bal)
                db.flush()
            balances.append(bal)

        db.commit()
        return balances

    @staticmethod
    def apply_leave(db: Session, data: LeaveRequestApply) -> LeaveRequest:
        total_days = (data.end_date - data.start_date).days + 1
        if total_days <= 0:
            raise PayrollException("End date must be on or after start date.", error_code="INVALID_DATE_RANGE")

        req = LeaveRequest(
            employee_id=data.employee_id,
            leave_type_id=data.leave_type_id,
            start_date=data.start_date,
            end_date=data.end_date,
            total_days=total_days,
            reason=data.reason,
            status="Pending",
        )
        db.add(req)

        # Update pending balance
        year = data.start_date.year
        bal = db.query(LeaveBalance).filter(
            LeaveBalance.employee_id == data.employee_id,
            LeaveBalance.leave_type_id == data.leave_type_id,
            LeaveBalance.year == year
        ).first()

        if bal:
            bal.pending += total_days

        db.commit()
        db.refresh(req)
        return req

    @staticmethod
    def approve_or_reject_leave(db: Session, request_id: int, user_id: int, data: LeaveApprovalRequest) -> LeaveRequest:
        req = db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()
        if not req:
            raise ResourceNotFoundException("LeaveRequest", request_id)

        req.status = data.status
        req.approved_by_user_id = user_id
        req.approval_comments = data.approval_comments

        year = req.start_date.year
        bal = db.query(LeaveBalance).filter(
            LeaveBalance.employee_id == req.employee_id,
            LeaveBalance.leave_type_id == req.leave_type_id,
            LeaveBalance.year == year
        ).first()

        if data.status == "Approved":
            if bal:
                bal.pending = max(0.0, float(bal.pending) - float(req.total_days))
                bal.used += float(req.total_days)
                bal.total_balance = max(0.0, float(bal.accrued) - float(bal.used))

            # Automatically log attendance records for each day of leave
            lt = db.query(LeaveType).filter(LeaveType.id == req.leave_type_id).first()
            att_status = "Paid Leave" if (lt and lt.is_paid) else "Unpaid Leave"

            curr_date = req.start_date
            while curr_date <= req.end_date:
                existing_att = db.query(Attendance).filter(
                    Attendance.employee_id == req.employee_id,
                    Attendance.date == curr_date
                ).first()
                if existing_att:
                    existing_att.status = att_status
                else:
                    db.add(Attendance(
                        employee_id=req.employee_id,
                        date=curr_date,
                        status=att_status,
                        source="Leave Engine"
                    ))
                curr_date += timedelta(days=1)

        elif data.status == "Rejected":
            if bal:
                bal.pending = max(0.0, float(bal.pending) - float(req.total_days))

        db.commit()
        db.refresh(req)
        return req

    @staticmethod
    def get_leave_requests(db: Session, employee_id: Optional[int] = None) -> List[LeaveRequest]:
        query = db.query(LeaveRequest)
        if employee_id:
            query = query.filter(LeaveRequest.employee_id == employee_id)
        return query.order_by(LeaveRequest.id.desc()).all()

    # --- Holidays ---
    @staticmethod
    def create_holiday(db: Session, data: HolidayCreate) -> Holiday:
        h = Holiday(**data.model_dump())
        db.add(h)
        db.commit()
        db.refresh(h)
        return h

    @staticmethod
    def get_holidays(db: Session, company_id: int = 1) -> List[Holiday]:
        return db.query(Holiday).filter(Holiday.company_id == company_id).order_by(Holiday.date.asc()).all()
