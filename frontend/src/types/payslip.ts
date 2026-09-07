export interface PayrollApprovalAction {
  action: 'APPROVE' | 'REJECT';
  remarks?: string;
}

export interface PayrollApprovalResponse {
  id: number;
  payroll_run_id: number;
  stage: string;
  status: string;
  approver_id?: number;
  remarks?: string;
  created_at: string;
}
