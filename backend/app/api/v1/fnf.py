from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.fnf import FnfCalculateRequest, FnfSettlementResponse
from app.services.fnf_service import FnfService
from app.security.permissions import RequirePermission, get_current_user
from app.models.user import User

router = APIRouter(prefix="/fnf", tags=["Full & Final (F&F) Settlement"])


@router.post("/calculate", response_model=FnfSettlementResponse, status_code=status.HTTP_200_OK)
def calculate_fnf(
    body: FnfCalculateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("payroll.create")),
):
    """Execute Full & Final (F&F) exit settlement calculation engine."""
    return FnfService.calculate_fnf(db, body)


@router.get("/employee/{employee_id}", response_model=FnfSettlementResponse, status_code=status.HTTP_200_OK)
def get_fnf(
    employee_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Fetch Full & Final settlement details for an employee."""
    return FnfService.get_fnf(db, employee_id=employee_id)


@router.post("/{fnf_id}/approve", response_model=FnfSettlementResponse, status_code=status.HTTP_200_OK)
def approve_fnf(
    fnf_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("payroll.approve")),
):
    """Approve Full & Final settlement payout."""
    return FnfService.approve_fnf(db, fnf_id=fnf_id)
