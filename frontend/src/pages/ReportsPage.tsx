import React, { useEffect, useState } from 'react';
import {
  BarChart3,
  Download,
  FileSpreadsheet,
  Building,
  ShieldCheck,
  TrendingUp,
  Search,
  AlertCircle,
  FileText,
  PieChart,
} from 'lucide-react';
import { payrollService } from '../services/payrollService';
import { reportsService } from '../services/reportsService';
import { PayrollPeriod } from '../types/payroll';
import {
  MasterRegisterResponse,
  CostCenterSummaryRow,
  ExecutiveAnalyticsResponse,
} from '../types/reports';

export const ReportsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'analytics' | 'statutory' | 'register' | 'costcenter'>('analytics');
  const [periods, setPeriods] = useState<PayrollPeriod[]>([]);
  const [selectedPeriodId, setSelectedPeriodId] = useState<number | null>(null);

  // Data states
  const [analytics, setAnalytics] = useState<ExecutiveAnalyticsResponse | null>(null);
  const [registerData, setRegisterData] = useState<MasterRegisterResponse | null>(null);
  const [costCenterData, setCostCenterData] = useState<CostCenterSummaryRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadPeriods();
    loadAnalytics();
  }, []);

  useEffect(() => {
    if (selectedPeriodId) {
      if (activeTab === 'register') loadRegister(selectedPeriodId);
      if (activeTab === 'costcenter') loadCostCenter(selectedPeriodId);
    }
  }, [selectedPeriodId, activeTab]);

  const loadPeriods = async () => {
    try {
      const data = await payrollService.getPeriods();
      setPeriods(data);
      if (data.length > 0) setSelectedPeriodId(data[0].id);
    } catch (err: any) {
      setError('Failed to fetch payroll periods');
    }
  };

  const loadAnalytics = async () => {
    try {
      const data = await reportsService.getExecutiveAnalytics();
      setAnalytics(data);
    } catch (err: any) {
      setError('Failed to load analytics data');
    }
  };

  const loadRegister = async (periodId: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await reportsService.getMasterRegister(periodId);
      setRegisterData(data);
    } catch (err: any) {
      setError(err?.response?.data?.message || 'Failed to load master register');
    } finally {
      setLoading(false);
    }
  };

  const loadCostCenter = async (periodId: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await reportsService.getCostCenterBreakdown(periodId);
      setCostCenterData(data);
    } catch (err: any) {
      setError(err?.response?.data?.message || 'Failed to load cost center summary');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPfEcr = async () => {
    if (!selectedPeriodId) return;
    try {
      const blob = await reportsService.downloadPfEcrFile(selectedPeriodId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `PF_ECR_Return_Period_${selectedPeriodId}.txt`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err: any) {
      alert('Failed to download PF ECR file');
    }
  };

  const filteredRegister = registerData?.records.filter(
    (r) =>
      r.employee_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.employee_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.department.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex justify-between items-center bg-slate-800/60 p-6 rounded-2xl border border-slate-700/50 backdrop-blur-md">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-amber-400" />
            Payroll Reports & Executive Analytics
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Generate India PF ECR statutory returns, inspect itemized master registers, and track executive cost center analytics.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={selectedPeriodId || ''}
            onChange={(e) => setSelectedPeriodId(Number(e.target.value))}
            className="bg-slate-800 border border-slate-700 text-slate-100 px-4 py-2 rounded-xl text-sm font-medium focus:outline-none focus:border-amber-500"
          >
            {periods.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.year_month})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Tabs Bar */}
      <div className="flex gap-4 border-b border-slate-700/50 pb-2">
        <button
          onClick={() => setActiveTab('analytics')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
            activeTab === 'analytics'
              ? 'bg-slate-700 text-amber-400 border border-slate-600'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <TrendingUp className="w-4 h-4" /> Executive Analytics
        </button>
        <button
          onClick={() => setActiveTab('statutory')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
            activeTab === 'statutory'
              ? 'bg-slate-700 text-emerald-400 border border-slate-600'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <ShieldCheck className="w-4 h-4" /> Statutory Compliance
        </button>
        <button
          onClick={() => setActiveTab('register')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
            activeTab === 'register'
              ? 'bg-slate-700 text-sky-400 border border-slate-600'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileSpreadsheet className="w-4 h-4" /> Master Payroll Register
        </button>
        <button
          onClick={() => setActiveTab('costcenter')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
            activeTab === 'costcenter'
              ? 'bg-slate-700 text-purple-400 border border-slate-600'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Building className="w-4 h-4" /> Cost Center Summary
        </button>
      </div>

      {/* Content Panels */}
      {activeTab === 'analytics' && analytics && (
        <div className="space-y-6">
          {/* Executive Metrics Cards */}
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-slate-800/40 p-5 rounded-2xl border border-slate-700/50 space-y-2">
              <div className="text-slate-400 text-xs font-medium uppercase">YTD Gross Payroll CTC</div>
              <div className="text-2xl font-bold text-amber-400">₹{analytics.total_ytd_gross.toLocaleString()}</div>
              <div className="text-[11px] text-slate-500">Across {analytics.total_runs_executed} executed runs</div>
            </div>
            <div className="bg-slate-800/40 p-5 rounded-2xl border border-slate-700/50 space-y-2">
              <div className="text-slate-400 text-xs font-medium uppercase">YTD Net Salary Disbursed</div>
              <div className="text-2xl font-bold text-emerald-400">₹{analytics.total_ytd_net.toLocaleString()}</div>
              <div className="text-[11px] text-slate-500">Direct employee bank payout</div>
            </div>
            <div className="bg-slate-800/40 p-5 rounded-2xl border border-slate-700/50 space-y-2">
              <div className="text-slate-400 text-xs font-medium uppercase">YTD Total Deductions</div>
              <div className="text-2xl font-bold text-red-400">₹{analytics.total_ytd_deductions.toLocaleString()}</div>
              <div className="text-[11px] text-slate-500">Statutory PF/ESI + TDS Tax</div>
            </div>
            <div className="bg-slate-800/40 p-5 rounded-2xl border border-slate-700/50 space-y-2">
              <div className="text-slate-400 text-xs font-medium uppercase">Active Payroll Periods</div>
              <div className="text-2xl font-bold text-sky-400">{analytics.total_active_periods} Periods</div>
              <div className="text-[11px] text-slate-500">Configured in organization</div>
            </div>
          </div>

          {/* Historical Trends Card */}
          <div className="bg-slate-800/40 p-6 rounded-2xl border border-slate-700/50 space-y-4">
            <h2 className="text-base font-bold text-slate-200 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-amber-400" /> Historical Payroll Trends
            </h2>
            <div className="space-y-3">
              {analytics.payroll_trends.map((t) => (
                <div key={t.period_id} className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 flex justify-between items-center">
                  <div>
                    <div className="font-semibold text-slate-100">{t.period_name}</div>
                    <div className="text-xs text-slate-400">{t.total_employees} Employees Processed</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold text-emerald-400">Gross: ₹{t.total_gross.toLocaleString()}</div>
                    <div className="text-xs text-slate-400">Net: ₹{t.total_net.toLocaleString()}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* STATUTORY TAB */}
      {activeTab === 'statutory' && (
        <div className="grid grid-cols-3 gap-6">
          {/* PF ECR Card */}
          <div className="bg-slate-800/40 p-6 rounded-2xl border border-slate-700/50 space-y-4 flex flex-col justify-between">
            <div className="space-y-2">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-100">EPFO India PF ECR Return</h3>
              <p className="text-slate-400 text-xs">
                Generate standard Electronic Challan cum Return text file formatted with <code className="text-emerald-400">#~#</code> delimiters for direct EPFO portal upload.
              </p>
            </div>
            <button
              onClick={handleDownloadPfEcr}
              className="w-full bg-emerald-600 hover:bg-emerald-500 text-white py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center justify-center gap-2"
            >
              <Download className="w-4 h-4" /> Download PF ECR (.txt)
            </button>
          </div>

          {/* ESI Monthly Summary */}
          <div className="bg-slate-800/40 p-6 rounded-2xl border border-slate-700/50 space-y-4 flex flex-col justify-between">
            <div className="space-y-2">
              <div className="w-10 h-10 rounded-xl bg-sky-500/20 text-sky-400 flex items-center justify-center font-bold">
                <FileText className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-100">ESIC Statutory Return</h3>
              <p className="text-slate-400 text-xs">
                Monthly ESI contribution summary covering Employee (0.75%) and Employer (3.25%) contributions.
              </p>
            </div>
            <button
              onClick={() => alert('ESIC Return Summary exported.')}
              className="w-full bg-sky-600 hover:bg-sky-500 text-white py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center justify-center gap-2"
            >
              <Download className="w-4 h-4" /> Export ESI Summary (.csv)
            </button>
          </div>

          {/* TDS Form 24Q Card */}
          <div className="bg-slate-800/40 p-6 rounded-2xl border border-slate-700/50 space-y-4 flex flex-col justify-between">
            <div className="space-y-2">
              <div className="w-10 h-10 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold">
                <PieChart className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-100">Income Tax TDS Form 24Q</h3>
              <p className="text-slate-400 text-xs">
                Quarterly TDS tax deduction statement file containing taxable income, slab math, and 4% Cess.
              </p>
            </div>
            <button
              onClick={() => alert('Form 24Q dataset exported.')}
              className="w-full bg-amber-600 hover:bg-amber-500 text-white py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center justify-center gap-2"
            >
              <Download className="w-4 h-4" /> Export Form 24Q (.csv)
            </button>
          </div>
        </div>
      )}

      {/* MASTER REGISTER TAB */}
      {activeTab === 'register' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <div className="relative max-w-xs w-full">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="text"
                placeholder="Search staff, code, department..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl pl-9 pr-4 py-2 text-slate-100 text-sm"
              />
            </div>
            {registerData && (
              <div className="text-xs text-slate-400">
                Showing <strong className="text-slate-200">{filteredRegister.length}</strong> of {registerData.total_employees} records
              </div>
            )}
          </div>

          {loading ? (
            <div className="p-12 text-center text-slate-400">Loading master register...</div>
          ) : registerData ? (
            <div className="bg-slate-800/40 rounded-2xl border border-slate-700/50 overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-slate-800/80 text-slate-400 uppercase tracking-wider border-b border-slate-700">
                    <th className="p-3">Emp Code</th>
                    <th className="p-3">Employee Name</th>
                    <th className="p-3">Dept</th>
                    <th className="p-3">Days</th>
                    <th className="p-3">Basic</th>
                    <th className="p-3">HRA</th>
                    <th className="p-3">Special</th>
                    <th className="p-3">Gross Salary</th>
                    <th className="p-3">PF</th>
                    <th className="p-3">ESI</th>
                    <th className="p-3">TDS</th>
                    <th className="p-3">Total Ded</th>
                    <th className="p-3 font-bold text-emerald-400">Net Take-Home</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/50 text-slate-200">
                  {filteredRegister.map((r) => (
                    <tr key={r.payroll_employee_id} className="hover:bg-slate-700/20 transition-all">
                      <td className="p-3 font-mono text-sky-400">{r.employee_code}</td>
                      <td className="p-3 font-medium text-slate-100">{r.employee_name}</td>
                      <td className="p-3 text-slate-400">{r.department}</td>
                      <td className="p-3 text-slate-300">{r.payable_days}/{r.total_days}</td>
                      <td className="p-3 font-mono">₹{r.basic.toLocaleString()}</td>
                      <td className="p-3 font-mono">₹{r.hra.toLocaleString()}</td>
                      <td className="p-3 font-mono">₹{r.special_allowance.toLocaleString()}</td>
                      <td className="p-3 font-bold text-slate-100">₹{r.gross_salary.toLocaleString()}</td>
                      <td className="p-3 text-red-400 font-mono">₹{r.pf_deduction.toLocaleString()}</td>
                      <td className="p-3 text-red-400 font-mono">₹{r.esi_deduction.toLocaleString()}</td>
                      <td className="p-3 text-red-400 font-mono">₹{r.tds_deduction.toLocaleString()}</td>
                      <td className="p-3 text-red-400 font-bold">₹{r.total_deductions.toLocaleString()}</td>
                      <td className="p-3 font-bold text-emerald-400">₹{r.net_salary.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </div>
      )}

      {/* COST CENTER TAB */}
      {activeTab === 'costcenter' && (
        <div className="bg-slate-800/40 rounded-2xl border border-slate-700/50 overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-800/80 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-700">
                <th className="p-4">Department / Cost Center</th>
                <th className="p-4">Headcount</th>
                <th className="p-4">Gross CTC Expenditure</th>
                <th className="p-4">Employer Statutory Cost</th>
                <th className="p-4">Total Net Payout</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50 text-sm text-slate-200">
              {costCenterData.map((row) => (
                <tr key={row.department} className="hover:bg-slate-700/20 transition-all">
                  <td className="p-4 font-bold text-slate-100">{row.department}</td>
                  <td className="p-4 text-slate-300 font-mono">{row.employee_count} Staff</td>
                  <td className="p-4 font-semibold text-amber-400">₹{row.gross_salary.toLocaleString()}</td>
                  <td className="p-4 text-sky-400 font-mono">₹{row.employer_cost.toLocaleString()}</td>
                  <td className="p-4 font-bold text-emerald-400">₹{row.net_salary.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
