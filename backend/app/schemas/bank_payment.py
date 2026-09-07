from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class BankFileRequest(BaseModel):
    payroll_run_id: int
    bank_format: str  # HDFC_CMS, ICICI_CIB, SBI_CMP, ISO20022


class BankPaymentBatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    payroll_run_id: int
    bank_format: str
    total_records: int
    total_amount: float
    checksum_hash: str
    status: str
    created_at: datetime


class JournalEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    payroll_run_id: int
    entry_date: date
    account_code: str
    account_name: str
    debit_amount: float
    credit_amount: float
    narration: Optional[str] = None
    created_at: datetime


class JournalEntrySummary(BaseModel):
    entries: List[JournalEntryResponse]
    total_debit: float
    total_credit: float
    is_balanced: bool
