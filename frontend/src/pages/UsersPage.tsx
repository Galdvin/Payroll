import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { User, Role } from '../types/user';
import { Users as UsersIcon, Plus, Search, Shield, Mail, CheckCircle, XCircle } from 'lucide-react';

export const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [selectedRoleIds, setSelectedRoleIds] = useState<number[]>([]);
  const [createError, setCreateError] = useState<string | null>(null);

  const fetchUsersAndRoles = async () => {
    setIsLoading(true);
    try {
      const [usersRes, rolesRes] = await Promise.all([
        api.get<User[]>('/users'),
        api.get<Role[]>('/roles'),
      ]);
      setUsers(usersRes.data);
      setRoles(rolesRes.data);
    } catch (err) {
      console.error('Failed to load users or roles', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsersAndRoles();
  }, []);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateError(null);
    try {
      await api.post('/users', {
        email,
        full_name: fullName,
        password,
        role_ids: selectedRoleIds,
      });
      setShowCreateModal(false);
      setEmail('');
      setFullName('');
      setPassword('');
      setSelectedRoleIds([]);
      fetchUsersAndRoles();
    } catch (err: any) {
      setCreateError(err.response?.data?.message || 'Failed to create user account.');
    }
  };

  const filteredUsers = users.filter(
    (u) =>
      u.full_name.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center space-x-2">
            <UsersIcon className="w-5 h-5 text-brand-400" />
            <span>User Accounts & RBAC Profiles</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">Manage system access, roles, and administrative scopes</p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-lg shadow-brand-500/20 transition"
        >
          <Plus className="w-4 h-4" />
          <span>New User Account</span>
        </button>
      </div>

      {/* Filter & Search Toolbar */}
      <div className="glass-panel p-4 rounded-xl border border-slate-800 flex items-center justify-between">
        <div className="relative w-full max-w-sm">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name or email..."
            className="w-full bg-slate-900 border border-slate-800 rounded-lg py-1.5 pl-9 pr-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500"
          />
        </div>
        <div className="text-xs text-slate-400 font-mono">
          Total Users: <span className="text-white font-bold">{users.length}</span>
        </div>
      </div>

      {/* Data Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-slate-400 text-xs font-mono">Loading user catalog...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="py-3.5 px-4">User</th>
                  <th className="py-3.5 px-4">Assigned Roles</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4">SuperAdmin</th>
                  <th className="py-3.5 px-4">Created Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredUsers.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-800/30 transition">
                    <td className="py-3.5 px-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-brand-400 uppercase text-xs">
                          {u.full_name[0]}
                        </div>
                        <div>
                          <div className="font-semibold text-white">{u.full_name}</div>
                          <div className="text-slate-400 font-mono text-[11px] flex items-center space-x-1">
                            <Mail className="w-3 h-3 text-slate-500 inline" />
                            <span>{u.email}</span>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex flex-wrap gap-1">
                        {u.roles.length > 0 ? (
                          u.roles.map((r) => (
                            <span key={r.id} className="px-2 py-0.5 rounded bg-brand-500/10 border border-brand-500/20 text-brand-300 text-[10px] font-mono">
                              {r.name}
                            </span>
                          ))
                        ) : (
                          <span className="text-slate-500 italic text-[11px]">No custom role</span>
                        )}
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      {u.is_active ? (
                        <span className="inline-flex items-center text-emerald-400 text-[11px] font-mono">
                          <CheckCircle className="w-3.5 h-3.5 mr-1" /> Active
                        </span>
                      ) : (
                        <span className="inline-flex items-center text-red-400 text-[11px] font-mono">
                          <XCircle className="w-3.5 h-3.5 mr-1" /> Inactive
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-[11px]">
                      {u.is_superuser ? (
                        <span className="text-purple-400 font-bold bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">YES</span>
                      ) : (
                        <span className="text-slate-500">NO</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 font-mono text-[11px]">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create User Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-md p-6 rounded-2xl border border-slate-700 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white">Create User Account</h3>
            
            {createError && (
              <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-xs text-red-400">
                {createError}
              </div>
            )}

            <form onSubmit={handleCreateUser} className="space-y-3.5 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500"
                  placeholder="Jane Doe"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500"
                  placeholder="jane.doe@company.com"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:outline-none focus:border-brand-500"
                  placeholder="••••••••••••"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Assign Roles</label>
                <div className="space-y-1.5 max-h-32 overflow-y-auto bg-slate-900 p-2 rounded-lg border border-slate-800">
                  {roles.map((r) => (
                    <label key={r.id} className="flex items-center space-x-2 text-slate-300 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedRoleIds.includes(r.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedRoleIds([...selectedRoleIds, r.id]);
                          } else {
                            setSelectedRoleIds(selectedRoleIds.filter((id) => id !== r.id));
                          }
                        }}
                        className="rounded bg-slate-800 border-slate-700 text-brand-500 focus:ring-0"
                      />
                      <span>{r.name}</span>
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
                  Create User
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
