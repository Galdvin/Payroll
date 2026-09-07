import { api } from './api';
import {
  Organization,
  Company,
  Branch,
  Department,
  Designation,
  CostCenter,
} from '../types/organization';

export const organizationService = {
  getOrganizations: async (): Promise<Organization[]> => {
    const res = await api.get<Organization[]>('/organization');
    return res.data;
  },
  createOrganization: async (data: Partial<Organization>): Promise<Organization> => {
    const res = await api.post<Organization>('/organization', data);
    return res.data;
  },

  getCompanies: async (orgId: number = 1): Promise<Company[]> => {
    const res = await api.get<Company[]>(`/organization/companies?organization_id=${orgId}`);
    return res.data;
  },
  createCompany: async (data: Partial<Company>): Promise<Company> => {
    const res = await api.post<Company>('/organization/companies', data);
    return res.data;
  },

  getBranches: async (compId: number = 1): Promise<Branch[]> => {
    const res = await api.get<Branch[]>(`/organization/branches?company_id=${compId}`);
    return res.data;
  },
  createBranch: async (data: Partial<Branch>): Promise<Branch> => {
    const res = await api.post<Branch>('/organization/branches', data);
    return res.data;
  },

  getDepartments: async (compId: number = 1): Promise<Department[]> => {
    const res = await api.get<Department[]>(`/organization/departments?company_id=${compId}`);
    return res.data;
  },
  createDepartment: async (data: Partial<Department>): Promise<Department> => {
    const res = await api.post<Department>('/organization/departments', data);
    return res.data;
  },

  getDesignations: async (compId: number = 1): Promise<Designation[]> => {
    const res = await api.get<Designation[]>(`/organization/designations?company_id=${compId}`);
    return res.data;
  },
  createDesignation: async (data: Partial<Designation>): Promise<Designation> => {
    const res = await api.post<Designation>('/organization/designations', data);
    return res.data;
  },

  getCostCenters: async (compId: number = 1): Promise<CostCenter[]> => {
    const res = await api.get<CostCenter[]>(`/organization/cost-centers?company_id=${compId}`);
    return res.data;
  },
  createCostCenter: async (data: Partial<CostCenter>): Promise<CostCenter> => {
    const res = await api.post<CostCenter>('/organization/cost-centers', data);
    return res.data;
  },
};
