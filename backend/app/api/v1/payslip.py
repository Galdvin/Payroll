from typing import List
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.payroll_run import PayrollRun, PayrollEmployee
from app.models.payroll_approval import PayrollApproval
from app.schemas.payroll_approval import PayrollApprovalAction, PayrollApprovalResponse
from app.services.payslip_pdf_service import PayslipPDFService
from app.security.permissions import RequirePermission, get_current_user
from app.models.user import User
from app.core.exceptions import PayrollException

router = APIRouter(prefix="/payslips", tags=["Payslips & Approval Workflow"])


# --- PDF Generation & Downloads ---
@router.get("/employee/{employee_id}/period/{period_id}/pdf", status_code=status.HTTP_200_OK)
def get_employee_payslip_pdf(
    employee_id: int,
    period_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Generates and streams individual PDF payslip for an employee."""
    payroll_emp = (
        db.query(PayrollEmployee)
        .join(PayrollRun)
        .filter(
            PayrollEmployee.employee_id == employee_id,
            PayrollRun.payroll_period_id == period_id,
        )
        .first()
    )
    if not payroll_emp:
        raise PayrollException("PAYSLIP_NOT_FOUND", "Payslip record not found for this employee and period")

    pdf_bytes = PayslipPDFService.generate_payslip_pdf(db, payroll_emp)
    filename = f"Payslip_EMP{employee_id}_Period{period_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={filename}"},
    )


@router.get("/run/{run_id}/bulk-zip", status_code=status.HTTP_200_OK)
def get_bulk_payslips_zip(
    run_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("payroll.approve")),
):
    """Generates and streams a ZIP archive of all employee payslips for a payroll run."""
    zip_bytes = PayslipPDFService.generate_bulk_payslips_zip(db, run_id)
    filename = f"Bulk_Payslips_Run_{run_id}.zip"
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# --- Multi-Tier Approval Workflow ---
@router.post("/run/{run_id}/approve", response_model=PayrollApprovalResponse, status_code=status.HTTP_200_OK)
def approve_payroll_run(
    run_id: int,
    body: PayrollApprovalAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll.approve")),
):
    """Executes multi-tier approval transition for a payroll run."""
    run = db.query(PayrollRun).filter(PayrollRun.id == run_id).first()
    if not run:
        raise PayrollException("RUN_NOT_FOUND", f"Payroll run {run_id} not found")

    if run.status == "Locked":
        raise PayrollException("RUN_ALREADY_LOCKED", "Payroll run is already locked and finalized")

    # Determine next stage transition
    old_status = run.status
    if body.action.upper() == "REJECT":
        run.status = "Draft"
        new_stage = "REJECTED_TO_DRAFT"
    else:
        if run.status in ["Draft", "Calculated"]:
            run.status = "Manager Approved"
            new_stage = "MANAGER_REVIEW"
        elif run.status == "Manager Approved":
            run.status = "Finance Approved"
            new_stage = "FINANCE_AUDIT"
        elif run.status == "Finance Approved":
            run.status = "Locked"
            new_stage = "ORG_ADMIN_LOCK"
        else:
            run.status = "Locked"
            new_stage = "FINAL_LOCK"

    approval = PayrollApproval(
        payroll_run_id=run_id,
        stage=new_stage,
        status="APPROVED" if body.action.upper() == "APPROVE" else "REJECTED",
        approver_id=current_user.id,
        remarks=body.remarks or f"Transitioned from {old_status} to {run.status}",
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval


@router.get("/run/{run_id}/approvals", response_model=List[PayrollApprovalResponse], status_code=status.HTTP_200_OK)
def get_payroll_run_approvals(
    run_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Fetches approval history log for a given payroll run."""
    return db.query(PayrollApproval).filter(PayrollApproval.payroll_run_id == run_id).order_by(PayrollApproval.created_at.desc()).all()
