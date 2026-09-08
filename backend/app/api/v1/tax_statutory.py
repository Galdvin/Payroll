from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.tax_statutory import (
    StatutoryRuleResponse,
    TaxRuleResponse,
    EvaluateTDSRequest,
)
from app.services.statutory_engine_service import StatutoryEngineService
from app.security.permissions import RequirePermission, get_current_user
from app.models.user import User

router = APIRouter(prefix="/tax-statutory", tags=["Tax & Statutory Engine"])


@router.get("/statutory-rules", response_model=List[StatutoryRuleResponse], status_code=status.HTTP_200_OK)
def list_statutory_rules(country: str = "India", db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return StatutoryEngineService.get_statutory_rules(db, country=country)


@router.get("/tax-rules", response_model=List[TaxRuleResponse], status_code=status.HTTP_200_OK)
def list_tax_rules(country: str = "India", db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return StatutoryEngineService.get_tax_rules(db, country=country)


@router.post("/evaluate-tds", status_code=status.HTTP_200_OK)
def evaluate_tds(body: EvaluateTDSRequest, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Evaluate Income Tax TDS calculation and return step-by-step slab breakdown."""
    return StatutoryEngineService.calculate_tds_tax(db, gross_monthly=body.gross_monthly_salary, regime_name=body.regime_name)


@router.delete("/statutory-rules/{rule_id}", status_code=status.HTTP_200_OK)
def delete_statutory_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("payroll.lock")),
):
    return StatutoryEngineService.delete_statutory_rule(db, rule_id)


@router.delete("/tax-rules/{rule_id}", status_code=status.HTTP_200_OK)
def delete_tax_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("payroll.lock")),
):
    return StatutoryEngineService.delete_tax_rule(db, rule_id)


@router.delete("/tax-slabs/{slab_id}", status_code=status.HTTP_200_OK)
def delete_tax_slab(
    slab_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("payroll.lock")),
):
    return StatutoryEngineService.delete_tax_slab(db, slab_id)
