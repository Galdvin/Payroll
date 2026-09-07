import { create } from 'zustand';
import { CurrentUserPermissions } from '../types/auth';
import { authService } from '../services/authService';

interface AuthState {
  user: CurrentUserPermissions | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: str) => Promise<void>;
  logout: () => void;
  fetchProfile: () => Promise<void>;
  hasPermission: (permissionCode: string) => boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,
  error: null,

  login: async (email: string, password: str) => {
    set({ isLoading: true, error: null });
    try {
      const tokenData = await authService.login(email, password);
      localStorage.setItem('access_token', tokenData.access_token);
      localStorage.setItem('refresh_token', tokenData.refresh_token);
      
      const userProfile = await authService.getCurrentUser();
      set({ user: userProfile, isAuthenticated: true, isLoading: false });
    } catch (err: any) {
      const message = err.response?.data?.message || 'Failed to authenticate.';
      set({ error: message, isLoading: false });
      throw err;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ user: null, isAuthenticated: false, error: null });
  },

  fetchProfile: async () => {
    if (!localStorage.getItem('access_token')) return;
    set({ isLoading: true });
    try {
      const profile = await authService.getCurrentUser();
      set({ user: profile, isAuthenticated: true, isLoading: false });
    } catch (err) {
      get().logout();
      set({ isLoading: false });
    }
  },

  hasPermission: (permissionCode: string): boolean => {
    const { user } = get();
    if (!user) return false;
    if (user.is_superuser || user.permissions.includes('*')) return true;
    return user.permissions.includes(permissionCode);
  },
}));
