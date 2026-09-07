import React, { useEffect, useState } from 'react';
import { taxStatutoryService } from '../services/taxStatutoryService';
import { StatutoryRule, TaxRule, TDSEvaluationResult } from '../types/taxStatutory';
import { ShieldCheck, Globe, Layers, Calculator, Tag, Percent, ArrowRight, CheckCircle2, Lock } from 'lucide-react';

export const TaxStatutoryPage: React.FC = () => {
  const [selectedCountry, setSelectedCountry] = useState<'India' | 'UAE'>('India');
  const [statutoryRules, setStatutoryRules] = useState<StatutoryRule[]>([]);
  const [taxRules, setTaxRules] = useState<TaxRule[]>([]);
  const [activeTab, setActiveTab] = useState<'tax_slabs' | 'statutory' | 'tds_calc'>('tax_slabs');
  const [isLoading, setIsLoading] = useState(true);

  // TDS Calculator Test State
  const [calcMonthlyGross, setCalcMonthlyGross] = useState<number>(100000);
  const [calcRegime, setCalcRegime] = useState<string>('New Regime');
  const [tdsResult, setTdsResult] = useState<TDSEvaluationResult | null>(null);

  const loadData = async (country: string) => {
    setIsLoading(true);
    try {
      const [statRes, taxRes] = await Promise.all([
        taxStatutoryService.getStatutoryRules(country),
        taxStatutoryService.getTaxRules(country),
      ]);
      setStatutoryRules(statRes);
      setTaxRules(taxRes);

      // Auto evaluate TDS
      const tds = await taxStatutoryService.evaluateTDS(calcMonthlyGross, calcRegime);
      setTdsResult(tds);
    } catch (err) {
      console.error('Failed to load statutory rules', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData(selectedCountry);
  }, [selectedCountry]);

  const handleEvaluateTDS = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const tds = await taxStatutoryService.evaluateTDS(calcMonthlyGross, calcRegime);
      setTdsResult(tds);
    } catch (err) {
      alert('TDS calculation failed');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-brand-400" />
            <span>Configurable Tax & Statutory Engine</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">Versioned income tax slabs, standard deductions, PF/ESI/PT statutory rules, and multi-country extension layer</p>
        </div>

        {/* Country Selector for Multi-Country Extensibility */}
        <div className="flex items-center space-x-2 bg-slate-900 p-1.5 rounded-xl border border-slate-800">
          <Globe className="w-4 h-4 text-brand-400 ml-1" />
          <button
            onClick={() => setSelectedCountry('India')}
            className={`px-3 py-1 rounded-lg text-xs font-semibold font-mono transition ${
              selectedCountry === 'India' ? 'bg-brand-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            🇮🇳 India (Active)
          </button>
          <button
            onClick={() => setSelectedCountry('UAE')}
            className={`px-3 py-1 rounded-lg text-xs font-semibold font-mono transition ${
              selectedCountry === 'UAE' ? 'bg-brand-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            🇦🇪 UAE / GCC (Ready)
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('tax_slabs')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeTab === 'tax_slabs' ? 'bg-brand-500/10 text-brand-400 border border-brand-500/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>Income Tax Regimes & Slabs ({taxRules.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('statutory')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeTab === 'statutory' ? 'bg-brand-500/10 text-brand-400 border border-brand-500/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          <span>Statutory Rules (PF, ESI, PT) ({statutoryRules.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('tds_calc')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeTab === 'tds_calc' ? 'bg-brand-500/10 text-brand-400 border border-brand-500/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Calculator className="w-4 h-4" />
          <span>Interactive TDS Tax Calculator</span>
        </button>
      </div>

      {/* Tab 1: Tax Slabs */}
      {activeTab === 'tax_slabs' && (
        <div className="space-y-4">
          {taxRules.map((rule) => (
            <div key={rule.id} className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
              <div className="p-4 border-b border-slate-800 flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="font-bold text-white text-sm">{rule.regime_name} — FY {rule.financial_year}</h3>
                    <span className="px-2 py-0.5 rounded bg-brand-500/10 border border-brand-500/30 text-brand-400 font-mono text-[10px]">
                      {rule.rule_version}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Standard Deduction: <strong className="text-emerald-400 font-mono">₹{rule.standard_deduction.toLocaleString()}</strong> • Health & Edu Cess: <strong className="text-purple-400 font-mono">{rule.cess_rate * 100}%</strong>
                  </p>
                </div>
                <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-mono font-semibold">
                  ACTIVE RULE
                </span>
              </div>

              <div className="p-4 overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="text-slate-400 font-semibold border-b border-slate-800 uppercase tracking-wider">
                    <tr>
                      <th className="py-2.5 px-3">Income Slab Range (₹)</th>
                      <th className="py-2.5 px-3">Applicable Tax Rate</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300">
                    {rule.tax_slabs.map((slab) => (
                      <tr key={slab.id}>
                        <td className="py-2.5 px-3">
                          ₹{slab.from_income.toLocaleString()} {slab.to_income ? `to ₹${slab.to_income.toLocaleString()}` : 'and above'}
                        </td>
                        <td className="py-2.5 px-3 font-bold text-brand-400">
                          {slab.tax_rate * 100}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 2: Statutory Rules */}
      {activeTab === 'statutory' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {statutoryRules.map((rule) => (
            <div key={rule.id} className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-white text-sm">{rule.name}</span>
                <span className="px-2 py-0.5 rounded bg-brand-500/10 text-brand-400 font-mono text-[10px]">
                  {rule.rule_code}
                </span>
              </div>

              <div className="text-xs text-slate-400 space-y-1.5 font-mono pt-1">
                <div className="flex justify-between"><span>Employee Share:</span><span className="text-white font-bold">{rule.employee_rate * 100}%</span></div>
                <div className="flex justify-between"><span>Employer Share:</span><span className="text-white font-bold">{rule.employer_rate * 100}%</span></div>
                {rule.monthly_cap && <div className="flex justify-between"><span>Monthly Cap:</span><span className="text-emerald-400 font-bold">₹{rule.monthly_cap.toLocaleString()}</span></div>}
                {rule.eligibility_threshold && <div className="flex justify-between"><span>Eligibility Ceiling:</span><span className="text-purple-400 font-bold">₹{rule.eligibility_threshold.toLocaleString()}</span></div>}
                <div className="flex justify-between text-slate-500 text-[10px]"><span>Rule Version:</span><span>{rule.rule_version}</span></div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 3: TDS Estimator Calculator */}
      {activeTab === 'tds_calc' && (
        <div className="space-y-6">
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
            <form onSubmit={handleEvaluateTDS} className="flex flex-col sm:flex-row items-center space-y-2 sm:space-y-0 sm:space-x-3 w-full">
              <span className="text-xs font-semibold text-slate-300">Monthly Gross Salary (₹):</span>
              <input
                type="number"
                required
                step="5000"
                value={calcMonthlyGross}
                onChange={(e) => setCalcMonthlyGross(Number(e.target.value))}
                className="bg-slate-900 border border-slate-700 rounded-xl py-2 px-3 text-xs text-white font-mono w-40 focus:outline-none focus:border-brand-500"
              />

              <span className="text-xs font-semibold text-slate-300 sm:ml-4">Tax Regime:</span>
              <select
                value={calcRegime}
                onChange={(e) => setCalcRegime(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded-xl py-2 px-3 text-xs text-white"
              >
                <option value="New Regime">New Regime (FY 2024-25)</option>
              </select>

              <button
                type="submit"
                className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs shadow-md transition"
              >
                Evaluate TDS
              </button>
            </form>
          </div>

          {tdsResult && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="glass-panel p-5 rounded-2xl border border-slate-800">
                <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">Annual Gross Income</span>
                <span className="text-2xl font-bold text-white font-mono">₹{tdsResult.annual_gross.toLocaleString()}</span>
              </div>

              <div className="glass-panel p-5 rounded-2xl border border-slate-800">
                <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">Standard Deduction</span>
                <span className="text-2xl font-bold text-emerald-400 font-mono">-₹{tdsResult.standard_deduction.toLocaleString()}</span>
              </div>

              <div className="glass-panel p-5 rounded-2xl border border-slate-800">
                <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">Total Annual Tax (+4% Cess)</span>
                <span className="text-2xl font-bold text-red-400 font-mono">₹{tdsResult.total_annual_tax.toLocaleString()}</span>
              </div>

              <div className="glass-panel p-5 rounded-2xl border border-brand-500/40 bg-brand-500/10">
                <span className="text-xs text-brand-300 uppercase tracking-wider font-semibold block mb-1">Monthly TDS Deduction</span>
                <span className="text-2xl font-bold text-white font-mono">₹{tdsResult.monthly_tds.toLocaleString()}</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
