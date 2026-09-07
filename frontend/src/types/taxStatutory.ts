export interface StatutoryRule {
  id: number;
  country: string;
  rule_code: string;
  name: string;
  employee_rate: number;
  employer_rate: number;
  wage_ceiling?: number;
  monthly_cap?: number;
  eligibility_threshold?: number;
  rule_version: string;
  effective_date: string;
  is_active: boolean;
}

export interface TaxSlab {
  id: number;
  from_income: number;
  to_income?: number;
  tax_rate: number;
}

export interface TaxRule {
  id: number;
  country: string;
  financial_year: string;
  regime_name: string;
  standard_deduction: number;
  cess_rate: number;
  rule_version: string;
  effective_date: string;
  is_active: boolean;
  tax_slabs: TaxSlab[];
}

export interface TDSEvaluationResult {
  annual_gross: number;
  standard_deduction: number;
  taxable_annual: number;
  tax_before_cess: number;
  cess_amount: number;
  total_annual_tax: number;
  monthly_tds: number;
  regime_name: string;
  rule_version: string;
}
