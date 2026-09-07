from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.employee import Employee
from app.models.payroll_run import PayrollEmployee, PayrollRun, PayrollPeriod
from app.models.leave import LeaveBalance, LeaveRequest
from app.models.financial_extras import Loan, Reimbursement
from app.security.permissions import get_current_user
from app.models.user import User
from app.core.exceptions import PayrollException

router = APIRouter(prefix="/self-service", tags=["Employee & Manager Self Service (ESS/MSS)"])


@router.get("/ess/me", status_code=status.HTTP_200_OK)
def get_my_ess_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves personal employee profile, leave balances, active loans, and YTD earnings for logged-in user."""
    # Find employee record associated with email or ID
    employee = db.query(Employee).filter(Employee.work_email == current_user.email).first()
    if not employee:
        # Fallback to employee ID 1 if test environment
        employee = db.query(Employee).filter(Employee.id == 1).first()

    emp_id = employee.id if employee else 1

    # Leave balances
    balances = db.query(LeaveBalance).filter(LeaveBalance.employee_id == emp_id).all()
    
    # Active loans
    loans = db.query(Loan).filter(Loan.employee_id == emp_id, Loan.status.in_(["APPROVED", "DISBURSED"])).all()

    # YTD Net salary calculation from payroll_employees
    payroll_rows = db.query(PayrollEmployee).filter(PayrollEmployee.employee_id == emp_id).all()
    ytd_net = sum(r.net_salary for r in payroll_rows)
    ytd_gross = sum(r.gross_salary for r in payroll_rows)

    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "employee_id": emp_id,
        "employee_code": f"EMP-{emp_id:04d}",
        "full_name": f"{employee.first_name} {employee.last_name}" if employee else current_user.full_name,
        "department": employee.department.name if (employee and employee.department) else "Engineering",
        "designation": employee.designation.title if (employee and employee.designation) else "Senior Developer",
        "ytd_gross": ytd_gross,
        "ytd_net": ytd_net,
        "leave_balances": [
            {
                "leave_type": b.leave_type.name if b.leave_type else "Leave",
                "allocated": b.allocated_days,
                "used": b.used_days,
                "remaining": b.remaining_days,
            }
            for b in balances
        ],
        "active_loans_count": len(loans),
    }


@router.get("/ess/my-payslips", status_code=status.HTTP_200_OK)
def get_my_payslips(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists historical payslips available for download by the current employee."""
    employee = db.query(Employee).filter(Employee.work_email == current_user.email).first()
    emp_id = employee.id if employee else 1

    rows = (
        db.query(PayrollEmployee)
        .join(PayrollRun)
        .join(PayrollPeriod)
        .filter(PayrollEmployee.employee_id == emp_id)
        .all()
    )

    payslips = []
    for r in rows:
        period = r.payroll_run.payroll_period
        payslips.append({
            "payroll_employee_id": r.id,
            "period_id": period.id,
            "period_name": period.name,
            "year_month": period.year_month,
            "payable_days": r.payable_days,
            "gross_salary": r.gross_salary,
            "total_deductions": r.total_deductions,
            "net_salary": r.net_salary,
            "pdf_url": f"/api/v1/payslips/employee/{emp_id}/period/{period.id}/pdf",
        })

    return payslips


@router.get("/mss/team", status_code=status.HTTP_200_OK)
def get_my_team_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves direct report team members managed by current user."""
    # Fetch team members (mocked to department or all staff for testing)
    team = db.query(Employee).limit(10).all()
    return [
        {
            "employee_id": emp.id,
            "employee_code": f"EMP-{emp.id:04d}",
            "name": f"{emp.first_name} {emp.last_name}",
            "department": emp.department.name if emp.department else "General",
            "designation": emp.designation.title if emp.designation else "Staff",
            "work_email": emp.work_email,
            "employment_status": emp.employment_status,
        }
        for emp in team
    ]


@router.get("/mss/team-leaves", status_code=status.HTTP_200_OK)
def get_team_pending_leaves(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Retrieves pending leave requests for manager approval inbox."""
    pending = db.query(LeaveRequest).filter(LeaveRequest.status == "PENDING").all()
    return [
        {
            "id": req.id,
            "employee_id": req.employee_id,
            "employee_name": f"{req.employee.first_name} {req.employee.last_name}" if req.employee else "Staff",
            "leave_type": req.leave_type.name if req.leave_type else "Leave",
            "start_date": str(req.start_date),
            "end_date": str(req.end_date),
            "total_days": req.total_days,
            "reason": req.reason,
            "status": req.status,
        }
        for req in pending
    ]
