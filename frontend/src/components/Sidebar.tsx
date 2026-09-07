import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  ShieldCheck, 
  Building2, 
  CalendarCheck, 
  Calculator, 
  FileText, 
  CreditCard, 
  BarChart3,
  Palmtree
} from 'lucide-react';
import { useAuthStore } from '../stores/authStore';

export const Sidebar: React.FC = () => {
  const { hasPermission } = useAuthStore();

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, perm: null },
    { label: 'Staff Directory', path: '/employees', icon: Users, perm: 'employee.view' },
    { label: 'Organization', path: '/organization', icon: Building2, perm: 'employee.view' },
    { label: 'Roles & RBAC', path: '/roles', icon: ShieldCheck, perm: 'employee.view' },
    { label: 'Attendance & Shifts', path: '/attendance', icon: CalendarCheck, perm: 'attendance.view' },
    { label: 'Leave Portal', path: '/leaves', icon: Palmtree, perm: 'attendance.view' },
    { label: 'Salary Structure', path: '/salary-structures', icon: Calculator, perm: 'salary.view' },
    { label: 'Payroll Engine', path: '/payroll', icon: Calculator, perm: 'payroll.view' },
    { label: 'Tax & Statutory', path: '/tax-statutory', icon: ShieldCheck, perm: 'salary.view' },
    { label: 'Financial Extras', path: '/financial-extras', icon: CreditCard, perm: 'payroll.view' },
    { label: 'Payslips & PDF', path: '/payslips', icon: FileText, perm: 'payroll.view' },
    { label: 'Bank Payments', path: '/payments', icon: CreditCard, perm: 'payroll.process_payment' },
    { label: 'Reports & Analytics', path: '/reports', icon: BarChart3, perm: 'reports.view' },
    { label: 'Self-Service (ESS/MSS)', path: '/self-service', icon: Users, perm: null },
    { label: 'Audit Trail', path: '/audit', icon: ShieldCheck, perm: 'employee.view' },
  ];

  return (
    <aside className="w-64 glass-panel border-r border-slate-800/80 min-h-screen flex flex-col justify-between p-4 sticky top-0 z-30">
      <div>
        {/* Brand Logo & Name */}
        <div className="flex items-center space-x-3 px-3 py-4 mb-6 border-b border-slate-800/60">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 via-brand-500 to-sky-400 flex items-center justify-center shadow-lg shadow-brand-500/20">
            <Calculator className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-white tracking-tight leading-none text-base">PayPlatform</h1>
            <span className="text-[11px] font-mono text-brand-400 font-semibold tracking-wider uppercase">Enterprise v1.0</span>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            if (item.perm && !hasPermission(item.perm)) return null;

            const Icon = item.icon;
            if (item.disabled) {
              return (
                <div
                  key={item.path}
                  className="flex items-center justify-between px-3 py-2.5 rounded-lg text-slate-500 cursor-not-allowed opacity-60 text-sm font-medium"
                >
                  <div className="flex items-center space-x-3">
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </div>
                  <span className="text-[10px] font-mono bg-slate-800/80 px-1.5 py-0.5 rounded text-slate-400">Phase 12+</span>
                </div>
              );
            }

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-brand-600/30 to-brand-500/10 text-white border border-brand-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800/40'
                  }`
                }
              >
                <Icon className="w-4 h-4 text-brand-400" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* System Status Footer */}
      <div className="px-3 py-3 rounded-xl bg-slate-900/60 border border-slate-800/50">
        <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
          <span>Security Engine</span>
          <span className="flex items-center text-emerald-400 font-mono text-[10px]">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse mr-1"></span> Active
          </span>
        </div>
        <div className="text-[11px] font-mono text-slate-500 truncate">Phase 12: Security & Audit Trail</div>
      </div>





    </aside>
  );
};
