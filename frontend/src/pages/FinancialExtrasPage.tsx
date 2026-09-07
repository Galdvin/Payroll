import React, { useEffect, useState } from 'react';
import {
  CreditCard,
  Plus,
  DollarSign,
  Gift,
  Receipt,
  CheckCircle2,
  XCircle,
  FileText,
  TrendingUp,
  AlertCircle,
} from 'lucide-react';
import { financialExtrasService } from '../services/financialExtrasService';
import {
  Loan,
  Advance,
  BonusIncentive,
  Reimbursement,
  BonusType,
  ExpenseCategory,
} from '../types/financialExtras';

export const FinancialExtrasPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'loans' | 'advances' | 'bonuses' | 'reimbursements'>('loans');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Data states
  const [loans, setLoans] = useState<Loan[]>([]);
  const [advances, setAdvances] = useState<Advance[]>([]);
  const [bonuses, setBonuses] = useState<BonusIncentive[]>([]);
  const [reimbursements, setReimbursements] = useState<Reimbursement[]>([]);

  // Modals
  const [showLoanModal, setShowLoanModal] = useState(false);
  const [showAdvanceModal, setShowAdvanceModal] = useState(false);
  const [showBonusModal, setShowBonusModal] = useState(false);
  const [showReimbModal, setShowReimbModal] = useState(false);

  // Form states
  const [loanForm, setLoanForm] = useState({ employee_id: 1, principal_amount: 100000, interest_rate_annual: 12, tenure_months: 12, reason: '' });
  const [advanceForm, setAdvanceForm] = useState({ employee_id: 1, amount: 15000, reason: '' });
  const [bonusForm, setBonusForm] = useState({ employee_id: 1, bonus_type: 'PERFORMANCE' as BonusType, amount: 25000, is_taxable: true, remarks: '' });
  const [reimbForm, setReimbForm] = useState({
    employee_id: 1,
    claim_date: new Date().toISOString().split('T')[0],
    items: [{ expense_category: 'TRAVEL' as ExpenseCategory, amount: 2500, description: 'Client meeting transportation', receipt_url: '' }],
  });

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      if (activeTab === 'loans') {
        const data = await financialExtrasService.getLoans();
        setLoans(data);
      } else if (activeTab === 'advances') {
        const data = await financialExtrasService.getAdvances();
        setAdvances(data);
      } else if (activeTab === 'bonuses') {
        const data = await financialExtrasService.getBonuses();
        setBonuses(data);
      } else if (activeTab === 'reimbursements') {
        const data = await financialExtrasService.getReimbursements();
        setReimbursements(data);
      }
    } catch (err: any) {
      setError(err?.response?.data?.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateLoan = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await financialExtrasService.requestLoan(loanForm);
      setShowLoanModal(false);
      loadData();
    } catch (err: any) {
      alert(err?.response?.data?.message || 'Failed to submit loan request');
    }
  };

  const handleApproveLoan = async (loanId: number) => {
    try {
      await financialExtrasService.approveLoan(loanId);
      loadData();
    } catch (err: any) {
      alert(err?.response?.data?.message || 'Failed to approve loan');
    }
  };

  const handleCreateAdvance = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await financialExtrasService.requestAdvance(advanceForm);
      setShowAdvanceModal(false);
      loadData();
    } catch (err: any) {
      alert(err?.response?.data?.message || 'Failed to request advance');
    }
  };

  const handleCreateBonus = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await financialExtrasService.createBonus(bonusForm);
      setShowBonusModal(false);
      loadData();
    } catch (err: any) {
      alert(err?.response?.data?.message || 'Failed to issue bonus');
    }
  };

  const handleCreateReimb = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await financialExtrasService.createReimbursement(reimbForm);
      setShowReimbModal(false);
      loadData();
    } catch (err: any) {
      alert(err?.response?.data?.message || 'Failed to submit claim');
    }
  };

  const handleApproveReimb = async (id: number, status: 'APPROVED' | 'REJECTED') => {
    try {
      await financialExtrasService.approveReimbursement(id, { status, remarks: 'Verified by HR Admin' });
      loadData();
    } catch (err: any) {
      alert(err?.response?.data?.message || 'Failed to update reimbursement');
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner Header */}
      <div className="flex justify-between items-center bg-slate-800/60 p-6 rounded-2xl border border-slate-700/50 backdrop-blur-md">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-3">
            <DollarSign className="w-8 h-8 text-emerald-400" />
            Financial Extras & Variable Pay
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Manage Employee Loans, Emergency Advances, Bonuses, and Expense Reimbursements directly tied into monthly payroll deductions.
          </p>
        </div>
        <div className="flex gap-2">
          {activeTab === 'loans' && (
            <button
              onClick={() => setShowLoanModal(true)}
              className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-2 shadow-lg shadow-emerald-600/20"
            >
              <Plus className="w-4 h-4" /> Request Loan
            </button>
          )}
          {activeTab === 'advances' && (
            <button
              onClick={() => setShowAdvanceModal(true)}
              className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-2 shadow-lg shadow-blue-600/20"
            >
              <Plus className="w-4 h-4" /> Request Advance
            </button>
          )}
          {activeTab === 'bonuses' && (
            <button
              onClick={() => setShowBonusModal(true)}
              className="bg-amber-600 hover:bg-amber-500 text-white px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-2 shadow-lg shadow-amber-600/20"
            >
              <Plus className="w-4 h-4" /> Issue Bonus
            </button>
          )}
          {activeTab === 'reimbursements' && (
            <button
              onClick={() => setShowReimbModal(true)}
              className="bg-purple-600 hover:bg-purple-500 text-white px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-2 shadow-lg shadow-purple-600/20"
            >
              <Plus className="w-4 h-4" /> Submit Claim
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 border-b border-slate-700/50 pb-2">
        <button
          onClick={() => setActiveTab('loans')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
            activeTab === 'loans' ? 'bg-slate-700 text-emerald-400 border border-slate-600' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <CreditCard className="w-4 h-4" /> Loans & EMIs
        </button>
        <button
          onClick={() => setActiveTab('advances')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
            activeTab === 'advances' ? 'bg-slate-700 text-blue-400 border border-slate-600' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <TrendingUp className="w-4 h-4" /> Salary Advances
        </button>
        <button
          onClick={() => setActiveTab('bonuses')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
            activeTab === 'bonuses' ? 'bg-slate-700 text-amber-400 border border-slate-600' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Gift className="w-4 h-4" /> Bonuses & Incentives
        </button>
        <button
          onClick={() => setActiveTab('reimbursements')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
            activeTab === 'reimbursements' ? 'bg-slate-700 text-purple-400 border border-slate-600' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Receipt className="w-4 h-4" /> Expense Claims
        </button>
      </div>

      {/* Content Area */}
      {loading ? (
        <div className="p-12 text-center text-slate-400">Loading financial records...</div>
      ) : error ? (
        <div className="p-4 bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl flex items-center gap-3">
          <AlertCircle className="w-5 h-5" /> {error}
        </div>
      ) : (
        <div>
          {/* TAB 1: LOANS */}
          {activeTab === 'loans' && (
            <div className="bg-slate-800/40 rounded-2xl border border-slate-700/50 overflow-hidden">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-800/80 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-700">
                    <th className="p-4">Loan ID</th>
                    <th className="p-4">Employee ID</th>
                    <th className="p-4">Principal Amount</th>
                    <th className="p-4">Interest Rate</th>
                    <th className="p-4">Tenure</th>
                    <th className="p-4">Monthly EMI</th>
                    <th className="p-4">Remaining Balance</th>
                    <th className="p-4">Status</th>
                    <th className="p-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/50 text-sm text-slate-200">
                  {loans.length === 0 ? (
                    <tr>
                      <td colSpan={9} className="p-8 text-center text-slate-500">
                        No loans recorded yet.
                      </td>
                    </tr>
                  ) : (
                    loans.map((loan) => (
                      <tr key={loan.id} className="hover:bg-slate-700/20 transition-all">
                        <td className="p-4 font-mono text-emerald-400">#LN-{loan.id}</td>
                        <td className="p-4 font-mono text-slate-300">EMP-00{loan.employee_id}</td>
                        <td className="p-4 font-semibold">₹{loan.principal_amount.toLocaleString()}</td>
                        <td className="p-4 text-slate-400">{loan.interest_rate_annual}% / yr</td>
                        <td className="p-4">{loan.tenure_months} months</td>
                        <td className="p-4 text-emerald-400 font-medium">₹{loan.monthly_emi.toLocaleString()}</td>
                        <td className="p-4 text-amber-400">₹{loan.remaining_balance.toLocaleString()}</td>
                        <td className="p-4">
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-semibold ${
                              loan.status === 'APPROVED' || loan.status === 'DISBURSED'
                                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                                : loan.status === 'PENDING'
                                ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                                : 'bg-slate-700 text-slate-400'
                            }`}
                          >
                            {loan.status}
                          </span>
                        </td>
                        <td className="p-4 text-right">
                          {loan.status === 'PENDING' && (
                            <button
                              onClick={() => handleApproveLoan(loan.id)}
                              className="px-3 py-1 bg-emerald-600/30 hover:bg-emerald-600/50 text-emerald-300 rounded-lg text-xs font-medium border border-emerald-500/30 transition-all"
                            >
                              Approve
                            </button>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* TAB 2: ADVANCES */}
          {activeTab === 'advances' && (
            <div className="bg-slate-800/40 rounded-2xl border border-slate-700/50 overflow-hidden">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-800/80 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-700">
                    <th className="p-4">Advance ID</th>
                    <th className="p-4">Employee ID</th>
                    <th className="p-4">Amount</th>
                    <th className="p-4">Request Date</th>
                    <th className="p-4">Reason</th>
                    <th className="p-4">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/50 text-sm text-slate-200">
                  {advances.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="p-8 text-center text-slate-500">
                        No salary advances requested.
                      </td>
                    </tr>
                  ) : (
                    advances.map((adv) => (
                      <tr key={adv.id} className="hover:bg-slate-700/20 transition-all">
                        <td className="p-4 font-mono text-blue-400">#ADV-{adv.id}</td>
                        <td className="p-4 font-mono text-slate-300">EMP-00{adv.employee_id}</td>
                        <td className="p-4 font-semibold text-emerald-400">₹{adv.amount.toLocaleString()}</td>
                        <td className="p-4 text-slate-400">{adv.request_date}</td>
                        <td className="p-4 text-slate-300">{adv.reason || 'N/A'}</td>
                        <td className="p-4">
                          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/30">
                            {adv.status}
                          </span>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* TAB 3: BONUSES */}
          {activeTab === 'bonuses' && (
            <div className="bg-slate-800/40 rounded-2xl border border-slate-700/50 overflow-hidden">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-800/80 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-700">
                    <th className="p-4">Bonus ID</th>
                    <th className="p-4">Employee ID</th>
                    <th className="p-4">Type</th>
                    <th className="p-4">Amount</th>
                    <th className="p-4">Taxable</th>
                    <th className="p-4">Remarks</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/50 text-sm text-slate-200">
                  {bonuses.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="p-8 text-center text-slate-500">
                        No bonus entries created yet.
                      </td>
                    </tr>
                  ) : (
                    bonuses.map((b) => (
                      <tr key={b.id} className="hover:bg-slate-700/20 transition-all">
                        <td className="p-4 font-mono text-amber-400">#BNS-{b.id}</td>
                        <td className="p-4 font-mono text-slate-300">EMP-00{b.employee_id}</td>
                        <td className="p-4">
                          <span className="px-3 py-1 bg-amber-500/10 text-amber-300 rounded-lg text-xs font-semibold border border-amber-500/30">
                            {b.bonus_type}
                          </span>
                        </td>
                        <td className="p-4 font-bold text-emerald-400">₹{b.amount.toLocaleString()}</td>
                        <td className="p-4">
                          {b.is_taxable ? (
                            <span className="text-red-400 text-xs bg-red-500/10 px-2 py-0.5 rounded border border-red-500/20">Yes (TDS Applies)</span>
                          ) : (
                            <span className="text-emerald-400 text-xs bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">Tax Exempt</span>
                          )}
                        </td>
                        <td className="p-4 text-slate-400">{b.remarks || 'N/A'}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* TAB 4: REIMBURSEMENTS */}
          {activeTab === 'reimbursements' && (
            <div className="bg-slate-800/40 rounded-2xl border border-slate-700/50 overflow-hidden">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-800/80 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-700">
                    <th className="p-4">Claim ID</th>
                    <th className="p-4">Employee ID</th>
                    <th className="p-4">Claim Date</th>
                    <th className="p-4">Items Count</th>
                    <th className="p-4">Total Amount</th>
                    <th className="p-4">Status</th>
                    <th className="p-4 text-right">Approval Inbox</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/50 text-sm text-slate-200">
                  {reimbursements.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="p-8 text-center text-slate-500">
                        No expense reimbursement claims submitted.
                      </td>
                    </tr>
                  ) : (
                    reimbursements.map((r) => (
                      <tr key={r.id} className="hover:bg-slate-700/20 transition-all">
                        <td className="p-4 font-mono text-purple-400">#CLM-{r.id}</td>
                        <td className="p-4 font-mono text-slate-300">EMP-00{r.employee_id}</td>
                        <td className="p-4 text-slate-400">{r.claim_date}</td>
                        <td className="p-4 text-slate-300">{r.items?.length || 0} expenses</td>
                        <td className="p-4 font-bold text-emerald-400">₹{r.total_amount.toLocaleString()}</td>
                        <td className="p-4">
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-semibold ${
                              r.status === 'APPROVED' || r.status === 'PAID'
                                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                                : r.status === 'SUBMITTED'
                                ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                                : 'bg-red-500/10 text-red-400 border border-red-500/30'
                            }`}
                          >
                            {r.status}
                          </span>
                        </td>
                        <td className="p-4 text-right space-x-2">
                          {r.status === 'SUBMITTED' && (
                            <>
                              <button
                                onClick={() => handleApproveReimb(r.id, 'APPROVED')}
                                className="px-3 py-1 bg-emerald-600/30 hover:bg-emerald-600/50 text-emerald-300 rounded-lg text-xs font-medium border border-emerald-500/30 transition-all inline-flex items-center gap-1"
                              >
                                <CheckCircle2 className="w-3.5 h-3.5" /> Approve
                              </button>
                              <button
                                onClick={() => handleApproveReimb(r.id, 'REJECTED')}
                                className="px-3 py-1 bg-red-600/30 hover:bg-red-600/50 text-red-300 rounded-lg text-xs font-medium border border-red-500/30 transition-all inline-flex items-center gap-1"
                              >
                                <XCircle className="w-3.5 h-3.5" /> Reject
                              </button>
                            </>
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

      {/* LOAN MODAL */}
      {showLoanModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-700/80 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
              <CreditCard className="w-5 h-5 text-emerald-400" /> Apply For Employee Loan
            </h2>
            <form onSubmit={handleCreateLoan} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Principal Amount (INR)</label>
                <input
                  type="number"
                  value={loanForm.principal_amount}
                  onChange={(e) => setLoanForm({ ...loanForm, principal_amount: Number(e.target.value) })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 text-sm"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Interest Rate (% p.a.)</label>
                  <input
                    type="number"
                    value={loanForm.interest_rate_annual}
                    onChange={(e) => setLoanForm({ ...loanForm, interest_rate_annual: Number(e.target.value) })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 text-sm"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Tenure (Months)</label>
                  <input
                    type="number"
                    value={loanForm.tenure_months}
                    onChange={(e) => setLoanForm({ ...loanForm, tenure_months: Number(e.target.value) })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 text-sm"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Reason / Purpose</label>
                <textarea
                  value={loanForm.reason}
                  onChange={(e) => setLoanForm({ ...loanForm, reason: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 text-sm"
                  rows={2}
                />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowLoanModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl text-sm"
                >
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-sm font-medium">
                  Submit Loan Request
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ADVANCE MODAL */}
      {showAdvanceModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-700/80 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-400" /> Request Salary Advance
            </h2>
            <form onSubmit={handleCreateAdvance} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Advance Amount (INR)</label>
                <input
                  type="number"
                  value={advanceForm.amount}
                  onChange={(e) => setAdvanceForm({ ...advanceForm, amount: Number(e.target.value) })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 text-sm"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Reason</label>
                <textarea
                  value={advanceForm.reason}
                  onChange={(e) => setAdvanceForm({ ...advanceForm, reason: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 text-sm"
                  rows={2}
                />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAdvanceModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl text-sm"
                >
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-sm font-medium">
                  Submit Request
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* BONUS MODAL */}
      {showBonusModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-700/80 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
              <Gift className="w-5 h-5 text-amber-400" /> Issue Variable Bonus
            </h2>
            <form onSubmit={handleCreateBonus} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Bonus Type</label>
                <select
                  value={bonusForm.bonus_type}
                  onChange={(e) => setBonusForm({ ...bonusForm, bonus_type: e.target.value as BonusType })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 text-sm"
                >
                  <option value="PERFORMANCE">Performance Bonus</option>
                  <option value="FESTIVAL">Festival / Annual Bonus</option>
                  <option value="RETENTION">Retention Bonus</option>
                  <option value="COMMISSION">Sales Commission</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Bonus Amount (INR)</label>
                <input
                  type="number"
                  value={bonusForm.amount}
                  onChange={(e) => setBonusForm({ ...bonusForm, amount: Number(e.target.value) })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 text-sm"
                  required
                />
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_taxable"
                  checked={bonusForm.is_taxable}
                  onChange={(e) => setBonusForm({ ...bonusForm, is_taxable: e.target.checked })}
                  className="rounded bg-slate-800 border-slate-700 text-amber-500"
                />
                <label htmlFor="is_taxable" className="text-xs text-slate-300">
                  Subject to TDS Tax Deduction
                </label>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Remarks</label>
                <input
                  type="text"
                  value={bonusForm.remarks}
                  onChange={(e) => setBonusForm({ ...bonusForm, remarks: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 text-sm"
                />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowBonusModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl text-sm"
                >
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-xl text-sm font-medium">
                  Issue Bonus
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* REIMBURSEMENT MODAL */}
      {showReimbModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-700/80 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
              <Receipt className="w-5 h-5 text-purple-400" /> Submit Expense Claim
            </h2>
            <form onSubmit={handleCreateReimb} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Category</label>
                <select
                  value={reimbForm.items[0].expense_category}
                  onChange={(e) =>
                    setReimbForm({
                      ...reimbForm,
                      items: [{ ...reimbForm.items[0], expense_category: e.target.value as ExpenseCategory }],
                    })
                  }
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 text-sm"
                >
                  <option value="TRAVEL">Travel & Flights</option>
                  <option value="MEALS">Client Meals</option>
                  <option value="SUPPLIES">Office Supplies</option>
                  <option value="INTERNET">Internet Allowance</option>
                  <option value="TRAINING">Training / Certifications</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Claim Amount (INR)</label>
                <input
                  type="number"
                  value={reimbForm.items[0].amount}
                  onChange={(e) =>
                    setReimbForm({
                      ...reimbForm,
                      items: [{ ...reimbForm.items[0], amount: Number(e.target.value) }],
                    })
                  }
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 text-sm"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Description</label>
                <input
                  type="text"
                  value={reimbForm.items[0].description}
                  onChange={(e) =>
                    setReimbForm({
                      ...reimbForm,
                      items: [{ ...reimbForm.items[0], description: e.target.value }],
                    })
                  }
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-slate-100 text-sm"
                  required
                />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowReimbModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl text-sm"
                >
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-sm font-medium">
                  Submit Expense Claim
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
