from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import PayrollException, ResourceNotFoundException
from app.models.leave import LeaveType, LeavePolicy, LeaveBalance, LeaveRequest
from app.models.holiday import Holiday
from app.models.attendance import Attendance
from app.schemas.leave import (
    LeaveTypeCreate,
    LeavePolicyCreate,
    LeaveRequestApply,
    LeaveApprovalRequest,
    HolidayCreate,
    CarryForwardRequest,
    CarryForwardResponse,
    LeaveEncashmentRequest,
    LeaveEncashmentResponse,
)

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
        calendar_days = (data.end_date - data.start_date).days + 1
        if calendar_days <= 0:
            raise PayrollException("End date must be on or after start date.", error_code="INVALID_DATE_RANGE")

        # Exclude holidays falling inside the leave period (LEAVE-008)
        holidays = db.query(Holiday).filter(
            Holiday.date >= data.start_date,
            Holiday.date <= data.end_date
        ).all()
        holiday_dates = {h.date for h in holidays}

        net_leave_days = sum(1 for i in range(calendar_days) if (data.start_date + timedelta(days=i)) not in holiday_dates)
        if net_leave_days <= 0:
            raise PayrollException("Selected date range consists entirely of official holidays.", error_code="ALL_HOLIDAYS")

        lt = db.query(LeaveType).filter(LeaveType.id == data.leave_type_id).first()
        year = data.start_date.year
        
        # Ensure balances are seeded
        LeaveService.get_leave_balances(db, data.employee_id, year)
        
        bal = db.query(LeaveBalance).filter(
            LeaveBalance.employee_id == data.employee_id,
            LeaveBalance.leave_type_id == data.leave_type_id,
            LeaveBalance.year == year
        ).first()

        # Check available balance for paid leave types (LEAVE-002)
        if lt and lt.is_paid:
            avail = (float(bal.total_balance) - float(bal.pending)) if bal else 0.0
            if avail < net_leave_days:
                raise PayrollException("Insufficient leave balance for requested leave type.", error_code="INSUFFICIENT_LEAVE_BALANCE")

        req = LeaveRequest(
            employee_id=data.employee_id,
            leave_type_id=data.leave_type_id,
            start_date=data.start_date,
            end_date=data.end_date,
            total_days=float(net_leave_days),
            reason=data.reason,
            status="Pending",
        )
        db.add(req)

        if bal:
            bal.pending = float(bal.pending) + float(net_leave_days)

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
                bal.used = float(bal.used) + float(req.total_days)
                bal.total_balance = max(0.0, float(bal.accrued) - float(bal.used))

            # Automatically log attendance records for each day of leave (excluding holidays)
            holidays = db.query(Holiday).filter(
                Holiday.date >= req.start_date,
                Holiday.date <= req.end_date
            ).all()
            holiday_dates = {h.date for h in holidays}

            lt = db.query(LeaveType).filter(LeaveType.id == req.leave_type_id).first()
            att_status = "Paid Leave" if (lt and lt.is_paid) else "Unpaid Leave"

            curr_date = req.start_date
            while curr_date <= req.end_date:
                if curr_date not in holiday_dates:
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
    def cancel_leave(db: Session, request_id: int) -> LeaveRequest:
        req = db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()
        if not req:
            raise ResourceNotFoundException("LeaveRequest", request_id)

        if req.status == "Cancelled":
            return req

        year = req.start_date.year
        bal = db.query(LeaveBalance).filter(
            LeaveBalance.employee_id == req.employee_id,
            LeaveBalance.leave_type_id == req.leave_type_id,
            LeaveBalance.year == year
        ).first()

        if req.status == "Pending":
            if bal:
                bal.pending = max(0.0, float(bal.pending) - float(req.total_days))
        elif req.status == "Approved":
            if bal:
                bal.used = max(0.0, float(bal.used) - float(req.total_days))
                bal.total_balance = float(bal.total_balance) + float(req.total_days)

            # Revert attendance records created by leave engine
            curr_date = req.start_date
            while curr_date <= req.end_date:
                att = db.query(Attendance).filter(
                    Attendance.employee_id == req.employee_id,
                    Attendance.date == curr_date,
                    Attendance.source == "Leave Engine"
                ).first()
                if att:
                    db.delete(att)
                curr_date += timedelta(days=1)

        req.status = "Cancelled"
        db.commit()
        db.refresh(req)
        return req

    @staticmethod
    def process_carry_forward(db: Session, req: CarryForwardRequest) -> CarryForwardResponse:
        from_bals = db.query(LeaveBalance).filter(
            LeaveBalance.employee_id == req.employee_id,
            LeaveBalance.year == req.from_year
        ).all()

        total_cf = 0.0
        for fb in from_bals:
            unused = max(0.0, float(fb.total_balance))
            cf = min(unused, req.max_carry_forward)
            total_cf += cf

        # Ensure to_year balance exists
        LeaveService.get_leave_balances(db, req.employee_id, req.to_year)
        ann_lt = db.query(LeaveType).filter(LeaveType.code == "AL").first()
        
        new_total = 0.0
        if ann_lt:
            to_bal = db.query(LeaveBalance).filter(
                LeaveBalance.employee_id == req.employee_id,
                LeaveBalance.leave_type_id == ann_lt.id,
                LeaveBalance.year == req.to_year
            ).first()
            if to_bal:
                to_bal.accrued = float(to_bal.accrued) + total_cf
                to_bal.total_balance = float(to_bal.total_balance) + total_cf
                new_total = float(to_bal.total_balance)

        db.commit()

        return CarryForwardResponse(
            employee_id=req.employee_id,
            from_year=req.from_year,
            to_year=req.to_year,
            carried_forward_days=total_cf,
            new_total_balance=new_total,
        )

    @staticmethod
    def encash_leave(db: Session, req: LeaveEncashmentRequest) -> LeaveEncashmentResponse:
        lt = db.query(LeaveType).filter(LeaveType.id == req.leave_type_id).first()
        if not lt or not lt.is_encashable:
            raise PayrollException("Selected leave type is not eligible for encashment.")

        LeaveService.get_leave_balances(db, req.employee_id, req.year)

        bal = db.query(LeaveBalance).filter(
            LeaveBalance.employee_id == req.employee_id,
            LeaveBalance.leave_type_id == req.leave_type_id,
            LeaveBalance.year == req.year
        ).first()

        if not bal or float(bal.total_balance) < req.days:
            raise PayrollException("Insufficient leave balance for encashment.")

        bal.used = float(bal.used) + req.days
        bal.total_balance = max(0.0, float(bal.total_balance) - req.days)

        amount = req.days * req.daily_rate
        db.commit()
        db.refresh(bal)

        return LeaveEncashmentResponse(
            employee_id=req.employee_id,
            leave_type_id=req.leave_type_id,
            days_encashed=req.days,
            encashment_amount=amount,
            remaining_balance=float(bal.total_balance),
        )

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

    @staticmethod
    def delete_leave_request(db: Session, request_id: int) -> dict:
        req = db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()
        if not req:
            raise ResourceNotFoundException("LeaveRequest", request_id)
        db.delete(req)
        db.commit()
        return {"success": True, "message": f"Leave request {request_id} deleted successfully."}

    @staticmethod
    def delete_leave_type(db: Session, leave_type_id: int) -> dict:
        lt = db.query(LeaveType).filter(LeaveType.id == leave_type_id).first()
        if not lt:
            raise ResourceNotFoundException("LeaveType", leave_type_id)
        db.delete(lt)
        db.commit()
        return {"success": True, "message": f"Leave type {leave_type_id} deleted successfully."}

    @staticmethod
    def delete_holiday(db: Session, holiday_id: int) -> dict:
        h = db.query(Holiday).filter(Holiday.id == holiday_id).first()
        if not h:
            raise ResourceNotFoundException("Holiday", holiday_id)
        db.delete(h)
        db.commit()
        return {"success": True, "message": f"Holiday {holiday_id} deleted successfully."}

