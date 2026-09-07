import api from './api';
import { BankFileRequest, JournalEntrySummary } from '../types/bankPayment';

export const bankPaymentService = {
  // Generate & download bank disbursement file
  generateBankFile: async (data: BankFileRequest): Promise<{ blob: Blob; filename: string }> => {
    const res = await api.post('/payments/generate-bank-file', data, {
      responseType: 'blob',
    });
    
    // Extract filename from disposition header if available
    let filename = `Salaries_${data.bank_format}.txt`;
    const disposition = res.headers['content-disposition'];
    if (disposition && disposition.includes('filename=')) {
      filename = disposition.split('filename=')[1].replace(/"/g, '');
    }

    return { blob: res.data, filename };
  },

  // Fetch GL Journal Entries
  getJournalEntries: async (runId: number): Promise<JournalEntrySummary> => {
    const res = await api.get(`/payments/journal-entries/${runId}`);
    return res.data;
  },

  // Export GL entries CSV
  exportJournalCsv: async (runId: number): Promise<Blob> => {
    const res = await api.get(`/payments/journal-entries/${runId}/export`, {
      responseType: 'blob',
    });
    return res.data;
  },
};
