import api from './api';
import { AuditLogsResponse, AuditIntegrityResponse } from '../types/audit';

export const auditService = {
  // Fetch audit logs
  getLogs: async (module?: string, action?: string): Promise<AuditLogsResponse> => {
    const params: any = {};
    if (module) params.module = module;
    if (action) params.action = action;
    const res = await api.get('/audit/logs', { params });
    return res.data;
  },

  // Verify SHA-256 chain integrity
  verifyIntegrity: async (): Promise<AuditIntegrityResponse> => {
    const res = await api.get('/audit/verify-integrity');
    return res.data;
  },
};
