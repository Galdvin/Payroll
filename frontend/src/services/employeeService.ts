import { api } from './api';
import { Employee, EmployeeHistory, EmployeeDocument } from '../types/employee';

export interface GetEmployeesParams {
  organization_id?: number;
  department_id?: number;
  status?: string;
  employment_type?: string;
  search?: string;
  skip?: number;
  limit?: number;
}

export const employeeService = {
  getEmployees: async (params: GetEmployeesParams = {}): Promise<{ items: Employee[]; total: number }> => {
    const res = await api.get<{ items: Employee[]; total: number }>('/employees', { params });
    return res.data;
  },

  getEmployeeById: async (id: number): Promise<Employee> => {
    const res = await api.get<Employee>(`/employees/${id}`);
    return res.data;
  },

  createEmployee: async (data: Partial<Employee>): Promise<Employee> => {
    const res = await api.post<Employee>('/employees', data);
    return res.data;
  },

  updateEmployee: async (id: number, data: Partial<Employee>): Promise<Employee> => {
    const res = await api.put<Employee>(`/employees/${id}`, data);
    return res.data;
  },

  getEmployeeHistory: async (id: number): Promise<EmployeeHistory[]> => {
    const res = await api.get<EmployeeHistory[]>(`/employees/${id}/history`);
    return res.data;
  },

  getEmployeeDocuments: async (id: number): Promise<EmployeeDocument[]> => {
    const res = await api.get<EmployeeDocument[]>(`/employees/${id}/documents`);
    return res.data;
  },

  uploadEmployeeDocument: async (id: number, formData: FormData): Promise<EmployeeDocument> => {
    const res = await api.post<EmployeeDocument>(`/employees/${id}/documents`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
};
