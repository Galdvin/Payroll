import React, { useEffect, useState } from 'react';
import { attendanceService } from '../services/attendanceService';
import { employeeService } from '../services/employeeService';
import { Attendance, Shift, AttendanceSummary } from '../types/attendance';
import { Employee } from '../types/employee';
import { CalendarCheck, Clock, Plus, CheckCircle, AlertCircle, Calculator, User } from 'lucide-react';

export const AttendancePage: React.FC = () => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [attendanceRecords, setAttendanceRecords] = useState<Attendance[]>([]);
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [selectedEmpId, setSelectedEmpId] = useState<number | undefined>(undefined);
  const [summary, setSummary] = useState<AttendanceSummary | null>(null);
  const [activeTab, setActiveTab] = useState<'daily' | 'shifts' | 'summary'>('daily');
  const [isLoading, setIsLoading] = useState(true);

  // Check-In Modal state
  const [showCheckInModal, setShowCheckInModal] = useState(false);
  const [checkInEmpId, setCheckInEmpId] = useState<number>(1);
  const [checkInTime, setCheckInTime] = useState('2024-09-10T09:00:00Z');
  const [attDate, setAttDate] = useState('2024-09-10');

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [empRes, attRes, shiftRes] = await Promise.all([
        employeeService.getEmployees({ limit: 100 }),
        attendanceService.getAttendanceRecords(),
        attendanceService.getShifts(1),
      ]);
      setEmployees(empRes.items);
      setAttendanceRecords(attRes);
      setShifts(shiftRes);
      if (empRes.items.length > 0) {
        setSelectedEmpId(empRes.items[0].id);
        setCheckInEmpId(empRes.items[0].id);
      }
    } catch (err) {
      console.error('Failed to load attendance data', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const loadSummaryForEmp = async (empId: number) => {
    try {
      const s = await attendanceService.getAttendanceSummary(empId, '2024-09');
      setSummary(s);
    } catch (err) {
      console.error('Failed to load summary', err);
    }
  };

  const handleCheckInSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await attendanceService.checkIn(checkInEmpId, checkInTime, attDate);
      setShowCheckInModal(false);
      loadData();
    } catch (err) {
      alert('Check-in failed');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center space-x-2">
            <CalendarCheck className="w-5 h-5 text-brand-400" />
            <span>Attendance & Shift Management Console</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">Daily timekeeping, biometric sync, overtime hours, and payroll payable days feeder</p>
        </div>

        <button
          onClick={() => setShowCheckInModal(true)}
          className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-lg shadow-brand-500/20 transition"
        >
          <Clock className="w-4 h-4" />
          <span>Record Daily Punch</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('daily')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeTab === 'daily' ? 'bg-brand-500/10 text-brand-400 border border-brand-500/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Clock className="w-4 h-4" />
          <span>Daily Roster ({attendanceRecords.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('shifts')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeTab === 'shifts' ? 'bg-brand-500/10 text-brand-400 border border-brand-500/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <CalendarCheck className="w-4 h-4" />
          <span>Shift Rules ({shifts.length})</span>
        </button>

        <button
          onClick={() => {
            setActiveTab('summary');
            if (selectedEmpId) loadSummaryForEmp(selectedEmpId);
          }}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeTab === 'summary' ? 'bg-brand-500/10 text-brand-400 border border-brand-500/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Calculator className="w-4 h-4" />
          <span>Payroll Payable Days Feeder</span>
        </button>
      </div>

      {/* Tab 1: Daily Attendance Table */}
      {activeTab === 'daily' && (
        <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
          {isLoading ? (
            <div className="p-12 text-center text-slate-400 text-xs font-mono">Loading timekeeping roster...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                  <tr>
                    <th className="py-3.5 px-4">Date</th>
                    <th className="py-3.5 px-4">Employee ID</th>
                    <th className="py-3.5 px-4">Punch In</th>
                    <th className="py-3.5 px-4">Punch Out</th>
                    <th className="py-3.5 px-4">Status</th>
                    <th className="py-3.5 px-4">Overtime</th>
                    <th className="py-3.5 px-4">Source</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {attendanceRecords.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="py-8 text-center text-slate-500 italic">No attendance punches recorded yet. Click 'Record Daily Punch' above.</td>
                    </tr>
                  ) : (
                    attendanceRecords.map((att) => (
                      <tr key={att.id} className="hover:bg-slate-800/30 transition">
                        <td className="py-3.5 px-4 font-mono text-white font-semibold">{att.date}</td>
                        <td className="py-3.5 px-4 font-mono text-brand-400 font-bold">EMP #{att.employee_id}</td>
                        <td className="py-3.5 px-4 font-mono text-slate-300">
                          {att.check_in ? new Date(att.check_in).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '--:--'}
                        </td>
                        <td className="py-3.5 px-4 font-mono text-slate-300">
                          {att.check_out ? new Date(att.check_out).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '--:--'}
                        </td>
                        <td className="py-3.5 px-4">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                            att.status === 'Present' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/10 text-amber-400'
                          }`}>
                            {att.status}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 font-mono text-purple-400 font-bold">
                          {att.overtime_hours > 0 ? `+${att.overtime_hours} hrs` : '0 hrs'}
                        </td>
                        <td className="py-3.5 px-4 text-slate-400 text-[11px] font-mono">{att.source}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Shifts */}
      {activeTab === 'shifts' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-bold text-white text-sm">General Shift</span>
              <span className="px-2 py-0.5 rounded bg-brand-500/10 text-brand-400 text-[10px] font-mono">DAY</span>
            </div>
            <div className="text-xs text-slate-400 space-y-1 font-mono">
              <div>Timing: <strong className="text-white">09:00 - 18:00</strong></div>
              <div>Grace Period: 15 mins</div>
              <div>Break Duration: 60 mins</div>
            </div>
          </div>

          <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-bold text-white text-sm">Night Shift</span>
              <span className="px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 text-[10px] font-mono">NIGHT</span>
            </div>
            <div className="text-xs text-slate-400 space-y-1 font-mono">
              <div>Timing: <strong className="text-white">22:00 - 07:00</strong></div>
              <div>Grace Period: 15 mins</div>
              <div>Break Duration: 60 mins</div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Payroll Payable Days Feeder Summary */}
      {activeTab === 'summary' && (
        <div className="space-y-4">
          <div className="glass-panel p-4 rounded-xl border border-slate-800 flex items-center space-x-4">
            <span className="text-xs font-semibold text-slate-300">Select Employee:</span>
            <select
              value={selectedEmpId}
              onChange={(e) => {
                const id = Number(e.target.value);
                setSelectedEmpId(id);
                loadSummaryForEmp(id);
              }}
              className="bg-slate-900 border border-slate-700 rounded-lg py-1.5 px-3 text-xs text-white"
            >
              {employees.map((emp) => (
                <option key={emp.id} value={emp.id}>{emp.first_name} {emp.last_name} ({emp.employee_code})</option>
              ))}
            </select>
          </div>

          {summary && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="glass-panel p-5 rounded-2xl border border-slate-800">
                <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">Standard Month Days</span>
                <span className="text-2xl font-bold text-white font-mono">{summary.total_days} Days</span>
              </div>

              <div className="glass-panel p-5 rounded-2xl border border-slate-800">
                <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">Days Present</span>
                <span className="text-2xl font-bold text-emerald-400 font-mono">{summary.present_days} Days</span>
              </div>

              <div className="glass-panel p-5 rounded-2xl border border-slate-800">
                <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">Unpaid Absences</span>
                <span className="text-2xl font-bold text-red-400 font-mono">{summary.unpaid_leave_days + summary.absent_days} Days</span>
              </div>

              <div className="glass-panel p-5 rounded-2xl border border-brand-500/40 bg-brand-500/10">
                <span className="text-xs text-brand-300 uppercase tracking-wider font-semibold block mb-1">Net Payable Days for Payroll</span>
                <span className="text-2xl font-bold text-white font-mono">{summary.payable_days} Days</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Record Punch Modal */}
      {showCheckInModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-md p-6 rounded-2xl border border-slate-700 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white">Record Daily Punch</h3>
            <form onSubmit={handleCheckInSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Select Employee</label>
                <select
                  value={checkInEmpId}
                  onChange={(e) => setCheckInEmpId(Number(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white"
                >
                  {employees.map((emp) => (
                    <option key={emp.id} value={emp.id}>{emp.first_name} {emp.last_name} ({emp.employee_code})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Attendance Date</label>
                <input
                  type="date"
                  required
                  value={attDate}
                  onChange={(e) => setAttDate(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Punch In Timestamp</label>
                <input
                  type="datetime-local"
                  required
                  value={checkInTime.slice(0, 16)}
                  onChange={(e) => setCheckInTime(e.target.value + ':00Z')}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white font-mono"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCheckInModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300"
                >
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 rounded-lg bg-brand-600 text-white font-semibold shadow-md">
                  Record Punch
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
