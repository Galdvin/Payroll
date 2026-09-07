import { Employee } from './employee';

export interface PayrollPeriod {
  id: number;
  company_id: number;
  name: string;
  year_month: string;
  start_date: string;
  end_date: string;
  cutoff_date: string;
  status: string;
}

export interface PayrollEarning {
  id: number;
  component_code: string;
  name: string;
  full_amount: number;
  prorated_amount: number;
}

export interface PayrollDeduction {
  id: number;
  component_code: string;
  name: string;
  amount: number;
}

export interface PayrollEmployee {
  id: number;
  payroll_run_id: number;
  employee_id: number;
  total_days: number;
  payable_days: number;
  gross_salary: number;
  taxable_income: number;
  employee_statutory: number;
  employer_statutory: number;
  total_deductions: number;
  net_salary: number;
  employer_cost: number;
  calculation_trace: Record<string, any>;
  employee?: Employee;
  earnings: PayrollEarning[];
  deductions: PayrollDeduction[];
}

export interface PayrollRun {
  id: number;
  payroll_period_id: number;
  total_employees: number;
  total_gross: number;
  total_deductions: number;
  total_net: number;
  total_employer_cost: number;
  status: string;
  executed_by_user_id?: number;
  payroll_period: PayrollPeriod;
  employee_results: PayrollEmployee[];
}
