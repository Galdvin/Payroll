import React, { useEffect, useState } from 'react';
import { leaveService } from '../services/leaveService';
import { employeeService } from '../services/employeeService';
import { LeaveBalance, LeaveRequest, Holiday } from '../types/leave';
import { Employee } from '../types/employee';
import { CalendarCheck, Plus, CheckCircle, XCircle, Clock, Calendar, Check, X, Palmtree } from 'lucide-react';

export const LeavesPage: React.FC = () => {
  const [balances, setBalances] = useState<LeaveBalance[]>([]);
  const [requests, setRequests] = useState<LeaveRequest[]>([]);
  const [holidays, setHolidays] = useState<Holiday[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [activeTab, setActiveTab] = useState<'balances' | 'requests' | 'holidays'>('requests');
  const [isLoading, setIsLoading] = useState(true);

  // Apply Leave Modal
  const [showApplyModal, setShowApplyModal] = useState(false);
  const [applyEmpId, setApplyEmpId] = useState<number>(1);
  const [leaveTypeId, setLeaveTypeId] = useState<number>(1);
  const [startDate, setStartDate] = useState('2024-10-01');
  const [endDate, setEndDate] = useState('2024-10-03');
  const [reason, setReason] = useState('');

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [empRes, reqRes, holRes] = await Promise.all([
        employeeService.getEmployees({ limit: 100 }),
        leaveService.getLeaveRequests(),
        leaveService.getHolidays(1),
      ]);
      setEmployees(empRes.items);
      setRequests(reqRes);
      setHolidays(holRes);

      if (empRes.items.length > 0) {
        setApplyEmpId(empRes.items[0].id);
        const bal = await leaveService.getLeaveBalances(empRes.items[0].id);
        setBalances(bal);
        if (bal.length > 0) setLeaveTypeId(bal[0].leave_type_id);
      }
    } catch (err) {
      console.error('Failed to load leave data', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleApplyLeave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await leaveService.applyLeave({
        employee_id: applyEmpId,
        leave_type_id: leaveTypeId,
        start_date: startDate,
        end_date: endDate,
        reason,
      });
      setShowApplyModal(false);
      setReason('');
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Failed to submit leave request');
    }
  };

  const handleApprove = async (id: number, status: 'Approved' | 'Rejected') => {
    try {
      await leaveService.approveLeave(id, status, status === 'Approved' ? 'Approved by HR Manager' : 'Rejected due to business requirements');
      loadData();
    } catch (err) {
      alert('Action failed');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center space-x-2">
            <Palmtree className="w-5 h-5 text-brand-400" />
            <span>Leave Management & Approval Portal</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">Leave quotas, application workflows, manager approvals, and holiday calendar</p>
        </div>

        <button
          onClick={() => setShowApplyModal(true)}
          className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-lg shadow-brand-500/20 transition"
        >
          <Plus className="w-4 h-4" />
          <span>Apply For Leave</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('requests')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeTab === 'requests' ? 'bg-brand-500/10 text-brand-400 border border-brand-500/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Clock className="w-4 h-4" />
          <span>Leave Requests ({requests.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('balances')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeTab === 'balances' ? 'bg-brand-500/10 text-brand-400 border border-brand-500/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <CalendarCheck className="w-4 h-4" />
          <span>Leave Balances</span>
        </button>

        <button
          onClick={() => setActiveTab('holidays')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeTab === 'holidays' ? 'bg-brand-500/10 text-brand-400 border border-brand-500/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Calendar className="w-4 h-4" />
          <span>Holiday Calendar ({holidays.length})</span>
        </button>
      </div>

      {/* Tab 1: Leave Requests & Approval Inbox */}
      {activeTab === 'requests' && (
        <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
          {isLoading ? (
            <div className="p-12 text-center text-slate-400 text-xs font-mono">Loading leave request inbox...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                  <tr>
                    <th className="py-3.5 px-4">Employee ID</th>
                    <th className="py-3.5 px-4">Leave Type</th>
                    <th className="py-3.5 px-4">Dates</th>
                    <th className="py-3.5 px-4">Days</th>
                    <th className="py-3.5 px-4">Reason</th>
                    <th className="py-3.5 px-4">Status</th>
                    <th className="py-3.5 px-4 text-right">Approval Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {requests.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="py-8 text-center text-slate-500 italic">No leave applications submitted yet.</td>
                    </tr>
                  ) : (
                    requests.map((req) => (
                      <tr key={req.id} className="hover:bg-slate-800/30 transition">
                        <td className="py-3.5 px-4 font-mono font-bold text-brand-400">EMP #{req.employee_id}</td>
                        <td className="py-3.5 px-4 font-semibold text-white">{req.leave_type.name}</td>
                        <td className="py-3.5 px-4 font-mono text-slate-300">{req.start_date} to {req.end_date}</td>
                        <td className="py-3.5 px-4 font-mono font-bold text-white">{req.total_days} Days</td>
                        <td className="py-3.5 px-4 text-slate-400 max-w-xs truncate">{req.reason || 'N/A'}</td>
                        <td className="py-3.5 px-4">
                          <span className={`px-2.5 py-0.5 rounded text-[10px] font-mono font-semibold ${
                            req.status === 'Approved'
                              ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-400'
                              : req.status === 'Rejected'
                              ? 'bg-red-500/10 border border-red-500/30 text-red-400'
                              : 'bg-amber-500/10 border border-amber-500/30 text-amber-400 animate-pulse'
                          }`}>
                            {req.status}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          {req.status === 'Pending' ? (
                            <div className="flex items-center justify-end space-x-1">
                              <button
                                onClick={() => handleApprove(req.id, 'Approved')}
                                className="p-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 transition"
                                title="Approve Leave"
                              >
                                <Check className="w-3.5 h-3.5" />
                              </button>
                              <button
                                onClick={() => handleApprove(req.id, 'Rejected')}
                                className="p-1.5 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-300 border border-red-500/30 transition"
                                title="Reject Leave"
                              >
                                <X className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          ) : (
                            <span className="text-slate-500 text-[11px] italic">Processed</span>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Balances */}
      {activeTab === 'balances' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {balances.map((b) => (
            <div key={b.id} className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-white text-sm">{b.leave_type.name}</span>
                <span className="px-2 py-0.5 rounded bg-brand-500/10 text-brand-400 font-mono text-[10px]">
                  {b.leave_type.code}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-2 text-center pt-2 border-t border-slate-800 font-mono">
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block">Accrued</span>
                  <span className="text-sm font-bold text-white">{b.accrued}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block">Used</span>
                  <span className="text-sm font-bold text-amber-400">{b.used}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block">Available</span>
                  <span className="text-sm font-bold text-emerald-400">{b.total_balance}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 3: Holidays */}
      {activeTab === 'holidays' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {holidays.map((h) => (
            <div key={h.id} className="glass-panel p-4 rounded-xl border border-slate-800 flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400 font-bold font-mono text-xs">
                HOL
              </div>
              <div>
                <h4 className="font-bold text-white text-xs">{h.name}</h4>
                <p className="text-[11px] text-slate-400 font-mono">{h.date} • {h.holiday_type}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Apply Leave Modal */}
      {showApplyModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-md p-6 rounded-2xl border border-slate-700 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white">Apply For Leave</h3>
            <form onSubmit={handleApplyLeave} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Select Employee</label>
                <select
                  value={applyEmpId}
                  onChange={(e) => setApplyEmpId(Number(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white"
                >
                  {employees.map((emp) => (
                    <option key={emp.id} value={emp.id}>{emp.first_name} {emp.last_name} ({emp.employee_code})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Leave Type</label>
                <select
                  value={leaveTypeId}
                  onChange={(e) => setLeaveTypeId(Number(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white"
                >
                  {balances.map((b) => (
                    <option key={b.leave_type_id} value={b.leave_type_id}>{b.leave_type.name} (Available: {b.total_balance})</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Start Date</label>
                  <input
                    type="date"
                    required
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">End Date</label>
                  <input
                    type="date"
                    required
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Reason</label>
                <textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white"
                  rows={2}
                  placeholder="Enter reason for leave..."
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowApplyModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300"
                >
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 rounded-lg bg-brand-600 text-white font-semibold shadow-md">
                  Submit Application
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
