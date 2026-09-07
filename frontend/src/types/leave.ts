export interface LeaveType {
  id: number;
  name: string;
  code: string;
  is_paid: boolean;
  is_encashable: boolean;
  requires_approval: boolean;
}

export interface LeaveBalance {
  id: number;
  employee_id: number;
  leave_type_id: number;
  year: number;
  accrued: number;
  used: number;
  pending: number;
  total_balance: number;
  leave_type: LeaveType;
}

export interface LeaveRequest {
  id: number;
  employee_id: number;
  leave_type_id: number;
  start_date: string;
  end_date: string;
  total_days: number;
  reason?: string;
  status: string;
  approved_by_user_id?: number;
  approval_comments?: string;
  leave_type: LeaveType;
}

export interface Holiday {
  id: number;
  company_id: number;
  branch_id?: number;
  name: string;
  date: string;
  holiday_type: string;
  is_optional: boolean;
}
