export interface MasterRegisterRow {
  payroll_employee_id: number;
  employee_id: number;
  employee_code: string;
  employee_name: string;
  department: string;
  total_days: number;
  payable_days: number;
  basic: number;
  hra: number;
  transport: number;
  special_allowance: number;
  bonus: number;
  gross_salary: number;
  pf_deduction: number;
  esi_deduction: number;
  tds_deduction: number;
  pt_deduction: number;
  total_deductions: number;
  net_salary: number;
}

export interface MasterRegisterResponse {
  period_id: number;
  payroll_run_id: number;
  period_name: string;
  total_employees: number;
  total_gross: number;
  total_deductions: number;
  total_net: number;
  records: MasterRegisterRow[];
}

export interface CostCenterSummaryRow {
  department: string;
  employee_count: number;
  gross_salary: number;
  total_deductions: number;
  net_salary: number;
  employer_cost: number;
}

export interface PayrollTrendRow {
  period_id: number;
  period_name: string;
  year_month: string;
  total_gross: number;
  total_net: number;
  total_employees: number;
}

export interface ExecutiveAnalyticsResponse {
  total_runs_executed: number;
  total_active_periods: number;
  total_ytd_gross: number;
  total_ytd_net: number;
  total_ytd_deductions: number;
  payroll_trends: PayrollTrendRow[];
}
