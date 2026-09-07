import api from './api';
import {
  EssProfileResponse,
  EssPayslipRow,
  MssTeamMember,
  MssPendingLeave,
} from '../types/selfService';

export const selfService = {
  // ESS Profile
  getEssProfile: async (): Promise<EssProfileResponse> => {
    const res = await api.get('/self-service/ess/me');
    return res.data;
  },

  // ESS My Payslips
  getMyPayslips: async (): Promise<EssPayslipRow[]> => {
    const res = await api.get('/self-service/ess/my-payslips');
    return res.data;
  },

  // MSS Team
  getTeamMembers: async (): Promise<MssTeamMember[]> => {
    const res = await api.get('/self-service/mss/team');
    return res.data;
  },

  // MSS Pending Leaves
  getPendingTeamLeaves: async (): Promise<MssPendingLeave[]> => {
    const res = await api.get('/self-service/mss/team-leaves');
    return res.data;
  },
};
