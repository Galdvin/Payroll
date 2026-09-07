import api from './api';
import {
  Loan,
  LoanRequestCreate,
  Advance,
  AdvanceRequestCreate,
  BonusIncentive,
  BonusIncentiveCreate,
  Reimbursement,
  ReimbursementCreate,
  ReimbursementApprovalRequest,
} from '../types/financialExtras';

export const financialExtrasService = {
  // Loans
  getLoans: async (employeeId?: number): Promise<Loan[]> => {
    const params = employeeId ? { employee_id: employeeId } : {};
    const res = await api.get('/financial-extras/loans', { params });
    return res.data;
  },

  requestLoan: async (data: LoanRequestCreate): Promise<Loan> => {
    const res = await api.post('/financial-extras/loans', data);
    return res.data;
  },

  approveLoan: async (loanId: number): Promise<Loan> => {
    const res = await api.post(`/financial-extras/loans/${loanId}/approve`);
    return res.data;
  },

  // Advances
  getAdvances: async (employeeId?: number): Promise<Advance[]> => {
    const params = employeeId ? { employee_id: employeeId } : {};
    const res = await api.get('/financial-extras/advances', { params });
    return res.data;
  },

  requestAdvance: async (data: AdvanceRequestCreate): Promise<Advance> => {
    const res = await api.post('/financial-extras/advances', data);
    return res.data;
  },

  // Bonuses
  getBonuses: async (employeeId?: number): Promise<BonusIncentive[]> => {
    const params = employeeId ? { employee_id: employeeId } : {};
    const res = await api.get('/financial-extras/bonuses', { params });
    return res.data;
  },

  createBonus: async (data: BonusIncentiveCreate): Promise<BonusIncentive> => {
    const res = await api.post('/financial-extras/bonuses', data);
    return res.data;
  },

  // Reimbursements
  getReimbursements: async (employeeId?: number): Promise<Reimbursement[]> => {
    const params = employeeId ? { employee_id: employeeId } : {};
    const res = await api.get('/financial-extras/reimbursements', { params });
    return res.data;
  },

  createReimbursement: async (data: ReimbursementCreate): Promise<Reimbursement> => {
    const res = await api.post('/financial-extras/reimbursements', data);
    return res.data;
  },

  approveReimbursement: async (reimbId: number, data: ReimbursementApprovalRequest): Promise<Reimbursement> => {
    const res = await api.post(`/financial-extras/reimbursements/${reimbId}/approve`, data);
    return res.data;
  },
};
