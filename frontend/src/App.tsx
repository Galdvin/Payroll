import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from './stores/authStore';
import { ProtectedRoute } from './components/ProtectedRoute';
import { DashboardLayout } from './layouts/DashboardLayout';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { UsersPage } from './pages/UsersPage';
import { RolesPage } from './pages/RolesPage';
import { OrganizationPage } from './pages/OrganizationPage';
import { EmployeesPage } from './pages/EmployeesPage';
import { EmployeeDetailPage } from './pages/EmployeeDetailPage';
import { AttendancePage } from './pages/AttendancePage';
import { LeavesPage } from './pages/LeavesPage';
import { SalaryStructuresPage } from './pages/SalaryStructuresPage';
import { PayrollEnginePage } from './pages/PayrollEnginePage';
import { TaxStatutoryPage } from './pages/TaxStatutoryPage';
import { FinancialExtrasPage } from './pages/FinancialExtrasPage';
import { PayslipsPage } from './pages/PayslipsPage';
import { BankPaymentsPage } from './pages/BankPaymentsPage';
import { ReportsPage } from './pages/ReportsPage';
import { SelfServicePage } from './pages/SelfServicePage';
import { NotFoundPage } from './pages/NotFoundPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export const App: React.FC = () => {
  const { fetchProfile } = useAuthStore();

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          {/* Protected Dashboard Layout */}
          <Route element={<ProtectedRoute />}>
            <Route element={<DashboardLayout />}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/users" element={<UsersPage />} />
              <Route path="/roles" element={<RolesPage />} />
              <Route path="/organization" element={<OrganizationPage />} />
              <Route path="/employees" element={<EmployeesPage />} />
              <Route path="/employees/:id" element={<EmployeeDetailPage />} />
              <Route path="/attendance" element={<AttendancePage />} />
              <Route path="/leaves" element={<LeavesPage />} />
              <Route path="/salary-structures" element={<SalaryStructuresPage />} />
              <Route path="/payroll" element={<PayrollEnginePage />} />
              <Route path="/tax-statutory" element={<TaxStatutoryPage />} />
              <Route path="/financial-extras" element={<FinancialExtrasPage />} />
              <Route path="/payslips" element={<PayslipsPage />} />
              <Route path="/payments" element={<BankPaymentsPage />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route path="/self-service" element={<SelfServicePage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
};






export default App;
