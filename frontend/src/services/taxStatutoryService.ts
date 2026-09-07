import { api } from './api';
import { StatutoryRule, TaxRule, TDSEvaluationResult } from '../types/taxStatutory';

export const taxStatutoryService = {
  getStatutoryRules: async (country: string = 'India'): Promise<StatutoryRule[]> => {
    const res = await api.get<StatutoryRule[]>(`/tax-statutory/statutory-rules?country=${country}`);
    return res.data;
  },

  getTaxRules: async (country: string = 'India'): Promise<TaxRule[]> => {
    const res = await api.get<TaxRule[]>(`/tax-statutory/tax-rules?country=${country}`);
    return res.data;
  },

  evaluateTDS: async (grossMonthlySalary: number, regimeName: string = 'New Regime'): Promise<TDSEvaluationResult> => {
    const res = await api.post<TDSEvaluationResult>('/tax-statutory/evaluate-tds', {
      gross_monthly_salary: grossMonthlySalary,
      regime_name: regimeName,
    });
    return res.data;
  },
};
