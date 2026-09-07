import React, { useEffect, useState } from 'react';
import { salaryService } from '../services/salaryService';
import { employeeService } from '../services/employeeService';
import { SalaryComponent, EmployeeSalary, SalaryRevision } from '../types/salary';
import { Employee } from '../types/employee';
import { Calculator, Plus, DollarSign, TrendingUp, Layers, Tag, ShieldCheck, CheckCircle2, RefreshCw } from 'lucide-react';

export const SalaryStructuresPage: React.FC = () => {
  const [components, setComponents] = useState<SalaryComponent[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [selectedEmpId, setSelectedEmpId] = useState<number | undefined>(undefined);
  const [activeSalary, setActiveSalary] = useState<EmployeeSalary | null>(null);
  const [revisions, setRevisions] = useState<SalaryRevision[]>([]);
  const [activeTab, setActiveTab] = useState<'calculator' | 'catalog' | 'revisions'>('calculator');
  const [isLoading, setIsLoading] = useState(true);

  // CTC Assignment Form
  const [ctcInput, setCtcInput] = useState<number>(600000);
  const [effDate, setEffDate] = useState<string>('2024-01-01');

  // Revision Modal State
  const [showReviseModal, setShowReviseModal] = useState(false);
  const [newCtcInput, setNewCtcInput] = useState<number>(720000);
  const [revDate, setRevDate] = useState<string>('2024-10-01');
  const [revReason, setRevReason] = useState<string>('Annual Performance Increment');

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [compRes, empRes] = await Promise.all([
        salaryService.getComponents(),
        employeeService.getEmployees({ limit: 100 }),
      ]);
      setComponents(compRes);
      setEmployees(empRes.items);

      if (empRes.items.length > 0) {
        const empId = empRes.items[0].id;
        setSelectedEmpId(empId);
        await loadEmployeeSalaryData(empId);
      }
    } catch (err) {
      console.error('Failed to load salary catalog', err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadEmployeeSalaryData = async (empId: number) => {
    try {
      const sal = await salaryService.getEmployeeSalary(empId);
      setActiveSalary(sal);
      setCtcInput(sal.total_ctc);
      const revs = await salaryService.getSalaryRevisions(empId);
      setRevisions(revs);
    } catch (err) {
      // Auto-assign default CTC if not existing
      const newSal = await salaryService.assignSalary(empId, 600000, '2024-01-01');
      setActiveSalary(newSal);
      setCtcInput(600000);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCalculateBreakdown = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedEmpId) return;
    try {
      const sal = await salaryService.assignSalary(selectedEmpId, ctcInput, effDate);
      setActiveSalary(sal);
    } catch (err) {
      alert('Failed to assign salary');
    }
  };

  const handleExecuteRevision = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedEmpId) return;
    try {
      await salaryService.reviseSalary(selectedEmpId, newCtcInput, revDate, revReason);
      setShowReviseModal(false);
      await loadEmployeeSalaryData(selectedEmpId);
    } catch (err) {
      alert('Revision failed');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center space-x-2">
            <Calculator className="w-5 h-5 text-brand-400" />
            <span>Configurable Salary Structure & CTC Engine</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">Dynamic earnings & deductions component formulas, CTC breakdown, and revision audit tracking</p>
        </div>

        <button
          onClick={() => setShowReviseModal(true)}
          className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-sky-400 text-white text-xs font-semibold shadow-lg shadow-brand-500/20 transition"
        >
          <TrendingUp className="w-4 h-4" />
          <span>Revise Employee CTC</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('calculator')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeTab === 'calculator' ? 'bg-brand-500/10 text-brand-400 border border-brand-500/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Calculator className="w-4 h-4" />
          <span>CTC Breakdown Engine</span>
        </button>

        <button
          onClick={() => setActiveTab('catalog')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeTab === 'catalog' ? 'bg-brand-500/10 text-brand-400 border border-brand-500/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>Component Catalog ({components.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('revisions')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeTab === 'revisions' ? 'bg-brand-500/10 text-brand-400 border border-brand-500/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <RefreshCw className="w-4 h-4" />
          <span>Salary Revision Audit ({revisions.length})</span>
        </button>
      </div>

      {/* Tab 1: CTC Breakdown Engine */}
      {activeTab === 'calculator' && (
        <div className="space-y-6">
          {/* Employee Selector & CTC Input */}
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center space-x-4 w-full md:w-auto">
              <span className="text-xs font-semibold text-slate-300">Select Employee:</span>
              <select
                value={selectedEmpId}
                onChange={(e) => {
                  const empId = Number(e.target.value);
                  setSelectedEmpId(empId);
                  loadEmployeeSalaryData(empId);
                }}
                className="bg-slate-900 border border-slate-700 rounded-xl py-2 px-3 text-xs text-white focus:outline-none focus:border-brand-500"
              >
                {employees.map((emp) => (
                  <option key={emp.id} value={emp.id}>{emp.first_name} {emp.last_name} ({emp.employee_code})</option>
                ))}
              </select>
            </div>

            <form onSubmit={handleCalculateBreakdown} className="flex items-center space-x-3 w-full md:w-auto">
              <span className="text-xs text-slate-400 font-mono">Annual CTC (₹):</span>
              <input
                type="number"
                required
                step="10000"
                value={ctcInput}
                onChange={(e) => setCtcInput(Number(e.target.value))}
                className="bg-slate-900 border border-slate-700 rounded-xl py-2 px-3 text-xs text-white font-mono w-36 focus:outline-none focus:border-brand-500"
              />
              <button
                type="submit"
                className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs shadow-md transition"
              >
                Re-Calculate
              </button>
            </form>
          </div>

          {/* Active Salary Summary Cards */}
          {activeSalary && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="glass-panel p-5 rounded-2xl border border-slate-800">
                <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">Annual CTC</span>
                <span className="text-2xl font-bold text-white font-mono">₹{activeSalary.total_ctc.toLocaleString()}</span>
                <span className="text-[11px] text-slate-500 block mt-1 font-mono">₹{(activeSalary.total_ctc / 12).toFixed(2)} / month</span>
              </div>

              <div className="glass-panel p-5 rounded-2xl border border-slate-800">
                <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">Monthly Gross Salary</span>
                <span className="text-2xl font-bold text-emerald-400 font-mono">₹{activeSalary.gross_salary.toLocaleString()}</span>
                <span className="text-[11px] text-emerald-500/80 block mt-1 font-mono">Pre-deduction earnings</span>
              </div>

              <div className="glass-panel p-5 rounded-2xl border border-brand-500/40 bg-brand-500/10">
                <span className="text-xs text-brand-300 uppercase tracking-wider font-semibold block mb-1">Monthly Net Take-Home</span>
                <span className="text-2xl font-bold text-white font-mono">₹{activeSalary.net_salary.toLocaleString()}</span>
                <span className="text-[11px] text-brand-300/80 block mt-1 font-mono">After PF & PT deductions</span>
              </div>
            </div>
          )}

          {/* Detailed Component Breakdown Table */}
          {activeSalary && (
            <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
              <div className="p-4 border-b border-slate-800 font-bold text-white text-xs flex items-center justify-between">
                <span>Calculated Salary Component Breakdown</span>
                <span className="font-mono text-slate-400 text-[11px]">Effective Date: {activeSalary.effective_date}</span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                    <tr>
                      <th className="py-3.5 px-4">Component</th>
                      <th className="py-3.5 px-4">Code</th>
                      <th className="py-3.5 px-4">Category</th>
                      <th className="py-3.5 px-4 text-right">Monthly Amount</th>
                      <th className="py-3.5 px-4 text-right">Annual Amount</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {activeSalary.assigned_components.map((row) => (
                      <tr key={row.id} className="hover:bg-slate-800/30 transition">
                        <td className="py-3.5 px-4 font-semibold text-white">{row.component.name}</td>
                        <td className="py-3.5 px-4 font-mono font-bold text-brand-400">{row.component.code}</td>
                        <td className="py-3.5 px-4">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                            row.component.component_type === 'Earning'
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                              : 'bg-red-500/10 text-red-400 border border-red-500/30'
                          }`}>
                            {row.component.component_type}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-right font-mono font-bold text-white">
                          ₹{row.monthly_amount.toLocaleString()}
                        </td>
                        <td className="py-3.5 px-4 text-right font-mono text-slate-400">
                          ₹{row.annual_amount.toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Catalog */}
      {activeTab === 'catalog' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {components.map((comp) => (
            <div key={comp.id} className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-white text-sm">{comp.name}</span>
                <span className={`px-2 py-0.5 rounded font-mono text-[10px] font-bold ${
                  comp.component_type === 'Earning' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
                }`}>
                  {comp.component_type}
                </span>
              </div>
              <div className="text-xs text-slate-400 space-y-1 font-mono">
                <div>Code: <strong className="text-brand-300">{comp.code}</strong></div>
                <div>Calc Type: {comp.calculation_type}</div>
                {comp.percentage_value && <div>Formula: {comp.percentage_value}% of {comp.percentage_base_code}</div>}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 3: Revisions */}
      {activeTab === 'revisions' && (
        <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="py-3.5 px-4">Effective Date</th>
                  <th className="py-3.5 px-4">Old CTC</th>
                  <th className="py-3.5 px-4">New CTC</th>
                  <th className="py-3.5 px-4">Increment %</th>
                  <th className="py-3.5 px-4">Revision Reason</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {revisions.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-slate-500 italic">No salary revisions recorded for selected employee.</td>
                  </tr>
                ) : (
                  revisions.map((rev) => (
                    <tr key={rev.id} className="hover:bg-slate-800/30 transition">
                      <td className="py-3.5 px-4 font-mono text-white font-semibold">{rev.effective_date}</td>
                      <td className="py-3.5 px-4 font-mono text-slate-400">₹{rev.old_ctc.toLocaleString()}</td>
                      <td className="py-3.5 px-4 font-mono font-bold text-emerald-400">₹{rev.new_ctc.toLocaleString()}</td>
                      <td className="py-3.5 px-4 font-mono font-bold text-purple-400">+{rev.increment_percentage}%</td>
                      <td className="py-3.5 px-4 text-slate-300">{rev.revision_reason || 'N/A'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Revision Modal */}
      {showReviseModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-md p-6 rounded-2xl border border-slate-700 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white">Execute Salary Revision</h3>
            <form onSubmit={handleExecuteRevision} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">New Annual CTC (₹)</label>
                <input
                  type="number"
                  required
                  step="10000"
                  value={newCtcInput}
                  onChange={(e) => setNewCtcInput(Number(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Effective Date</label>
                <input
                  type="date"
                  required
                  value={revDate}
                  onChange={(e) => setRevDate(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Revision Reason</label>
                <textarea
                  value={revReason}
                  onChange={(e) => setRevReason(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white"
                  rows={2}
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowReviseModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300"
                >
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 rounded-lg bg-brand-600 text-white font-semibold shadow-md">
                  Execute Revision
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
