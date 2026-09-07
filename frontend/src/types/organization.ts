export interface Organization {
  id: number;
  name: string;
  code: string;
  tax_identifier?: string;
  currency: string;
  country: string;
}

export interface Company {
  id: number;
  organization_id: number;
  name: string;
  code: string;
  registration_number?: string;
  logo_url?: string;
}

export interface Branch {
  id: number;
  company_id: number;
  name: string;
  code: string;
  address?: string;
  city?: string;
  state?: string;
  country: string;
  timezone: string;
}

export interface Department {
  id: number;
  company_id: number;
  parent_department_id?: number;
  name: string;
  code: string;
}

export interface Designation {
  id: number;
  company_id: number;
  title: string;
  code: string;
  grade?: string;
}

export interface CostCenter {
  id: number;
  company_id: number;
  name: string;
  code: string;
  budget_allocation?: number;
}
