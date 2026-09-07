import { Department, Designation, Branch } from './organization';

export interface BankDetails {
  bank_name: string;
  account_number: str;
  ifsc_code?: string;
  iban?: string;
  swift_code?: string;
}

export interface Address {
  street: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
}

export interface EmergencyContact {
  name: string;
  relationship: string;
  phone: string;
}

export interface Employee {
  id: number;
  uuid: string;
  employee_code: string;
  first_name: string;
  middle_name?: string;
  last_name: string;
  gender: string;
  date_of_birth: string;
  nationality: string;
  employment_type: string;
  status: string;
  joining_date: string;
  confirmation_date?: string;

  organization_id: number;
  company_id: number;
  branch_id?: number;
  department_id?: number;
  designation_id?: number;
  cost_center_id?: number;
  reporting_manager_id?: number;
  user_id?: number;

  work_email: string;
  personal_email?: string;
  phone?: string;
  emergency_contact?: EmergencyContact;
  address?: Address;

  currency: string;
  bank_details?: BankDetails;
  tax_identifier?: string;
  statutory_identifiers?: Record<string, any>;
  is_active: boolean;

  department?: Department;
  designation?: Designation;
  branch?: Branch;
  created_at: string;
  updated_at: string;
}

export interface EmployeeHistory {
  id: number;
  employee_id: number;
  effective_date: string;
  change_type: string;
  old_values?: Record<string, any>;
  new_values?: Record<string, any>;
  remarks?: string;
  created_at: string;
}

export interface EmployeeDocument {
  id: number;
  employee_id: number;
  document_type: string;
  title: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  version: number;
  expiration_date?: string;
  created_at: string;
}
