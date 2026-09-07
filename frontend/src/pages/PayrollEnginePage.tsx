import React, { useEffect, useState } from 'react';
import { payrollService } from '../services/payrollService';
import { PayrollPeriod, PayrollRun, PayrollEmployee } from '../types/payroll';
import { Calculator, Play, CheckCircle2, Lock, ShieldCheck, HelpCircle, Eye, ArrowRight, DollarSign, Users, Award } from 'lucide-react';

export const PayrollEnginePage: React.FC = () => {
  const [periods, setPeriods] = useState<PayrollPeriod[]>([]);
  const [selectedPeriodId, setSelectedPeriodId] = useState<number | undefined>(undefined);
  const [activeRun, setActiveRun] = useState<PayrollRun | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCalculating, setIsCalculating] = useState(false);

  // Trace Inspect Drawer State
  const [inspectEmployee, setInspectEmployee] = useState<PayrollEmployee | null>(null);

  const loadPeriods = async () => {
    setIsLoading(true);
    try {
      const pList = await payrollService.getPeriods();
      setPeriods(pList);
      if (pList.length > 0) {
        setSelectedPeriodId(pList[0].id);
        // Automatically calculate or fetch run
        await runCalculation(pList[0].id);
      }
    } catch (err) {
      console.error('Failed to load payroll periods', err);
    } finally {
      setIsLoading(false);
    }
  };

  const runCalculation = async (periodId: number) => {
    setIsCalculating(true);
    try {
      const run = await payrollService.calculatePayroll(periodId);
      setActiveRun(run);
    } catch (err: any) {
      // If locked, load existing run
      if (err.response?.data?.error_code === 'PAYROLL_ALREADY_LOCKED') {
        const period = periods.find(p => p.id === periodId);
        if (period) {
          // Fetch existing run
        }
      }
    } finally {
      setIsCalculating(false);
    }
  };

  useEffect(() => {
    loadPeriods();
  }, []);

  const handleApprove = async () => {
    if (!activeRun) return;
    try {
      const updated = await payrollService.approvePayroll(activeRun.id);
      setActiveRun(updated);
    } catch (err) {
      alert('Approval failed');
    }
  };

  const handleLock = async () => {
    if (!activeRun) return;
    try {
      const updated = await payrollService.lockPayroll(activeRun.id);
      setActiveRun(updated);
    } catch (err) {
      alert('Locking failed');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center space-x-2">
            <Calculator className="w-5 h-5 text-brand-400" />
            <span>Independent Payroll Calculation Engine & Tracing</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">Deterministic payroll calculation pipeline, proration engine, and explainable mathematical trace inspection</p>
        </div>

        <div className="flex items-center space-x-2">
          {activeRun && activeRun.status !== 'Locked' && (
            <>
              {activeRun.status === 'Calculated' && (
                <button
                  onClick={handleApprove}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-lg shadow-emerald-500/20 transition flex items-center space-x-1.5"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Approve Payroll</span>
                </button>
              )}
              {activeRun.status === 'Approved' && (
                <button
                  onClick={handleLock}
                  className="px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold shadow-lg shadow-amber-500/20 transition flex items-center space-x-1.5"
                >
                  <Lock className="w-4 h-4" />
                  <span>Lock Payroll Run</span>
                </button>
              )}
            </>
          )}

          {activeRun?.status === 'Locked' && (
            <span className="px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-mono font-bold flex items-center space-x-1.5">
              <Lock className="w-4 h-4" />
              <span>LOCKED & IMMUTABLE</span>
            </span>
          )}
        </div>
      </div>

      {/* Period Selector Bar */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-3 w-full md:w-auto">
          <span className="text-xs font-semibold text-slate-300">Payroll Period:</span>
          <select
            value={selectedPeriodId}
            onChange={(e) => {
              const pId = Number(e.target.value);
              setSelectedPeriodId(pId);
              runCalculation(pId);
            }}
            className="bg-slate-900 border border-slate-700 rounded-xl py-2 px-3 text-xs text-white focus:outline-none focus:border-brand-500 font-mono"
          >
            {periods.map((p) => (
              <option key={p.id} value={p.id}>{p.name} ({p.year_month})</option>
            ))}
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={async () => {
              setIsCalculating(true);
              try {
                const res = await payrollService.runBenchmark(10000);
                alert(`✓ 10,000 Employee Benchmark Complete!\n• Duration: ${res.duration_seconds}s\n• Throughput: ${res.throughput_per_sec} calculations/sec\n• Total Gross: ₹${res.total_gross_disbursed.toLocaleString()}`);
              } catch (err) {
                alert('Benchmark failed');
              } finally {
                setIsCalculating(false);
              }
            }}
            disabled={isCalculating}
            className="w-full md:w-auto px-4 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs shadow-lg shadow-purple-500/25 flex items-center justify-center space-x-2 disabled:opacity-50 transition"
          >
            <Users className="w-4 h-4" />
            <span>Benchmark 10,000 Staff</span>
          </button>

          <button
            onClick={() => selectedPeriodId && runCalculation(selectedPeriodId)}
            disabled={isCalculating || activeRun?.status === 'Locked'}
            className="w-full md:w-auto px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs shadow-lg shadow-brand-500/25 flex items-center justify-center space-x-2 disabled:opacity-50 transition"
          >
            {isCalculating ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span>Execute Calculation Pipeline</span>
              </>
            )}
          </button>
        </div>
      </div>


      {/* Lifecycle Stepper Progress Bar */}
      {activeRun && (
        <div className="glass-panel p-4 rounded-2xl border border-slate-800 flex items-center justify-between text-xs">
          {['Draft', 'Calculated', 'Approved', 'Locked'].map((step, idx) => {
            const isCompleted = 
              (activeRun.status === 'Calculated' && idx <= 1) ||
              (activeRun.status === 'Approved' && idx <= 2) ||
              (activeRun.status === 'Locked');
            
            return (
              <React.Fragment key={step}>
                <div className={`flex items-center space-x-2 font-mono ${
                  isCompleted ? 'text-brand-400 font-bold' : 'text-slate-500'
                }`}>
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold ${
                    isCompleted ? 'bg-brand-500 text-white' : 'bg-slate-800 text-slate-500'
                  }`}>
                    {idx + 1}
                  </div>
                  <span>{step}</span>
                </div>
                {idx < 3 && <ArrowRight className="w-4 h-4 text-slate-700 hidden sm:block" />}
              </React.Fragment>
            );
          })}
        </div>
      )}

      {/* Financial Summary Dashboard Cards */}
      {activeRun && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="glass-panel p-5 rounded-2xl border border-slate-800">
            <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">Processed Employees</span>
            <span className="text-2xl font-bold text-white font-mono">{activeRun.total_employees} Staff</span>
          </div>

          <div className="glass-panel p-5 rounded-2xl border border-slate-800">
            <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">Total Gross Payroll</span>
            <span className="text-2xl font-bold text-emerald-400 font-mono">₹{activeRun.total_gross.toLocaleString()}</span>
          </div>

          <div className="glass-panel p-5 rounded-2xl border border-slate-800">
            <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">Total Net Disbursement</span>
            <span className="text-2xl font-bold text-white font-mono">₹{activeRun.total_net.toLocaleString()}</span>
          </div>

          <div className="glass-panel p-5 rounded-2xl border border-brand-500/40 bg-brand-500/10">
            <span className="text-xs text-brand-300 uppercase tracking-wider font-semibold block mb-1">Total Employer Cost</span>
            <span className="text-2xl font-bold text-brand-200 font-mono">₹{activeRun.total_employer_cost.toLocaleString()}</span>
          </div>
        </div>
      )}

      {/* Employee Payroll Register Table */}
      {activeRun && (
        <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
          <div className="p-4 border-b border-slate-800 font-bold text-white text-xs flex items-center justify-between">
            <span>Employee Payroll Register</span>
            <span className="font-mono text-brand-400 text-[11px]">Run Status: {activeRun.status}</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="py-3.5 px-4">Employee ID</th>
                  <th className="py-3.5 px-4">Payable / Total Days</th>
                  <th className="py-3.5 px-4 text-right">Gross Salary</th>
                  <th className="py-3.5 px-4 text-right">Deductions</th>
                  <th className="py-3.5 px-4 text-right">Net Take-Home</th>
                  <th className="py-3.5 px-4 text-right">Employer Cost</th>
                  <th className="py-3.5 px-4 text-center">Explainable Trace</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {activeRun.employee_results.map((row) => (
                  <tr key={row.id} className="hover:bg-slate-800/30 transition">
                    <td className="py-3.5 px-4 font-mono font-bold text-brand-400">EMP #{row.employee_id}</td>
                    <td className="py-3.5 px-4 font-mono text-slate-300">
                      <span className="text-white font-bold">{row.payable_days}</span> / {row.total_days} Days
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono font-bold text-emerald-400">₹{row.gross_salary.toLocaleString()}</td>
                    <td className="py-3.5 px-4 text-right font-mono text-red-400">₹{row.total_deductions.toLocaleString()}</td>
                    <td className="py-3.5 px-4 text-right font-mono font-bold text-white">₹{row.net_salary.toLocaleString()}</td>
                    <td className="py-3.5 px-4 text-right font-mono text-brand-300">₹{row.employer_cost.toLocaleString()}</td>
                    <td className="py-3.5 px-4 text-center">
                      <button
                        onClick={() => setInspectEmployee(row)}
                        className="px-3 py-1.5 rounded-lg bg-brand-600/20 hover:bg-brand-600/40 text-brand-300 border border-brand-500/30 text-xs font-semibold inline-flex items-center space-x-1 transition"
                      >
                        <HelpCircle className="w-3.5 h-3.5" />
                        <span>Inspect Trace</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Mandatory Explainable Calculation Trace Inspection Side Drawer Modal */}
      {inspectEmployee && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-end">
          <div className="glass-panel w-full max-w-xl h-full p-6 border-l border-slate-700 shadow-2xl overflow-y-auto space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center space-x-2">
                  <ShieldCheck className="w-5 h-5 text-brand-400" />
                  <span>Calculation Trace Tree</span>
                </h3>
                <p className="text-xs text-slate-400 font-mono mt-0.5">EMP #{inspectEmployee.employee_id} • September 2024</p>
              </div>
              <button
                onClick={() => setInspectEmployee(null)}
                className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold"
              >
                Close
              </button>
            </div>

            {/* Trace Step 1: Proration */}
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2 text-xs">
              <span className="font-bold text-brand-400 uppercase tracking-wider font-mono">Step 1: Attendance Proration</span>
              <p className="text-slate-300 font-mono">{inspectEmployee.calculation_trace.step_1_proration.explanation}</p>
            </div>

            {/* Trace Step 2: Earnings */}
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2 text-xs">
              <span className="font-bold text-emerald-400 uppercase tracking-wider font-mono">Step 2: Earnings & Overtime Breakdown</span>
              <div className="space-y-1 font-mono text-[11px] text-slate-300 pt-1">
                <div className="flex justify-between"><span>Basic Salary (Prorated):</span><span>₹{inspectEmployee.calculation_trace.step_2_earnings_breakdown.basic.prorated}</span></div>
                <div className="flex justify-between"><span>HRA (Prorated):</span><span>₹{inspectEmployee.calculation_trace.step_2_earnings_breakdown.hra.prorated}</span></div>
                <div className="flex justify-between"><span>Transport Allowance:</span><span>₹{inspectEmployee.calculation_trace.step_2_earnings_breakdown.transport.prorated}</span></div>
                <div className="flex justify-between"><span>Special Allowance:</span><span>₹{inspectEmployee.calculation_trace.step_2_earnings_breakdown.special_allowance.prorated}</span></div>
                <div className="flex justify-between text-purple-400"><span>Overtime Pay ({inspectEmployee.calculation_trace.step_2_earnings_breakdown.overtime.hours} hrs):</span><span>+₹{inspectEmployee.calculation_trace.step_2_earnings_breakdown.overtime.pay}</span></div>
              </div>
              <p className="text-slate-400 font-mono pt-2 border-t border-slate-800 text-[11px]">{inspectEmployee.calculation_trace.step_2_earnings_breakdown.explanation}</p>
            </div>

            {/* Trace Step 3: Deductions */}
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2 text-xs">
              <span className="font-bold text-red-400 uppercase tracking-wider font-mono">Step 3: Employee Statutory Deductions</span>
              <div className="space-y-1 font-mono text-[11px] text-slate-300 pt-1">
                <div className="flex justify-between"><span>Employee PF (12% capped at ₹1800):</span><span>₹{inspectEmployee.calculation_trace.step_3_deductions_breakdown.employee_pf.capped}</span></div>
                <div className="flex justify-between"><span>Professional Tax (PT):</span><span>₹{inspectEmployee.calculation_trace.step_3_deductions_breakdown.professional_tax.amount}</span></div>
              </div>
            </div>

            {/* Trace Step 4 & 5: Net Take-Home */}
            <div className="p-4 rounded-xl bg-brand-500/10 border border-brand-500/30 space-y-2 text-xs">
              <span className="font-bold text-white uppercase tracking-wider font-mono">Step 4 & 5: Final Net Disbursement</span>
              <p className="text-brand-200 font-mono font-semibold">{inspectEmployee.calculation_trace.step_5_final_takehome.formula_explanation}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
