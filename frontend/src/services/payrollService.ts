import { api } from './api';
import { PayrollPeriod, PayrollRun } from '../types/payroll';

export const payrollService = {
  getPeriods: async (): Promise<PayrollPeriod[]> => {
    const res = await api.get<PayrollPeriod[]>('/payroll/periods');
    return res.data;
  },

  calculatePayroll: async (periodId: number): Promise<PayrollRun> => {
    const res = await api.post<PayrollRun>('/payroll/calculate', { payroll_period_id: periodId });
    return res.data;
  },

  getPayrollRun: async (runId: number): Promise<PayrollRun> => {
    const res = await api.get<PayrollRun>(`/payroll/runs/${runId}`);
    return res.data;
  },

  getCalculationTrace: async (runId: number, employeeId: number): Promise<Record<string, any>> => {
    const res = await api.get<Record<string, any>>(`/payroll/runs/${runId}/trace/${employeeId}`);
    return res.data;
  },

  approvePayroll: async (runId: number): Promise<PayrollRun> => {
    const res = await api.post<PayrollRun>(`/payroll/runs/${runId}/approve`);
    return res.data;
  },

  lockPayroll: async (runId: number): Promise<PayrollRun> => {
    const res = await api.post<PayrollRun>(`/payroll/runs/${runId}/lock`);
    return res.data;
  },
};
