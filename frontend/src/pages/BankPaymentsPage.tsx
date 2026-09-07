import React, { useEffect, useState } from 'react';
import {
  CreditCard,
  Download,
  Building2,
  CheckCircle2,
  FileSpreadsheet,
  AlertCircle,
  Hash,
  Scale,
} from 'lucide-react';
import { payrollService } from '../services/payrollService';
import { bankPaymentService } from '../services/bankPaymentService';
import { PayrollPeriod, PayrollRun } from '../types/payroll';
import { BankFormat, JournalEntrySummary } from '../types/bankPayment';

export const BankPaymentsPage: React.FC = () => {
  const [periods, setPeriods] = useState<PayrollPeriod[]>([]);
  const [selectedPeriodId, setSelectedPeriodId] = useState<number | null>(null);
  const [currentRun, setCurrentRun] = useState<PayrollRun | null>(null);
  const [selectedBankFormat, setSelectedBankFormat] = useState<BankFormat>('HDFC_CMS');
  const [glSummary, setGlSummary] = useState<JournalEntrySummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPeriods();
  }, []);

  useEffect(() => {
    if (selectedPeriodId) {
      loadRunDetails(selectedPeriodId);
    }
  }, [selectedPeriodId]);

  const loadPeriods = async () => {
    try {
      const data = await payrollService.getPeriods();
      setPeriods(data);
      if (data.length > 0) {
        setSelectedPeriodId(data[0].id);
      }
    } catch (err: any) {
      setError('Failed to fetch payroll periods');
    }
  };

  const loadRunDetails = async (periodId: number) => {
    setLoading(true);
    setError(null);
    try {
      const runs = await payrollService.getRuns(periodId);
      if (runs.length > 0) {
        const run = runs[0];
        setCurrentRun(run);
        // Load GL Journal Entries
        const gl = await bankPaymentService.getJournalEntries(run.id);
        setGlSummary(gl);
      } else {
        setCurrentRun(null);
        setGlSummary(null);
      }
    } catch (err: any) {
      setError(err?.response?.data?.message || 'Failed to load run details');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateBankFile = async () => {
    if (!currentRun) return;
    try {
      const { blob, filename } = await bankPaymentService.generateBankFile({
        payroll_run_id: currentRun.id,
        bank_format: selectedBankFormat,
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err: any) {
      alert(err?.response?.data?.message || 'Failed to generate bank payment file');
    }
  };

  const handleExportGlCsv = async () => {
    if (!currentRun) return;
    try {
      const blob = await bankPaymentService.exportJournalCsv(currentRun.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `GL_Journal_Entries_Run_${currentRun.id}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err: any) {
      alert('Failed to export GL entries');
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner Header */}
      <div className="flex justify-between items-center bg-slate-800/60 p-6 rounded-2xl border border-slate-700/50 backdrop-blur-md">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-3">
            <CreditCard className="w-8 h-8 text-emerald-400" />
            Bank Payment Adapters & GL Accounting
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Generate corporate salary disbursement batch files (HDFC, ICICI, SBI, ISO20022) and export double-entry General Ledger journal mappings.
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Pay Period Selector */}
          <select
            value={selectedPeriodId || ''}
            onChange={(e) => setSelectedPeriodId(Number(e.target.value))}
            className="bg-slate-800 border border-slate-700 text-slate-100 px-4 py-2 rounded-xl text-sm font-medium focus:outline-none focus:border-emerald-500"
          >
            {periods.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.year_month})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Bank File Generator Card */}
      {currentRun && (
        <div className="bg-slate-800/40 p-6 rounded-2xl border border-slate-700/50 space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-lg font-bold text-slate-200 flex items-center gap-2">
                <Building2 className="w-5 h-5 text-emerald-400" /> Corporate Bank Salary Disbursement
              </h2>
              <p className="text-slate-400 text-xs mt-0.5">
                Select target bank adapter format to generate encrypted corporate payment file payload.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <select
                value={selectedBankFormat}
                onChange={(e) => setSelectedBankFormat(e.target.value as BankFormat)}
                className="bg-slate-900 border border-slate-700 text-slate-100 px-4 py-2 rounded-xl text-sm font-semibold focus:border-emerald-500"
              >
                <option value="HDFC_CMS">HDFC Bank CMS Format (.txt)</option>
                <option value="ICICI_CIB">ICICI Bank CIB NetBanking (.csv)</option>
                <option value="SBI_CMP">SBI Corporate CMP Format (.txt)</option>
                <option value="ISO20022">ISO 20022 XML Format (.xml)</option>
              </select>
              <button
                onClick={handleGenerateBankFile}
                className="bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-2 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 shadow-lg shadow-emerald-600/20"
              >
                <Download className="w-4 h-4" /> Download Payment File
              </button>
            </div>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-700/80">
              <div className="text-slate-400 text-xs font-medium">Total Net Disbursement</div>
              <div className="text-xl font-bold text-emerald-400 mt-1">₹{currentRun.total_net.toLocaleString()}</div>
            </div>
            <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-700/80">
              <div className="text-slate-400 text-xs font-medium">Beneficiary Count</div>
              <div className="text-xl font-bold text-slate-100 mt-1">{currentRun.total_employees} Employees</div>
            </div>
            <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-700/80">
              <div className="text-slate-400 text-xs font-medium">Security Validation</div>
              <div className="text-xs font-mono text-emerald-400 flex items-center gap-1 mt-2">
                <Hash className="w-3.5 h-3.5" /> SHA-256 Checksum Active
              </div>
            </div>
          </div>
        </div>
      )}

      {/* General Ledger (GL) Double-Entry Journal Audit Table */}
      {loading ? (
        <div className="p-12 text-center text-slate-400">Loading accounting entries...</div>
      ) : error ? (
        <div className="p-4 bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl flex items-center gap-3">
          <AlertCircle className="w-5 h-5" /> {error}
        </div>
      ) : glSummary ? (
        <div className="bg-slate-800/40 rounded-2xl border border-slate-700/50 overflow-hidden space-y-4 p-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-lg font-bold text-slate-200 flex items-center gap-2">
                <Scale className="w-5 h-5 text-blue-400" /> Double-Entry General Ledger (GL) Journal
              </h2>
              <p className="text-slate-400 text-xs mt-0.5">
                Automated accounting entry mapping with strict Debit = Credit equilibrium enforcement.
              </p>
            </div>
            <div className="flex items-center gap-3">
              {glSummary.is_balanced ? (
                <span className="px-3 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-xl text-xs font-bold flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Double-Entry Balanced
                </span>
              ) : (
                <span className="px-3 py-1 bg-red-500/10 text-red-400 border border-red-500/30 rounded-xl text-xs font-bold">
                  Unbalanced Entry
                </span>
              )}
              <button
                onClick={handleExportGlCsv}
                className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 shadow-lg shadow-blue-600/20"
              >
                <FileSpreadsheet className="w-4 h-4" /> Export CSV / SAP
              </button>
            </div>
          </div>

          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-800/80 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-700">
                <th className="p-3">Entry Date</th>
                <th className="p-3">Account Code</th>
                <th className="p-3">Account Name</th>
                <th className="p-3 text-right">Debit (INR)</th>
                <th className="p-3 text-right">Credit (INR)</th>
                <th className="p-3">Narration</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50 text-sm text-slate-200">
              {glSummary.entries.map((entry) => (
                <tr key={entry.id} className="hover:bg-slate-700/20 transition-all">
                  <td className="p-3 text-slate-400 text-xs font-mono">{entry.entry_date}</td>
                  <td className="p-3 font-mono text-sky-400 font-medium">{entry.account_code}</td>
                  <td className="p-3 font-semibold text-slate-200">{entry.account_name}</td>
                  <td className="p-3 text-right font-mono text-emerald-400 font-medium">
                    {entry.debit_amount > 0 ? `₹${entry.debit_amount.toLocaleString()}` : '-'}
                  </td>
                  <td className="p-3 text-right font-mono text-blue-400 font-medium">
                    {entry.credit_amount > 0 ? `₹${entry.credit_amount.toLocaleString()}` : '-'}
                  </td>
                  <td className="p-3 text-slate-400 text-xs">{entry.narration || 'N/A'}</td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="bg-slate-900/80 font-bold border-t border-slate-700 text-slate-100">
                <td colSpan={3} className="p-4 uppercase text-xs tracking-wider">
                  Total Accounting Journal Balance
                </td>
                <td className="p-4 text-right font-mono text-emerald-400">₹{glSummary.total_debit.toLocaleString()}</td>
                <td className="p-4 text-right font-mono text-blue-400">₹{glSummary.total_credit.toLocaleString()}</td>
                <td className="p-4 text-xs font-mono text-emerald-400">
                  {glSummary.is_balanced ? '✓ EQUILIBRIUM OK' : '✗ DISCREPANCY'}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      ) : null}
    </div>
  );
};
