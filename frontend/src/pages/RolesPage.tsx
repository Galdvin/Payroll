import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Role, Permission } from '../types/user';
import { ShieldCheck, Plus, Lock, Key, Layers } from 'lucide-react';

export const RolesPage: React.FC = () => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const [roleName, setRoleName] = useState('');
  const [description, setDescription] = useState('');
  const [selectedPermIds, setSelectedPermIds] = useState<number[]>([]);
  const [createError, setCreateError] = useState<string | null>(null);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [rolesRes, permsRes] = await Promise.all([
        api.get<Role[]>('/roles'),
        api.get<Permission[]>('/roles/permissions'),
      ]);
      setRoles(rolesRes.data);
      setPermissions(permsRes.data);
    } catch (err) {
      console.error('Failed to load RBAC metadata', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateRole = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateError(null);
    try {
      await api.post('/roles', {
        name: roleName,
        description,
        permission_ids: selectedPermIds,
      });
      setShowCreateModal(false);
      setRoleName('');
      setDescription('');
      setSelectedPermIds([]);
      fetchData();
    } catch (err: any) {
      setCreateError(err.response?.data?.message || 'Failed to create role.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-brand-400" />
            <span>Role-Based Access Control (RBAC) Architecture</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">Define custom security roles and grant granular system permissions</p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-lg shadow-brand-500/20 transition"
        >
          <Plus className="w-4 h-4" />
          <span>Create Custom Role</span>
        </button>
      </div>

      {/* Grid of Roles */}
      {isLoading ? (
        <div className="p-12 text-center text-slate-400 text-xs font-mono">Loading security matrix...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {roles.map((role) => (
            <div key={role.id} className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-white text-sm">{role.name}</span>
                  {role.is_system_role ? (
                    <span className="px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20 text-amber-300 text-[10px] font-mono flex items-center">
                      <Lock className="w-2.5 h-2.5 mr-1" /> SYSTEM
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 rounded bg-brand-500/10 border border-brand-500/20 text-brand-300 text-[10px] font-mono">
                      CUSTOM
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-400 line-clamp-2 mb-3">{role.description || 'No description provided.'}</p>
              </div>

              <div>
                <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5 flex items-center justify-between">
                  <span>Assigned Permissions</span>
                  <span className="font-mono text-brand-400">{role.permissions.length}</span>
                </div>
                <div className="flex flex-wrap gap-1 max-h-24 overflow-y-auto p-1 bg-slate-900/60 rounded-lg border border-slate-800/80">
                  {role.permissions.length > 0 ? (
                    role.permissions.map((p) => (
                      <span key={p.id} className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[10px]">
                        {p.code}
                      </span>
                    ))
                  ) : (
                    <span className="text-slate-500 italic text-[10px] px-1 py-0.5">All permissions (*)</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Permissions Matrix Catalog */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center space-x-2">
          <Key className="w-4 h-4 text-brand-400" />
          <span>System Granular Permissions Catalog ({permissions.length})</span>
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          {permissions.map((p) => (
            <div key={p.id} className="p-3 bg-slate-900/80 rounded-xl border border-slate-800/80 text-xs">
              <div className="font-mono font-bold text-brand-400">{p.code}</div>
              <div className="text-[10px] text-slate-500 uppercase tracking-wider mt-0.5">Module: {p.module}</div>
              <div className="text-slate-400 mt-1">{p.description}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Create Role Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-md p-6 rounded-2xl border border-slate-700 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white">Create Custom Security Role</h3>
            
            {createError && (
              <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-xs text-red-400">
                {createError}
              </div>
            )}

            <form onSubmit={handleCreateRole} className="space-y-3.5 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Role Name</label>
                <input
                  type="text"
                  required
                  value={roleName}
                  onChange={(e) => setRoleName(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500"
                  placeholder="e.g. Payroll Auditor"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500"
                  placeholder="Enter role responsibilities..."
                  rows={2}
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Grant Permissions</label>
                <div className="space-y-1.5 max-h-40 overflow-y-auto bg-slate-900 p-2 rounded-lg border border-slate-800">
                  {permissions.map((p) => (
                    <label key={p.id} className="flex items-center space-x-2 text-slate-300 cursor-pointer text-[11px]">
                      <input
                        type="checkbox"
                        checked={selectedPermIds.includes(p.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedPermIds([...selectedPermIds, p.id]);
                          } else {
                            setSelectedPermIds(selectedPermIds.filter((id) => id !== p.id));
                          }
                        }}
                        className="rounded bg-slate-800 border-slate-700 text-brand-500 focus:ring-0"
                      />
                      <span className="font-mono text-brand-400">{p.code}</span>
                      <span className="text-slate-500 text-[10px]">- {p.description}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex justify-end space-x-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold shadow-md"
                >
                  Create Role
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
