import api from './api';
import {
  MasterRegisterResponse,
  CostCenterSummaryRow,
  ExecutiveAnalyticsResponse,
} from '../types/reports';

export const reportsService = {
  // Master Payroll Register
  getMasterRegister: async (periodId: number): Promise<MasterRegisterResponse> => {
    const res = await api.get('/reports/payroll-register', { params: { period_id: periodId } });
    return res.data;
  },

  // Download PF ECR Return Text File
  downloadPfEcrFile: async (periodId: number): Promise<Blob> => {
    const res = await api.get(`/reports/pf-ecr/${periodId}`, { responseType: 'blob' });
    return res.data;
  },

  // Department & Cost Center breakdown
  getCostCenterBreakdown: async (periodId: number): Promise<CostCenterSummaryRow[]> => {
    const res = await api.get('/reports/cost-center', { params: { period_id: periodId } });
    return res.data;
  },

  // Executive Analytics KPIs
  getExecutiveAnalytics: async (): Promise<ExecutiveAnalyticsResponse> => {
    const res = await api.get('/reports/executive-analytics');
    return res.data;
  },
};
