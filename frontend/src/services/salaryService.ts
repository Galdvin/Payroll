import { api } from './api';
import { SalaryComponent, SalaryStructure, EmployeeSalary, SalaryRevision } from '../types/salary';

export const salaryService = {
  getComponents: async (): Promise<SalaryComponent[]> => {
    const res = await api.get<SalaryComponent[]>('/salary/components');
    return res.data;
  },

  createComponent: async (data: Partial<SalaryComponent>): Promise<SalaryComponent> => {
    const res = await api.post<SalaryComponent>('/salary/components', data);
    return res.data;
  },

  getStructures: async (companyId: number = 1): Promise<SalaryStructure[]> => {
    const res = await api.get<SalaryStructure[]>(`/salary/structures?company_id=${companyId}`);
    return res.data;
  },

  assignSalary: async (employeeId: number, totalCtc: number, effectiveDate: string = '2024-01-01'): Promise<EmployeeSalary> => {
    const res = await api.post<EmployeeSalary>('/salary/assign', {
      employee_id: employeeId,
      total_ctc: totalCtc,
      effective_date: effectiveDate,
      currency: 'INR',
    });
    return res.data;
  },

  getEmployeeSalary: async (employeeId: number): Promise<EmployeeSalary> => {
    const res = await api.get<EmployeeSalary>(`/salary/employee/${employeeId}`);
    return res.data;
  },

  reviseSalary: async (employeeId: number, newCtc: number, effectiveDate: string, reason?: string): Promise<SalaryRevision> => {
    const res = await api.post<SalaryRevision>('/salary/revisions', {
      employee_id: employeeId,
      new_ctc: newCtc,
      effective_date: effectiveDate,
      revision_reason: reason,
    });
    return res.data;
  },

  getSalaryRevisions: async (employeeId: number): Promise<SalaryRevision[]> => {
    const res = await api.get<SalaryRevision[]>(`/salary/revisions/${employeeId}`);
    return res.data;
  },
};
