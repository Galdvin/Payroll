from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.reports_service import ReportsService
from app.security.permissions import RequirePermission, get_current_user
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["Payroll Reports & Analytics"])


@router.get("/payroll-register", status_code=status.HTTP_200_OK)
def get_master_payroll_register(
    period_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Retrieves itemized master payroll register data for a pay period."""
    return ReportsService.generate_master_payroll_register(db, period_id=period_id)


@router.get("/pf-ecr/{period_id}", status_code=status.HTTP_200_OK)
def download_pf_ecr_file(
    period_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Generates and streams India PF Electronic Challan cum Return (ECR) text file (#~# formatted)."""
    ecr_bytes = ReportsService.generate_pf_ecr_file(db, period_id=period_id)
    filename = f"PF_ECR_Return_Period_{period_id}.txt"
    return Response(
        content=ecr_bytes,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/cost-center", status_code=status.HTTP_200_OK)
def get_cost_center_breakdown(
    period_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Retrieves Department & Cost Center payroll allocation summary."""
    return ReportsService.generate_cost_center_breakdown(db, period_id=period_id)


@router.get("/executive-analytics", status_code=status.HTTP_200_OK)
def get_executive_analytics(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Retrieves high-level Executive Analytics KPIs and historical payroll trends."""
    return ReportsService.get_executive_analytics(db)
