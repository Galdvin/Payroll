export interface LeaveBalanceSummary {
  leave_type: string;
  allocated: number;
  used: number;
  remaining: number;
}

export interface EssProfileResponse {
  user_id: number;
  email: string;
  employee_id: number;
  employee_code: string;
  full_name: string;
  department: string;
  designation: string;
  ytd_gross: number;
  ytd_net: number;
  leave_balances: LeaveBalanceSummary[];
  active_loans_count: number;
}

export interface EssPayslipRow {
  payroll_employee_id: number;
  period_id: number;
  period_name: string;
  year_month: string;
  payable_days: number;
  gross_salary: number;
  total_deductions: number;
  net_salary: number;
  pdf_url: string;
}

export interface MssTeamMember {
  employee_id: number;
  employee_code: string;
  name: string;
  department: string;
  designation: string;
  work_email: string;
  employment_status: string;
}

export interface MssPendingLeave {
  id: number;
  employee_id: number;
  employee_name: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  total_days: number;
  reason?: string;
  status: string;
}
