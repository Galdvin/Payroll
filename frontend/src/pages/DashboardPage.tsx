import React from 'react';
import { useAuthStore } from '../stores/authStore';
import { Shield, Key, Users, CheckCircle2, Server, Lock, Activity, Sparkles } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();

  const phaseRoadmap = [
    { num: 1, title: 'Architecture, DB & Auth', status: 'Completed', current: true },
    { num: 2, title: 'Multi-Tenant Org & Employees', status: 'Next Phase', current: false },
    { num: 3, title: 'Attendance, Shifts & Leaves', status: 'Upcoming', current: false },
    { num: 4, title: 'Salary Structure Engine', status: 'Upcoming', current: false },
    { num: 5, title: 'Payroll Calculation Engine', status: 'Upcoming', current: false },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-brand-500/20 bg-gradient-to-r from-slate-900 via-slate-900 to-slate-850 relative overflow-hidden">
        <div className="relative z-10 flex items-center justify-between">
          <div>
            <div className="inline-flex items-center space-x-2 bg-brand-500/10 border border-brand-500/30 px-3 py-1 rounded-full text-brand-400 text-xs font-semibold mb-3">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Phase 1 Architecture Live</span>
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Welcome, {user?.full_name}</h1>
            <p className="text-sm text-slate-400 mt-1 max-w-2xl">
              Enterprise Payroll Management System dashboard. Your session is secured with OAuth2 JWT tokens and active granular RBAC permission enforcement.
            </p>
          </div>
          <div className="hidden lg:flex flex-col items-end space-y-1 text-right">
            <span className="text-xs font-mono text-slate-400">Account Type</span>
            <span className="text-sm font-bold text-brand-400">{user?.is_superuser ? 'Super Administrator' : 'Standard User'}</span>
          </div>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-400">
            <Shield className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Assigned Roles</span>
            <span className="text-xl font-bold text-white">{user?.roles.length || 0}</span>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <Key className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Active Permissions</span>
            <span className="text-xl font-bold text-white">{user?.is_superuser ? 'ALL (*)' : user?.permissions.length || 0}</span>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
            <Server className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Database Status</span>
            <span className="text-sm font-bold text-emerald-400 font-mono flex items-center">
              <span className="w-2 h-2 rounded-full bg-emerald-400 mr-1.5 animate-pulse"></span> Connected
            </span>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Token Refresh</span>
            <span className="text-sm font-bold text-purple-300 font-mono">Auto Intercept</span>
          </div>
        </div>
      </div>

      {/* Detailed Section Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* User Profile & Security Tokens */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h2 className="text-base font-bold text-white flex items-center space-x-2">
            <Lock className="w-4 h-4 text-brand-400" />
            <span>Active Session Overview</span>
          </h2>
          <div className="space-y-3 text-xs">
            <div className="flex justify-between py-2 border-b border-slate-800">
              <span className="text-slate-400">Email Address</span>
              <span className="font-mono text-slate-200">{user?.email}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-800">
              <span className="text-slate-400">UUID</span>
              <span className="font-mono text-brand-400 truncate max-w-[180px]">{user?.uuid}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-800">
              <span className="text-slate-400">Security Claims</span>
              <span className="font-mono text-slate-200">OAuth2 Bearer JWT</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-slate-400">Tenant Isolation</span>
              <span className="font-mono text-emerald-400">Global Admin Scope</span>
            </div>
          </div>
        </div>

        {/* System Roadmap Tracker */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h2 className="text-base font-bold text-white flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-brand-400" />
            <span>Implementation Phase Roadmap</span>
          </h2>
          <div className="space-y-3">
            {phaseRoadmap.map((item) => (
              <div
                key={item.num}
                className={`p-3.5 rounded-xl border flex items-center justify-between text-xs transition ${
                  item.current
                    ? 'bg-brand-500/10 border-brand-500/40 text-white'
                    : 'bg-slate-900/40 border-slate-800/80 text-slate-400'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs font-mono ${
                    item.current ? 'bg-brand-500 text-white' : 'bg-slate-800 text-slate-400'
                  }`}>
                    P{item.num}
                  </div>
                  <span className="font-medium text-slate-200">{item.title}</span>
                </div>
                <span className={`px-2.5 py-0.5 rounded-full font-mono text-[10px] font-semibold ${
                  item.current
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    : 'bg-slate-800 text-slate-400'
                }`}>
                  {item.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
