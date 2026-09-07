export interface Permission {
  id: number;
  code: string;
  module: string;
  description?: string;
}

export interface Role {
  id: number;
  name: string;
  description?: string;
  is_system_role: boolean;
  permissions: Permission[];
}

export interface User {
  id: number;
  uuid: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  organization_id?: number;
  company_id?: number;
  roles: Role[];
  created_at: string;
  updated_at: string;
}
