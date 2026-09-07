export interface SalaryComponent {
  id: number;
  name: string;
  code: string;
  component_type: string; // Earning, Deduction
  calculation_type: string; // Fixed, Percentage, Formula
  percentage_base_code?: string;
  percentage_value?: number;
  formula_expression?: string;
  frequency: string;
  is_taxable: boolean;
  is_statutory_applicable: boolean;
  is_prorated: boolean;
  rounding_rule: string;
}

export interface SalaryStructure {
  id: number;
  company_id: number;
  name: string;
  description?: string;
  is_active: boolean;
}

export interface EmployeeSalaryComponent {
  id: number;
  component_id: number;
  monthly_amount: number;
  annual_amount: number;
  component: SalaryComponent;
}

export interface EmployeeSalary {
  id: number;
  employee_id: number;
  salary_structure_id?: number;
  total_ctc: number;
  gross_salary: number;
  net_salary: number;
  effective_date: string;
  currency: string;
  is_active: boolean;
  assigned_components: EmployeeSalaryComponent[];
}

export interface SalaryRevision {
  id: number;
  employee_id: number;
  effective_date: string;
  old_ctc: number;
  new_ctc: number;
  increment_percentage: number;
  revision_reason?: string;
  created_at: string;
}
