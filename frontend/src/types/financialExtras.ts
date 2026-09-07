export type LoanStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'DISBURSED' | 'CLOSED';
export type AdvanceStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'RECOVERED';
export type BonusType = 'PERFORMANCE' | 'FESTIVAL' | 'RETENTION' | 'COMMISSION' | 'OTHER';
export type ReimbursementStatus = 'SUBMITTED' | 'APPROVED' | 'PARTIALLY_APPROVED' | 'REJECTED' | 'PAID';
export type ExpenseCategory = 'TRAVEL' | 'MEALS' | 'SUPPLIES' | 'INTERNET' | 'TRAINING' | 'OTHER';

export interface Loan {
  id: number;
  employee_id: number;
  principal_amount: number;
  interest_rate_annual: number;
  tenure_months: number;
  monthly_emi: number;
  remaining_balance: number;
  disbursement_date?: string;
  status: LoanStatus;
  reason?: string;
  created_at: string;
}

export interface LoanRequestCreate {
  employee_id: number;
  principal_amount: number;
  interest_rate_annual?: number;
  tenure_months: number;
  disbursement_date?: string;
  reason?: string;
}

export interface Advance {
  id: number;
  employee_id: number;
  amount: number;
  request_date: string;
  recovery_payroll_period_id?: number;
  status: AdvanceStatus;
  reason?: string;
  created_at: string;
}

export interface AdvanceRequestCreate {
  employee_id: number;
  amount: number;
  request_date?: string;
  recovery_payroll_period_id?: number;
  reason?: string;
}

export interface BonusIncentive {
  id: number;
  employee_id: number;
  payroll_period_id?: number;
  bonus_type: BonusType;
  amount: number;
  is_taxable: boolean;
  remarks?: string;
  created_at: string;
}

export interface BonusIncentiveCreate {
  employee_id: number;
  payroll_period_id?: number;
  bonus_type: BonusType;
  amount: number;
  is_taxable?: boolean;
  remarks?: string;
}

export interface ReimbursementItem {
  id: number;
  reimbursement_id: number;
  expense_category: ExpenseCategory;
  amount: number;
  description?: string;
  receipt_url?: string;
}

export interface ReimbursementItemCreate {
  expense_category: ExpenseCategory;
  amount: number;
  description?: string;
  receipt_url?: string;
}

export interface Reimbursement {
  id: number;
  employee_id: number;
  payroll_period_id?: number;
  total_amount: number;
  approved_amount: number;
  status: ReimbursementStatus;
  claim_date: string;
  approval_remarks?: string;
  items: ReimbursementItem[];
  created_at: string;
}

export interface ReimbursementCreate {
  employee_id: number;
  payroll_period_id?: number;
  claim_date?: string;
  items: ReimbursementItemCreate[];
}

export interface ReimbursementApprovalRequest {
  status: ReimbursementStatus;
  approved_amount?: number;
  remarks?: string;
}
