import { api } from './api';
import { LeaveType, LeaveBalance, LeaveRequest, Holiday } from '../types/leave';

export const leaveService = {
  getLeaveTypes: async (): Promise<LeaveType[]> => {
    const res = await api.get<LeaveType[]>('/leaves/types');
    return res.data;
  },

  getLeaveBalances: async (employeeId: number, year: number = 2024): Promise<LeaveBalance[]> => {
    const res = await api.get<LeaveBalance[]>('/leaves/balances', {
      params: { employee_id: employeeId, year },
    });
    return res.data;
  },

  applyLeave: async (data: { employee_id: number; leave_type_id: number; start_date: string; end_date: string; reason?: string }): Promise<LeaveRequest> => {
    const res = await api.post<LeaveRequest>('/leaves/requests', data);
    return res.data;
  },

  getLeaveRequests: async (employeeId?: number): Promise<LeaveRequest[]> => {
    const res = await api.get<LeaveRequest[]>('/leaves/requests', {
      params: { employee_id: employeeId },
    });
    return res.data;
  },

  approveLeave: async (requestId: number, status: 'Approved' | 'Rejected', comments?: string): Promise<LeaveRequest> => {
    const res = await api.post<LeaveRequest>(`/leaves/requests/${requestId}/approve`, {
      status,
      approval_comments: comments,
    });
    return res.data;
  },

  getHolidays: async (companyId: number = 1): Promise<Holiday[]> => {
    const res = await api.get<Holiday[]>(`/leaves/holidays?company_id=${companyId}`);
    return res.data;
  },
};
