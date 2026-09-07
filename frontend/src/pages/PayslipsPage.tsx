import React, { useEffect, useState } from 'react';
import {
  FileText,
  Download,
  CheckCircle,
  Clock,
  Lock,
  Eye,
  X,
  AlertCircle,
  Building,
  UserCheck,
} from 'lucide-react';
import { payrollService } from '../services/payrollService';
import { payslipService } from '../services/payslipService';
import { PayrollPeriod, PayrollRun, PayrollEmployee } from '../types/payroll';
import { PayrollApprovalResponse } from '../types/payslip';

export const PayslipsPage: React.FC = () => {
  const [periods, setPeriods] = useState<PayrollPeriod[]>([]);
  const [selectedPeriodId, setSelectedPeriodId] = useState<number | null>(null);
  const [currentRun, setCurrentRun] = useState<PayrollRun | null>(null);
  const [employees, setEmployees] = useState<PayrollEmployee[]>([]);
  const [approvalLogs, setApprovalLogs] = useState<PayrollApprovalResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // PDF Preview Modal
  const [previewPdfUrl, setPreviewPdfUrl] = useState<string | null>(null);
  const [previewEmployeeName, setPreviewEmployeeName] = useState<string>('');

  // Approval Comment Modal
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [approvalActionType, setApprovalActionType] = useState<'APPROVE' | 'REJECT'>('APPROVE');
  const [approvalRemarks, setApprovalRemarks] = useState('');

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
        setEmployees(run.employee_results || []);
        
        // Fetch approval logs
        const logs = await payslipService.getApprovalLog(run.id);
        setApprovalLogs(logs);
      } else {
        setCurrentRun(null);
        setEmployees([]);
        setApprovalLogs([]);
      }
    } catch (err: any) {
      setError(err?.response?.data?.message || 'Failed to load run details');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadSinglePdf = async (employeeId: number, name: string) => {
    if (!selectedPeriodId) return;
    try {
      const blob = await payslipService.downloadEmployeePayslipPdf(employeeId, selectedPeriodId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Payslip_${name.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err: any) {
      alert('Failed to download PDF');
    }
  };

  const handlePreviewPdf = async (employeeId: number, name: string) => {
    if (!selectedPeriodId) return;
    try {
      const blob = await payslipService.downloadEmployeePayslipPdf(employeeId, selectedPeriodId);
      const url = window.URL.createObjectURL(blob);
      setPreviewPdfUrl(url);
      setPreviewEmployeeName(name);
    } catch (err: any) {
      alert('Failed to preview PDF');
    }
  };

  const handleDownloadBulkZip = async () => {
    if (!currentRun) return;
    try {
      const blob = await payslipService.downloadBulkPayslipsZip(currentRun.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Bulk_Payslips_Run_${currentRun.id}.zip`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err: any) {
      alert('Failed to download bulk ZIP');
    }
  };

  const submitApprovalAction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentRun) return;
    try {
      await payslipService.approvePayrollRun(currentRun.id, {
        action: approvalActionType,
        remarks: approvalRemarks,
      });
      setShowApprovalModal(false);
      setApprovalRemarks('');
      loadRunDetails(selectedPeriodId!);
    } catch (err: any) {
      alert(err?.response?.data?.message || 'Approval action failed');
    }
  };

  // Helper for Stepper Stage Status
  const getStageStatus = (stageIndex: number) => {
    if (!currentRun) return 'pending';
    const status = currentRun.status;
    if (status === 'Locked') return 'completed';
    if (status === 'Finance Approved' && stageIndex <= 2) return 'completed';
    if (status === 'Manager Approved' && stageIndex <= 1) return 'completed';
    if (status === 'Calculated' && stageIndex === 0) return 'active';
    return 'pending';
  };

  return (
    <div className="space-y-6">
      {/* Header Panel */}
      <div className="flex justify-between items-center bg-slate-800/60 p-6 rounded-2xl border border-slate-700/50 backdrop-blur-md">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-3">
            <FileText className="w-8 h-8 text-sky-400" />
            Payslips & Approval Workflow
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Execute sequential multi-tier approvals, inspect live ReportLab PDF payslips, and download organization bulk ZIP archives.
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Period Selector */}
          <select
            value={selectedPeriodId || ''}
            onChange={(e) => setSelectedPeriodId(Number(e.target.value))}
            className="bg-slate-800 border border-slate-700 text-slate-100 px-4 py-2 rounded-xl text-sm font-medium focus:outline-none focus:border-sky-500"
          >
            {periods.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.year_month})
              </option>
            ))}
          </select>
          {currentRun && (
            <button
              onClick={handleDownloadBulkZip}
              className="bg-sky-600 hover:bg-sky-500 text-white px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-2 shadow-lg shadow-sky-600/20"
            >
              <Download className="w-4 h-4" /> Download All (ZIP)
            </button>
          )}
        </div>
      </div>

      {/* Multi-Tier Approval Workflow Stepper */}
      {currentRun && (
        <div className="bg-slate-800/40 p-6 rounded-2xl border border-slate-700/50 space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-bold text-slate-200 flex items-center gap-2">
              <UserCheck className="w-5 h-5 text-emerald-400" /> Multi-Tier Approval Chain
            </h2>
            <div className="flex gap-2">
              {currentRun.status !== 'Locked' && (
                <>
                  <button
                    onClick={() => {
                      setApprovalActionType('APPROVE');
                      setShowApprovalModal(true);
                    }}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-1.5 rounded-xl text-xs font-semibold transition-all flex items-center gap-1.5 shadow-md shadow-emerald-600/20"
                  >
                    <CheckCircle className="w-4 h-4" /> Advance Stage
                  </button>
                  <button
                    onClick={() => {
                      setApprovalActionType('REJECT');
                      setShowApprovalModal(true);
                    }}
                    className="bg-red-600/20 hover:bg-red-600/40 text-red-300 border border-red-500/30 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all flex items-center gap-1.5"
                  >
                    Reject to Draft
                  </button>
                </>
              )}
              {currentRun.status === 'Locked' && (
                <span className="px-3 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-xl text-xs font-bold flex items-center gap-1">
                  <Lock className="w-3.5 h-3.5" /> Locked & Finalized
                </span>
              )}
            </div>
          </div>

          {/* Stepper Steps */}
          <div className="grid grid-cols-4 gap-4 relative">
            <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-700/80 flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold">1</div>
              <div>
                <div className="text-xs text-slate-400">Step 1</div>
                <div className="text-sm font-semibold text-slate-200">Calculated</div>
              </div>
            </div>
            <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-700/80 flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold">2</div>
              <div>
                <div className="text-xs text-slate-400">Step 2</div>
                <div className="text-sm font-semibold text-slate-200">Manager Approved</div>
              </div>
            </div>
            <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-700/80 flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold">3</div>
              <div>
                <div className="text-xs text-slate-400">Step 3</div>
                <div className="text-sm font-semibold text-slate-200">Finance Approved</div>
              </div>
            </div>
            <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-700/80 flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center font-bold">4</div>
              <div>
                <div className="text-xs text-slate-400">Step 4</div>
                <div className="text-sm font-semibold text-slate-200">Locked & Sealed</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Employee Payslip Register Table */}
      {loading ? (
        <div className="p-12 text-center text-slate-400">Loading payslip records...</div>
      ) : error ? (
        <div className="p-4 bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl flex items-center gap-3">
          <AlertCircle className="w-5 h-5" /> {error}
        </div>
      ) : employees.length === 0 ? (
        <div className="bg-slate-800/40 p-12 text-center rounded-2xl border border-slate-700/50 text-slate-400">
          No calculated payroll run found for this period.
        </div>
      ) : (
        <div className="bg-slate-800/40 rounded-2xl border border-slate-700/50 overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-800/80 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-700">
                <th className="p-4">Employee ID</th>
                <th className="p-4">Employee Name</th>
                <th className="p-4">Payable Days</th>
                <th className="p-4">Gross Earnings</th>
                <th className="p-4">Deductions</th>
                <th className="p-4">Net Take-Home</th>
                <th className="p-4 text-right">PDF Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50 text-sm text-slate-200">
              {employees.map((emp) => {
                const name = emp.employee ? `${emp.employee.first_name} ${emp.employee.last_name}` : 'Staff Member';
                return (
                  <tr key={emp.id} className="hover:bg-slate-700/20 transition-all">
                    <td className="p-4 font-mono text-sky-400">EMP-00{emp.employee_id}</td>
                    <td className="p-4 font-medium text-slate-100">{name}</td>
                    <td className="p-4 text-slate-400">{emp.payable_days} / {emp.total_days}</td>
                    <td className="p-4 font-semibold text-slate-200">₹{emp.gross_salary.toLocaleString()}</td>
                    <td className="p-4 text-red-400">₹{emp.total_deductions.toLocaleString()}</td>
                    <td className="p-4 font-bold text-emerald-400">₹{emp.net_salary.toLocaleString()}</td>
                    <td className="p-4 text-right space-x-2">
                      <button
                        onClick={() => handlePreviewPdf(emp.employee_id, name)}
                        className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg text-xs font-medium transition-all inline-flex items-center gap-1"
                      >
                        <Eye className="w-3.5 h-3.5 text-sky-400" /> Preview
                      </button>
                      <button
                        onClick={() => handleDownloadSinglePdf(emp.employee_id, name)}
                        className="px-3 py-1.5 bg-sky-600/30 hover:bg-sky-600/50 text-sky-300 rounded-lg text-xs font-medium border border-sky-500/30 transition-all inline-flex items-center gap-1"
                      >
                        <Download className="w-3.5 h-3.5" /> PDF
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* PDF PREVIEW MODAL */}
      {previewPdfUrl && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-700/80 rounded-2xl max-w-4xl w-full h-[85vh] flex flex-col shadow-2xl overflow-hidden">
            <div className="flex justify-between items-center p-4 border-b border-slate-700 bg-slate-800/80">
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <FileText className="w-5 h-5 text-sky-400" /> Payslip Document: {previewEmployeeName}
              </h3>
              <button
                onClick={() => setPreviewPdfUrl(null)}
                className="text-slate-400 hover:text-slate-100 transition-colors p-1"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="flex-1 bg-slate-950 p-2">
              <iframe src={previewPdfUrl} className="w-full h-full rounded-xl border border-slate-800" title="Payslip PDF" />
            </div>
          </div>
        </div>
      )}

      {/* APPROVAL MODAL */}
      {showApprovalModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-700/80 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
              <UserCheck className="w-5 h-5 text-emerald-400" /> Confirm Approval Action
            </h2>
            <form onSubmit={submitApprovalAction} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Action</label>
                <input
                  type="text"
                  value={approvalActionType}
                  disabled
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-slate-300 text-sm font-bold"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Audit Remarks / Comments</label>
                <textarea
                  value={approvalRemarks}
                  onChange={(e) => setApprovalRemarks(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 text-sm"
                  placeholder="Verified variance report and statutory deductions..."
                  rows={3}
                  required
                />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowApprovalModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl text-sm"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className={`px-4 py-2 rounded-xl text-sm font-medium text-white ${
                    approvalActionType === 'APPROVE' ? 'bg-emerald-600 hover:bg-emerald-500' : 'bg-red-600 hover:bg-red-500'
                  }`}
                >
                  Confirm {approvalActionType}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
