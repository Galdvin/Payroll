import React from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, Home } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center p-6 text-center">
      <div className="w-16 h-16 bg-amber-500/10 border border-amber-500/30 rounded-2xl flex items-center justify-center text-amber-400 mb-4">
        <AlertTriangle className="w-8 h-8" />
      </div>
      <h1 className="text-3xl font-bold text-white mb-2">404 - Page Not Found</h1>
      <p className="text-slate-400 max-w-md mb-6 text-sm">
        The payroll view or resource module you requested does not exist or is currently being built in a future implementation phase.
      </p>
      <Link
        to="/dashboard"
        className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs shadow-lg shadow-brand-500/20 transition"
      >
        <Home className="w-4 h-4" />
        <span>Return to Dashboard</span>
      </Link>
    </div>
  );
};
