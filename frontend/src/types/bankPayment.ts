export type BankFormat = 'HDFC_CMS' | 'ICICI_CIB' | 'SBI_CMP' | 'ISO20022';

export interface BankFileRequest {
  payroll_run_id: number;
  bank_format: BankFormat;
}

export interface JournalEntryResponse {
  id: number;
  payroll_run_id: number;
  entry_date: string;
  account_code: string;
  account_name: string;
  debit_amount: number;
  credit_amount: number;
  narration?: string;
  created_at: string;
}

export interface JournalEntrySummary {
  entries: JournalEntryResponse[];
  total_debit: number;
  total_credit: number;
  is_balanced: boolean;
}
