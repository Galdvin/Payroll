import React, { useEffect, useState } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  Lock,
  Search,
  Eye,
  X,
  AlertCircle,
  Hash,
  Activity,
} from 'lucide-react';
import { auditService } from '../services/auditService';
import { AuditLogRow, AuditIntegrityResponse } from '../types/audit';

export const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogRow[]>([]);
  const [totalLogs, setTotalLogs] = useState(0);
  const [integrityStatus, setIntegrityStatus] = useState<AuditIntegrityResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [selectedModule, setSelectedModule] = useState<string>('');
  const [selectedDiffRow, setSelectedDiffRow] = useState<AuditLogRow | null>(null);

  useEffect(() => {
    loadAuditLogs();
    handleVerifyIntegrity();
  }, [selectedModule]);

  const loadAuditLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await auditService.getLogs(selectedModule || undefined);
      setLogs(data.logs);
      setTotalLogs(data.total);
    } catch (err: any) {
      setError(err?.response?.data?.message || 'Failed to fetch audit trail');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyIntegrity = async () => {
    setVerifying(true);
    try {
      const res = await auditService.verifyIntegrity();
      setIntegrityStatus(res);
    } catch (err: any) {
      console.error('Integrity check failed', err);
    } finally {
      setVerifying(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex justify-between items-center bg-slate-800/60 p-6 rounded-2xl border border-slate-700/50 backdrop-blur-md">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-3">
            <Lock className="w-8 h-8 text-emerald-400" />
            Security & Cryptographic Audit Trail
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Tamper-proof SHA-256 hash-chained audit logging tracking all state mutations, payroll calculations, and financial approvals.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={selectedModule}
            onChange={(e) => setSelectedModule(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-100 px-4 py-2 rounded-xl text-sm font-medium focus:border-emerald-500"
          >
            <option value="">All Security Modules</option>
            <option value="PAYROLL">Payroll Calculations</option>
            <option value="FINANCIAL_EXTRAS">Loans & Bonuses</option>
            <option value="APPROVALS">Approval Chain</option>
            <option value="EMPLOYEE">Staff Management</option>
          </select>
          <button
            onClick={handleVerifyIntegrity}
            disabled={verifying}
            className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 shadow-lg shadow-emerald-600/20"
          >
            <ShieldCheck className="w-4 h-4" /> {verifying ? 'Verifying Chain...' : 'Verify Cryptographic Chain'}
          </button>
        </div>
      </div>

      {/* Integrity Verification Status Bar */}
      {integrityStatus && (
        <div
          className={`p-4 rounded-2xl border flex items-center justify-between transition-all ${
            integrityStatus.is_intact
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
              : 'bg-red-500/10 border-red-500/30 text-red-400'
          }`}
        >
          <div className="flex items-center gap-3">
            {integrityStatus.is_intact ? (
              <CheckCircle2 className="w-6 h-6 text-emerald-400 flex-shrink-0" />
            ) : (
              <ShieldAlert className="w-6 h-6 text-red-400 flex-shrink-0" />
            )}
            <div>
              <div className="font-bold text-sm">
                {integrityStatus.is_intact
                  ? 'SHA-256 Audit Chain Verification Intact & Tamper-Proof'
                  : 'WARNING: Cryptographic Hash Mismatch Detected'}
              </div>
              <div className="text-xs opacity-80 mt-0.5">
                {integrityStatus.is_intact
                  ? `Verified ${integrityStatus.total_entries} historical log entries across sequential block hashes.`
                  : `Tampering detected at entry ID #${integrityStatus.tampered_entry_id}.`}
              </div>
            </div>
          </div>
          <span className="font-mono text-xs px-3 py-1 bg-slate-900/60 rounded-xl border border-slate-700">
            Hash Method: SHA-256 Chaining
          </span>
        </div>
      )}

      {/* Audit Log Register Table */}
      {loading ? (
        <div className="p-12 text-center text-slate-400">Loading audit trail records...</div>
      ) : error ? (
        <div className="p-4 bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl flex items-center gap-3">
          <AlertCircle className="w-5 h-5" /> {error}
        </div>
      ) : (
        <div className="bg-slate-800/40 rounded-2xl border border-slate-700/50 overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-800/80 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-700">
                <th className="p-4">Log ID</th>
                <th className="p-4">User Email</th>
                <th className="p-4">Module</th>
                <th className="p-4">Action</th>
                <th className="p-4">Record ID</th>
                <th className="p-4">SHA-256 Checksum</th>
                <th className="p-4 text-right">Inspect State Diff</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50 text-sm text-slate-200">
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-slate-500">
                    No audit records captured yet.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-700/20 transition-all">
                    <td className="p-4 font-mono text-emerald-400">#{log.id}</td>
                    <td className="p-4 text-slate-300 font-medium">{log.user_email || 'System'}</td>
                    <td className="p-4">
                      <span className="px-2.5 py-0.5 bg-slate-700 text-slate-300 rounded text-xs font-semibold">
                        {log.module}
                      </span>
                    </td>
                    <td className="p-4 font-semibold text-slate-100">{log.action}</td>
                    <td className="p-4 font-mono text-sky-400">{log.record_id || 'N/A'}</td>
                    <td className="p-4 font-mono text-xs text-slate-400 truncate max-w-[140px]" title={log.hash_checksum}>
                      {log.hash_checksum ? `${log.hash_checksum.slice(0, 16)}...` : 'N/A'}
                    </td>
                    <td className="p-4 text-right">
                      <button
                        onClick={() => setSelectedDiffRow(log)}
                        className="px-3 py-1 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg text-xs font-medium transition-all inline-flex items-center gap-1"
                      >
                        <Eye className="w-3.5 h-3.5 text-emerald-400" /> Diff Viewer
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* JSON DIFF MODAL */}
      {selectedDiffRow && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-700/80 rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-4">
            <div className="flex justify-between items-center border-b border-slate-700 pb-3">
              <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <Activity className="w-5 h-5 text-emerald-400" /> Audit Log Diff Inspection #{selectedDiffRow.id}
              </h3>
              <button onClick={() => setSelectedDiffRow(null)} className="text-slate-400 hover:text-slate-100">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <div className="font-bold text-slate-400 mb-1 uppercase">Previous State (Old Values)</div>
                <pre className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-red-300 font-mono overflow-x-auto max-h-60">
                  {JSON.stringify(selectedDiffRow.old_values || {}, null, 2)}
                </pre>
              </div>
              <div>
                <div className="font-bold text-slate-400 mb-1 uppercase">Updated State (New Values)</div>
                <pre className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-emerald-300 font-mono overflow-x-auto max-h-60">
                  {JSON.stringify(selectedDiffRow.new_values || {}, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
