from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PayrollApprovalAction(BaseModel):
    action: str  # APPROVE, REJECT
    remarks: Optional[str] = None


class PayrollApprovalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    payroll_run_id: int
    stage: str
    status: str
    approver_id: Optional[int] = None
    remarks: Optional[str] = None
    created_at: datetime
