from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.bank_payment import BankFileRequest, JournalEntrySummary
from app.services.bank_adapter_service import BankAdapterService
from app.services.accounting_journal_service import AccountingJournalService
from app.security.permissions import RequirePermission, get_current_user
from app.models.user import User

router = APIRouter(prefix="/payments", tags=["Bank Payments & General Ledger Mappings"])


@router.post("/generate-bank-file", status_code=status.HTTP_200_OK)
def generate_bank_payment_file(
    body: BankFileRequest,
    db: Session = Depends(get_db),
    _: User = Depends(RequirePermission("payroll.process_payment")),
):
    """Generates corporate bank disbursement file (HDFC_CMS, ICICI_CIB, SBI_CMP, ISO20022)."""
    content_bytes, batch, filename = BankAdapterService.generate_bank_payment_file(
        db, payroll_run_id=body.payroll_run_id, bank_format=body.bank_format
    )
    
    media_type = "text/csv" if filename.endswith(".csv") else "text/plain"
    if filename.endswith(".xml"):
        media_type = "application/xml"

    return Response(
        content=content_bytes,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "X-Batch-ID": str(batch.id),
            "X-Checksum-SHA256": batch.checksum_hash,
        },
    )


@router.get("/journal-entries/{run_id}", response_model=JournalEntrySummary, status_code=status.HTTP_200_OK)
def get_journal_entries(
    run_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Retrieves double-entry General Ledger (GL) records for a payroll run."""
    return AccountingJournalService.generate_journal_entries(db, payroll_run_id=run_id)


@router.get("/journal-entries/{run_id}/export", status_code=status.HTTP_200_OK)
def export_journal_entries_csv(
    run_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Exports General Ledger journal entries as CSV for SAP/Tally/QuickBooks."""
    csv_bytes = AccountingJournalService.export_gl_csv(db, payroll_run_id=run_id)
    filename = f"GL_Journal_Entries_Run_{run_id}.csv"
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
