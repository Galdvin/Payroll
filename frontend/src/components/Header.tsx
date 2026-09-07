import React from 'react';
import { LogOut, User as UserIcon, Shield, Bell } from 'lucide-react';
import { useAuthStore } from '../stores/authStore';

export const Header: React.FC = () => {
  const { user, logout } = useAuthStore();

  return (
    <header className="h-16 glass-panel border-b border-slate-800/80 px-6 flex items-center justify-between sticky top-0 z-20">
      <div className="flex items-center space-x-3">
        <h2 className="text-sm font-semibold text-slate-300">Enterprise Payroll Console</h2>
        <span className="text-xs bg-slate-800 text-slate-400 px-2.5 py-0.5 rounded-full border border-slate-700 font-mono">
          Phase 1: Auth & RBAC
        </span>
      </div>

      <div className="flex items-center space-x-4">
        {/* Notification bell placeholder */}
        <button className="w-9 h-9 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-400 hover:text-white transition">
          <Bell className="w-4 h-4" />
        </button>

        {/* Profile menu */}
        {user && (
          <div className="flex items-center space-x-3 pl-3 border-l border-slate-800">
            <div className="text-right">
              <div className="text-xs font-semibold text-white">{user.full_name}</div>
              <div className="text-[10px] text-brand-400 font-mono flex items-center justify-end space-x-1">
                <Shield className="w-3 h-3" />
                <span>{user.is_superuser ? 'SuperAdmin' : user.roles.join(', ') || 'Employee'}</span>
              </div>
            </div>
            
            <button
              onClick={logout}
              title="Sign Out"
              className="w-9 h-9 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-400 hover:bg-red-500/20 transition"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
