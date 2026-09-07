import api from './api';
import { PayrollApprovalAction, PayrollApprovalResponse } from '../types/payslip';

export const payslipService = {
  // Download single PDF as blob
  downloadEmployeePayslipPdf: async (employeeId: number, periodId: number): Promise<Blob> => {
    const res = await api.get(`/payslips/employee/${employeeId}/period/${periodId}/pdf`, {
      responseType: 'blob',
    });
    return res.data;
  },

  // Download bulk ZIP as blob
  downloadBulkPayslipsZip: async (runId: number): Promise<Blob> => {
    const res = await api.get(`/payslips/run/${runId}/bulk-zip`, {
      responseType: 'blob',
    });
    return res.data;
  },

  // Submit approval step
  approvePayrollRun: async (runId: number, data: PayrollApprovalAction): Promise<PayrollApprovalResponse> => {
    const res = await api.post(`/payslips/run/${runId}/approve`, data);
    return res.data;
  },

  // Fetch approval history log
  getApprovalLog: async (runId: number): Promise<PayrollApprovalResponse[]> => {
    const res = await api.get(`/payslips/run/${runId}/approvals`);
    return res.data;
  },
};
