import React, { useEffect, useState } from 'react';
import { organizationService } from '../services/organizationService';
import {
  Organization,
  Company,
  Branch,
  Department,
  Designation,
  CostCenter,
} from '../types/organization';
import { Building2, GitFork, MapPin, Plus, Layers, Wallet, Tag } from 'lucide-react';

export const OrganizationPage: React.FC = () => {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [designations, setDesignations] = useState<Designation[]>([]);
  const [costCenters, setCostCenters] = useState<CostCenter[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Active Tab: 'branches' | 'departments' | 'designations' | 'cost_centers'
  const [activeTab, setActiveTab] = useState<'branches' | 'departments' | 'designations' | 'cost_centers'>('departments');

  // Modals state
  const [showOrgModal, setShowOrgModal] = useState(false);
  const [showDeptModal, setShowDeptModal] = useState(false);

  const [orgName, setOrgName] = useState('');
  const [orgCode, setOrgCode] = useState('');
  const [deptName, setDeptName] = useState('');
  const [deptCode, setDeptCode] = useState('');

  const loadData = async () => {
    setIsLoading(true);
    try {
      let orgs = await organizationService.getOrganizations();
      if (orgs.length === 0) {
        // Seed default organization & company if empty
        const defaultOrg = await organizationService.createOrganization({
          name: 'Enterprise Organization',
          code: 'ENT_ORG',
          currency: 'INR',
          country: 'India',
        });
        const defaultComp = await organizationService.createCompany({
          organization_id: defaultOrg.id,
          name: 'Enterprise Corp Pvt Ltd',
          code: 'ENT_CORP',
        });
        await organizationService.createDepartment({ company_id: defaultComp.id, name: 'Human Resources', code: 'HR' });
        await organizationService.createDepartment({ company_id: defaultComp.id, name: 'Engineering', code: 'ENG' });
        await organizationService.createBranch({ company_id: defaultComp.id, name: 'Headquarters', code: 'HQ', city: 'Mumbai' });
        orgs = [defaultOrg];
      }
      setOrganizations(orgs);

      const comps = await organizationService.getCompanies(orgs[0].id);
      setCompanies(comps);

      if (comps.length > 0) {
        const [b, d, des, cc] = await Promise.all([
          organizationService.getBranches(comps[0].id),
          organizationService.getDepartments(comps[0].id),
          organizationService.getDesignations(comps[0].id),
          organizationService.getCostCenters(comps[0].id),
        ]);
        setBranches(b);
        setDepartments(d);
        setDesignations(des);
        setCostCenters(cc);
      }
    } catch (err) {
      console.error('Failed to load organization hierarchy', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateOrg = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await organizationService.createOrganization({ name: orgName, code: orgCode });
      setShowOrgModal(false);
      setOrgName('');
      setOrgCode('');
      loadData();
    } catch (err) {
      alert('Failed to create organization');
    }
  };

  const handleCreateDept = async (e: React.FormEvent) => {
    e.preventDefault();
    if (companies.length === 0) return;
    try {
      await organizationService.createDepartment({ company_id: companies[0].id, name: deptName, code: deptCode });
      setShowDeptModal(false);
      setDeptName('');
      setDeptCode('');
      loadData();
    } catch (err) {
      alert('Failed to create department');
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center space-x-2">
            <Building2 className="w-5 h-5 text-brand-400" />
            <span>Multi-Tenant Organization Structure</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">Manage companies, branches, department hierarchy, and cost centers</p>
        </div>

        <button
          onClick={() => setShowOrgModal(true)}
          className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-lg shadow-brand-500/20 transition"
        >
          <Plus className="w-4 h-4" />
          <span>New Organization</span>
        </button>
      </div>

      {/* Organization Banner */}
      {organizations.length > 0 && (
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 rounded-xl bg-brand-500/10 border border-brand-500/30 flex items-center justify-center text-brand-400 font-bold font-mono text-lg">
              {organizations[0].code.slice(0, 3)}
            </div>
            <div>
              <h2 className="text-base font-bold text-white">{organizations[0].name}</h2>
              <div className="flex items-center space-x-3 text-xs text-slate-400 mt-0.5 font-mono">
                <span>Code: <strong className="text-brand-300">{organizations[0].code}</strong></span>
                <span>•</span>
                <span>Country: {organizations[0].country}</span>
                <span>•</span>
                <span>Currency: {organizations[0].currency}</span>
              </div>
            </div>
          </div>
          <div className="text-right text-xs font-mono text-slate-400">
            Active Companies: <span className="text-white font-bold">{companies.length}</span>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('departments')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeTab === 'departments'
              ? 'bg-brand-500/10 text-brand-400 border border-brand-500/30'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <GitFork className="w-4 h-4" />
          <span>Departments ({departments.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('branches')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeTab === 'branches'
              ? 'bg-brand-500/10 text-brand-400 border border-brand-500/30'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <MapPin className="w-4 h-4" />
          <span>Branches ({branches.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('designations')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeTab === 'designations'
              ? 'bg-brand-500/10 text-brand-400 border border-brand-500/30'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <Tag className="w-4 h-4" />
          <span>Designations ({designations.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('cost_centers')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition ${
            activeTab === 'cost_centers'
              ? 'bg-brand-500/10 text-brand-400 border border-brand-500/30'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <Wallet className="w-4 h-4" />
          <span>Cost Centers ({costCenters.length})</span>
        </button>
      </div>

      {/* Tab Contents */}
      {activeTab === 'departments' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-sm font-bold text-white">Company Department Tree</h3>
            <button
              onClick={() => setShowDeptModal(true)}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold flex items-center space-x-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Department</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {departments.map((dept) => (
              <div key={dept.id} className="glass-panel p-4 rounded-xl border border-slate-800 flex items-center space-x-3">
                <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 font-mono font-bold text-xs">
                  {dept.code}
                </div>
                <div>
                  <h4 className="font-bold text-white text-xs">{dept.name}</h4>
                  <p className="text-[11px] text-slate-400 font-mono">Code: {dept.code}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'branches' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {branches.map((b) => (
            <div key={b.id} className="glass-panel p-4 rounded-xl border border-slate-800 space-y-2">
              <div className="flex items-center space-x-2 text-brand-400">
                <MapPin className="w-4 h-4" />
                <h4 className="font-bold text-white text-xs">{b.name}</h4>
              </div>
              <p className="text-xs text-slate-400">{b.city || 'Headquarter Location'}</p>
              <div className="text-[10px] font-mono text-slate-500">Timezone: {b.timezone}</div>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'designations' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {designations.map((d) => (
            <div key={d.id} className="glass-panel p-4 rounded-xl border border-slate-800 space-y-1">
              <h4 className="font-bold text-white text-xs">{d.title}</h4>
              <p className="text-[11px] font-mono text-slate-400">Code: {d.code}</p>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'cost_centers' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {costCenters.map((cc) => (
            <div key={cc.id} className="glass-panel p-4 rounded-xl border border-slate-800 space-y-1">
              <h4 className="font-bold text-white text-xs">{cc.name}</h4>
              <p className="text-[11px] font-mono text-brand-400">Cost Code: {cc.code}</p>
            </div>
          ))}
        </div>
      )}

      {/* Create Org Modal */}
      {showOrgModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-md p-6 rounded-2xl border border-slate-700 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white">Create Organization Tenant</h3>
            <form onSubmit={handleCreateOrg} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Organization Name</label>
                <input
                  type="text"
                  required
                  value={orgName}
                  onChange={(e) => setOrgName(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white"
                  placeholder="Global Apex Group"
                />
              </div>
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Organization Code</label>
                <input
                  type="text"
                  required
                  value={orgCode}
                  onChange={(e) => setOrgCode(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white"
                  placeholder="APEX"
                />
              </div>
              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowOrgModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300"
                >
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 rounded-lg bg-brand-600 text-white font-semibold">
                  Save Organization
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Create Dept Modal */}
      {showDeptModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-md p-6 rounded-2xl border border-slate-700 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white">Add Department</h3>
            <form onSubmit={handleCreateDept} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Department Name</label>
                <input
                  type="text"
                  required
                  value={deptName}
                  onChange={(e) => setDeptName(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white"
                  placeholder="Finance & Accounts"
                />
              </div>
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Department Code</label>
                <input
                  type="text"
                  required
                  value={deptCode}
                  onChange={(e) => setDeptCode(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white"
                  placeholder="FIN"
                />
              </div>
              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowDeptModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300"
                >
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 rounded-lg bg-brand-600 text-white font-semibold">
                  Save Department
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
