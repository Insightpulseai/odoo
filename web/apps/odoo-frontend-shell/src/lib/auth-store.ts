/**
 * Authentication State Management with Zustand
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { OdooSession, getOdooClient } from './odoo-client';

interface AuthState {
  session: OdooSession | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkSession: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      session: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (username: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const client = getOdooClient();
          const session = await client.authenticate(username, password);
          set({
            session,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          set({
            session: null,
            isAuthenticated: false,
            isLoading: false,
            error: error.message || 'Login failed',
          });
          throw error;
        }
      },

      logout: async () => {
        set({ isLoading: true });
        try {
          const client = getOdooClient();
          await client.logout();
          set({
            session: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || 'Logout failed',
          });
        }
      },

      checkSession: async () => {
        set({ isLoading: true });
        try {
          const client = getOdooClient();
          const session = await client.getSessionInfo();
          if (session) {
            set({
              session,
              isAuthenticated: true,
              isLoading: false,
            });
          } else {
            set({
              session: null,
              isAuthenticated: false,
              isLoading: false,
            });
          }
        } catch (error: any) {
          set({
            session: null,
            isAuthenticated: false,
            isLoading: false,
            error: error.message,
          });
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'odoo-auth-storage',
      partialize: (state) => ({ session: state.session }),
    }
  )
);
