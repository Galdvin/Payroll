import { api } from './api';
import { CurrentUserPermissions, TokenResponse } from '../types/auth';

export const authService = {
  login: async (email: string, password: str): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/auth/login', { email, password });
    return response.data;
  },

  getCurrentUser: async (): Promise<CurrentUserPermissions> => {
    const response = await api.get<CurrentUserPermissions>('/auth/me');
    return response.data;
  },

  seedAdmin: async (): Promise<{ success: boolean; message: string }> => {
    const response = await api.post('/auth/seed-admin');
    return response.data;
  },
};
