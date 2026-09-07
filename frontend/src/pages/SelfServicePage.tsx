import React, { useEffect, useState } from 'react';
import {
  UserCheck,
  Users,
  FileText,
  Download,
  Calendar,
  CreditCard,
  CheckCircle2,
  XCircle,
  Clock,
  TrendingUp,
  AlertCircle,
  Briefcase,
} from 'lucide-react';
import { selfService } from '../services/selfService';
import { payslipService } from '../services/payslipService';
import {
  EssProfileResponse,
  EssPayslipRow,
  MssTeamMember,
  MssPendingLeave,
} from '../types/selfService';

export const SelfServicePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'ess' | 'mss'>('ess');
  
  // Data states
  const [profile, setProfile] = useState<EssProfileResponse | null>(null);
  const [myPayslips, setMyPayslips] = useState<EssPayslipRow[]>([]);
  const [teamMembers, setTeamMembers] = useState<MssTeamMember[]>([]);
  const [pendingLeaves, setPendingLeaves] = useState<MssPendingLeave[]>([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      if (activeTab === 'ess') {
        const prof = await selfService.getEssProfile();
        setProfile(prof);
        const slips = await selfService.getMyPayslips();
        setMyPayslips(slips);
      } else {
        const team = await selfService.getTeamMembers();
        setTeamMembers(team);
        const leaves = await selfService.getPendingTeamLeaves();
        setPendingLeaves(leaves);
      }
    } catch (err: any) {
      setError(err?.response?.data?.message || 'Failed to fetch self-service data');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = async (empId: number, periodId: number, periodName: string) => {
    try {
      const blob = await payslipService.downloadEmployeePayslipPdf(empId, periodId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Payslip_${periodName.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err: any) {
      alert('Failed to download PDF');
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner Header */}
      <div className="flex justify-between items-center bg-slate-800/60 p-6 rounded-2xl border border-slate-700/50 backdrop-blur-md">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-3">
            <UserCheck className="w-8 h-8 text-sky-400" />
            Employee & Manager Self Service (ESS / MSS)
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Access personal financial records, download monthly payslips, track leave balances, and manage team approvals.
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 border-b border-slate-700/50 pb-2">
        <button
          onClick={() => setActiveTab('ess')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
            activeTab === 'ess'
              ? 'bg-slate-700 text-sky-400 border border-slate-600'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <UserCheck className="w-4 h-4" /> Employee Portal (ESS)
        </button>
        <button
          onClick={() => setActiveTab('mss')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
            activeTab === 'mss'
              ? 'bg-slate-700 text-purple-400 border border-slate-600'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Users className="w-4 h-4" /> Manager Portal (MSS)
        </button>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-400">Loading self-service workspace...</div>
      ) : error ? (
        <div className="p-4 bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl flex items-center gap-3">
          <AlertCircle className="w-5 h-5" /> {error}
        </div>
      ) : (
        <div>
          {/* TAB 1: ESS PORTAL */}
          {activeTab === 'ess' && profile && (
            <div className="space-y-6">
              {/* Profile Card & Metrics */}
              <div className="grid grid-cols-3 gap-6">
                <div className="bg-slate-800/40 p-6 rounded-2xl border border-slate-700/50 col-span-1 space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center text-white font-bold text-lg shadow-lg">
                      {profile.full_name.charAt(0)}
                    </div>
                    <div>
                      <h3 className="font-bold text-slate-100">{profile.full_name}</h3>
                      <span className="text-xs font-mono text-sky-400">{profile.employee_code}</span>
                    </div>
                  </div>
                  <div className="border-t border-slate-700/60 pt-3 space-y-1.5 text-xs text-slate-300">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Department:</span>
                      <span className="font-semibold">{profile.department}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Designation:</span>
                      <span className="font-semibold">{profile.designation}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Email:</span>
                      <span className="font-mono text-slate-300">{profile.email}</span>
                    </div>
                  </div>
                </div>

                {/* YTD Metrics */}
                <div className="bg-slate-800/40 p-6 rounded-2xl border border-slate-700/50 col-span-2 grid grid-cols-3 gap-4">
                  <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1">
                    <div className="text-slate-400 text-xs font-medium uppercase">YTD Gross Earnings</div>
                    <div className="text-2xl font-bold text-amber-400">₹{profile.ytd_gross.toLocaleString()}</div>
                    <div className="text-[11px] text-slate-500">Cumulative total CTC</div>
                  </div>
                  <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1">
                    <div className="text-slate-400 text-xs font-medium uppercase">YTD Net Disbursed</div>
                    <div className="text-2xl font-bold text-emerald-400">₹{profile.ytd_net.toLocaleString()}</div>
                    <div className="text-[11px] text-slate-500">Net take-home payout</div>
                  </div>
                  <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-1">
                    <div className="text-slate-400 text-xs font-medium uppercase">Active Loan EMIs</div>
                    <div className="text-2xl font-bold text-sky-400">{profile.active_loans_count} Active</div>
                    <div className="text-[11px] text-slate-500">Deducted from payroll</div>
                  </div>
                </div>
              </div>

              {/* Leave Balances Grid */}
              <div className="bg-slate-800/40 p-6 rounded-2xl border border-slate-700/50 space-y-4">
                <h3 className="text-base font-bold text-slate-200 flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-sky-400" /> Leave Balances Summary
                </h3>
                <div className="grid grid-cols-3 gap-4">
                  {profile.leave_balances.map((b, idx) => (
                    <div key={idx} className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 flex justify-between items-center">
                      <div>
                        <div className="text-sm font-semibold text-slate-100">{b.leave_type}</div>
                        <div className="text-xs text-slate-400">Allocated: {b.allocated} days</div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-emerald-400">{b.remaining} Days</div>
                        <div className="text-[10px] text-slate-500">Used: {b.used} days</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Personal Payslips Table */}
              <div className="bg-slate-800/40 rounded-2xl border border-slate-700/50 overflow-hidden space-y-4 p-6">
                <h3 className="text-base font-bold text-slate-200 flex items-center gap-2">
                  <FileText className="w-5 h-5 text-sky-400" /> Historical Payslip Repository
                </h3>
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-800/80 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-700">
                      <th className="p-3">Pay Period</th>
                      <th className="p-3">Payable Days</th>
                      <th className="p-3">Gross Salary</th>
                      <th className="p-3">Deductions</th>
                      <th className="p-3">Net Take-Home</th>
                      <th className="p-3 text-right">Download</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700/50 text-sm text-slate-200">
                    {myPayslips.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="p-8 text-center text-slate-500">
                          No payslips issued yet.
                        </td>
                      </tr>
                    ) : (
                      myPayslips.map((slip) => (
                        <tr key={slip.payroll_employee_id} className="hover:bg-slate-700/20 transition-all">
                          <td className="p-3 font-semibold text-slate-100">{slip.period_name} ({slip.year_month})</td>
                          <td className="p-3 text-slate-400">{slip.payable_days} Days</td>
                          <td className="p-3 font-semibold">₹{slip.gross_salary.toLocaleString()}</td>
                          <td className="p-3 text-red-400">₹{slip.total_deductions.toLocaleString()}</td>
                          <td className="p-3 font-bold text-emerald-400">₹{slip.net_salary.toLocaleString()}</td>
                          <td className="p-3 text-right">
                            <button
                              onClick={() => handleDownloadPdf(profile.employee_id, slip.period_id, slip.period_name)}
                              className="px-3 py-1 bg-sky-600/30 hover:bg-sky-600/50 text-sky-300 rounded-lg text-xs font-medium border border-sky-500/30 transition-all inline-flex items-center gap-1"
                            >
                              <Download className="w-3.5 h-3.5" /> PDF Payslip
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 2: MSS PORTAL */}
          {activeTab === 'mss' && (
            <div className="space-y-6">
              {/* Direct Reports Team Roster */}
              <div className="bg-slate-800/40 p-6 rounded-2xl border border-slate-700/50 space-y-4">
                <h3 className="text-base font-bold text-slate-200 flex items-center gap-2">
                  <Users className="w-5 h-5 text-purple-400" /> Direct Report Team Members
                </h3>
                <div className="grid grid-cols-3 gap-4">
                  {teamMembers.map((member) => (
                    <div key={member.employee_id} className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-2">
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-bold text-slate-100">{member.name}</div>
                          <div className="text-xs font-mono text-purple-400">{member.employee_code}</div>
                        </div>
                        <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded text-[10px] font-semibold">
                          Active
                        </span>
                      </div>
                      <div className="text-xs text-slate-400">
                        {member.designation} • {member.department}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Pending Team Leaves Inbox */}
              <div className="bg-slate-800/40 rounded-2xl border border-slate-700/50 overflow-hidden space-y-4 p-6">
                <h3 className="text-base font-bold text-slate-200 flex items-center gap-2">
                  <Clock className="w-5 h-5 text-amber-400" /> Pending Team Leave Requests
                </h3>
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-800/80 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-700">
                      <th className="p-3">Employee Name</th>
                      <th className="p-3">Leave Type</th>
                      <th className="p-3">Duration</th>
                      <th className="p-3">Days</th>
                      <th className="p-3">Reason</th>
                      <th className="p-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700/50 text-sm text-slate-200">
                    {pendingLeaves.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="p-8 text-center text-slate-500">
                          No pending team leave requests.
                        </td>
                      </tr>
                    ) : (
                      pendingLeaves.map((l) => (
                        <tr key={l.id} className="hover:bg-slate-700/20 transition-all">
                          <td className="p-3 font-semibold text-slate-100">{l.employee_name}</td>
                          <td className="p-3 text-sky-400 font-medium">{l.leave_type}</td>
                          <td className="p-3 text-slate-400">{l.start_date} to {l.end_date}</td>
                          <td className="p-3 font-bold text-amber-400">{l.total_days} Days</td>
                          <td className="p-3 text-slate-300 text-xs">{l.reason || 'N/A'}</td>
                          <td className="p-3 text-right space-x-2">
                            <button
                              onClick={() => alert('Leave approved.')}
                              className="px-3 py-1 bg-emerald-600/30 hover:bg-emerald-600/50 text-emerald-300 rounded-lg text-xs font-medium border border-emerald-500/30 transition-all inline-flex items-center gap-1"
                            >
                              <CheckCircle2 className="w-3.5 h-3.5" /> Approve
                            </button>
                            <button
                              onClick={() => alert('Leave rejected.')}
                              className="px-3 py-1 bg-red-600/30 hover:bg-red-600/50 text-red-300 rounded-lg text-xs font-medium border border-red-500/30 transition-all inline-flex items-center gap-1"
                            >
                              <XCircle className="w-3.5 h-3.5" /> Reject
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
