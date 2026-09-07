import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { employeeService } from '../services/employeeService';
import { Employee, EmployeeHistory, EmployeeDocument } from '../types/employee';
import { ArrowLeft, User, CreditCard, Clock, FileText, Upload, ShieldCheck, Mail, Calendar, Building2 } from 'lucide-react';

export const EmployeeDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const employeeId = Number(id);

  const [employee, setEmployee] = useState<Employee | null>(null);
  const [history, setHistory] = useState<EmployeeHistory[]>([]);
  const [documents, setDocuments] = useState<EmployeeDocument[]>([]);
  const [activeTab, setActiveTab] = useState<'profile' | 'financial' | 'history' | 'documents'>('profile');
  const [isLoading, setIsLoading] = useState(true);

  // Document Upload state
  const [docType, setDocType] = useState('Offer Letter');
  const [docTitle, setDocTitle] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const loadProfile = async () => {
    if (!employeeId) return;
    setIsLoading(true);
    try {
      const [emp, hist, docs] = await Promise.all([
        employeeService.getEmployeeById(employeeId),
        employeeService.getEmployeeHistory(employeeId),
        employeeService.getEmployeeDocuments(employeeId),
      ]);
      setEmployee(emp);
      setHistory(hist);
      setDocuments(docs);
    } catch (err) {
      console.error('Failed to load employee details', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, [employeeId]);

  const handleUploadDoc = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile || !docTitle) return;
    const formData = new FormData();
    formData.append('document_type', docType);
    formData.append('title', docTitle);
    formData.append('file', selectedFile);

    try {
      await employeeService.uploadEmployeeDocument(employeeId, formData);
      setDocTitle('');
      setSelectedFile(null);
      loadProfile();
    } catch (err) {
      alert('Document upload failed');
    }
  };

  if (isLoading) {
    return <div className="p-12 text-center text-slate-400 text-xs font-mono">Loading profile data...</div>;
  }

  if (!employee) {
    return <div className="p-12 text-center text-red-400 text-sm">Employee profile not found.</div>;
  }

  return (
    <div className="space-y-6">
      {/* Top Bar */}
      <button
        onClick={() => navigate('/employees')}
        className="inline-flex items-center space-x-2 text-xs text-slate-400 hover:text-white transition"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Employee Directory</span>
      </button>

      {/* Employee Profile Header Card */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600 via-brand-500 to-sky-400 flex items-center justify-center font-bold text-white text-2xl uppercase shadow-lg shadow-brand-500/20">
            {employee.first_name[0]}{employee.last_name[0]}
          </div>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-xl font-bold text-white">{employee.first_name} {employee.last_name}</h1>
              <span className="px-2.5 py-0.5 rounded bg-brand-500/10 border border-brand-500/30 text-brand-300 font-mono text-xs font-bold">
                {employee.employee_code}
              </span>
            </div>
            <div className="flex items-center space-x-4 text-xs text-slate-400 mt-1 font-mono">
              <span className="flex items-center"><Mail className="w-3.5 h-3.5 mr-1 text-slate-500" /> {employee.work_email}</span>
              <span>•</span>
              <span className="flex items-center"><Calendar className="w-3.5 h-3.5 mr-1 text-slate-500" /> Joined: {employee.joining_date}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <span className={`px-3 py-1 rounded-full text-xs font-mono font-bold ${
            employee.status === 'Active' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'bg-amber-500/20 text-amber-300'
          }`}>
            {employee.status}
          </span>
          <span className="px-3 py-1 rounded-full bg-slate-800 text-slate-300 text-xs font-mono">
            {employee.employment_type}
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('profile')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeTab === 'profile' ? 'bg-brand-500/10 text-brand-400 border border-brand-500/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <User className="w-4 h-4" />
          <span>Profile Info</span>
        </button>

        <button
          onClick={() => setActiveTab('financial')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeTab === 'financial' ? 'bg-brand-500/10 text-brand-400 border border-brand-500/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <CreditCard className="w-4 h-4" />
          <span>Bank & Tax Details</span>
        </button>

        <button
          onClick={() => setActiveTab('history')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeTab === 'history' ? 'bg-brand-500/10 text-brand-400 border border-brand-500/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Clock className="w-4 h-4" />
          <span>History Audit ({history.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('documents')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeTab === 'documents' ? 'bg-brand-500/10 text-brand-400 border border-brand-500/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Documents ({documents.length})</span>
        </button>
      </div>

      {/* Tab Panels */}
      {activeTab === 'profile' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-white">Personal Information</h3>
            <div className="space-y-2.5 text-xs">
              <div className="flex justify-between py-1.5 border-b border-slate-800"><span className="text-slate-400">Gender</span><span className="text-white font-medium">{employee.gender}</span></div>
              <div className="flex justify-between py-1.5 border-b border-slate-800"><span className="text-slate-400">Date of Birth</span><span className="text-white font-mono">{employee.date_of_birth}</span></div>
              <div className="flex justify-between py-1.5 border-b border-slate-800"><span className="text-slate-400">Nationality</span><span className="text-white">{employee.nationality}</span></div>
              <div className="flex justify-between py-1.5"><span className="text-slate-400">Personal Email</span><span className="text-white font-mono">{employee.personal_email || 'N/A'}</span></div>
            </div>
          </div>

          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-white">Organizational Scope</h3>
            <div className="space-y-2.5 text-xs">
              <div className="flex justify-between py-1.5 border-b border-slate-800"><span className="text-slate-400">Organization ID</span><span className="text-brand-400 font-mono">Org #{employee.organization_id}</span></div>
              <div className="flex justify-between py-1.5 border-b border-slate-800"><span className="text-slate-400">Company ID</span><span className="text-brand-400 font-mono">Comp #{employee.company_id}</span></div>
              <div className="flex justify-between py-1.5 border-b border-slate-800"><span className="text-slate-400">Department</span><span className="text-white">{employee.department?.name || 'Human Resources'}</span></div>
              <div className="flex justify-between py-1.5"><span className="text-slate-400">Payroll Currency</span><span className="text-emerald-400 font-mono">{employee.currency}</span></div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'financial' && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4 max-w-xl">
          <h3 className="text-sm font-bold text-white">Bank & Tax Account Metadata</h3>
          <div className="space-y-3 text-xs">
            <div className="flex justify-between py-2 border-b border-slate-800"><span className="text-slate-400">Tax Identifier (PAN / SSN)</span><span className="text-white font-mono font-bold">{employee.tax_identifier || 'PANXXXXXX12'}</span></div>
            <div className="flex justify-between py-2 border-b border-slate-800"><span className="text-slate-400">Bank Account Number</span><span className="text-white font-mono">{employee.bank_details?.account_number || '•••• •••• 9842'}</span></div>
            <div className="flex justify-between py-2 border-b border-slate-800"><span className="text-slate-400">Bank Name</span><span className="text-white">{employee.bank_details?.bank_name || 'HDFC Bank'}</span></div>
            <div className="flex justify-between py-2"><span className="text-slate-400">IFSC / Swift Code</span><span className="text-brand-400 font-mono">{employee.bank_details?.ifsc_code || 'HDFC0001234'}</span></div>
          </div>
        </div>
      )}

      {activeTab === 'history' && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-white">Chronological Audit History Trail</h3>
          <div className="space-y-3">
            {history.map((h) => (
              <div key={h.id} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 text-xs flex items-start space-x-3">
                <div className="w-8 h-8 rounded-lg bg-brand-500/10 border border-brand-500/30 flex items-center justify-center text-brand-400 font-bold font-mono text-[10px] flex-shrink-0">
                  HIST
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white font-mono">{h.change_type}</span>
                    <span className="text-slate-500 font-mono text-[10px]">{h.effective_date}</span>
                  </div>
                  <p className="text-slate-400 mt-1">{h.remarks}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'documents' && (
        <div className="space-y-6">
          {/* Upload Box */}
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
            <h4 className="text-xs font-bold text-white">Attach Employee Document</h4>
            <form onSubmit={handleUploadDoc} className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
              <select
                value={docType}
                onChange={(e) => setDocType(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded-lg p-2 text-white"
              >
                <option value="Offer Letter">Offer Letter</option>
                <option value="Appointment Letter">Appointment Letter</option>
                <option value="Tax Document">Tax Document</option>
                <option value="ID Document">ID Document</option>
              </select>
              <input
                type="text"
                required
                placeholder="Document Title (e.g. Signed Offer Letter)"
                value={docTitle}
                onChange={(e) => setDocTitle(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded-lg p-2 text-white"
              />
              <input
                type="file"
                required
                onChange={(e) => setSelectedFile(e.target.files ? e.target.files[0] : null)}
                className="bg-slate-900 border border-slate-700 rounded-lg p-1.5 text-slate-300 text-[11px]"
              />
              <button type="submit" className="bg-brand-600 hover:bg-brand-500 text-white font-semibold rounded-lg p-2 flex items-center justify-center space-x-1">
                <Upload className="w-3.5 h-3.5" />
                <span>Upload</span>
              </button>
            </form>
          </div>

          {/* Document list */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {documents.map((doc) => (
              <div key={doc.id} className="glass-panel p-4 rounded-xl border border-slate-800 flex items-center space-x-3">
                <FileText className="w-8 h-8 text-brand-400 flex-shrink-0" />
                <div className="truncate">
                  <h5 className="font-bold text-white text-xs truncate">{doc.title}</h5>
                  <p className="text-[10px] text-slate-400 font-mono">{doc.document_type} • v{doc.version}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
