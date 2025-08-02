import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import axios from 'axios';

interface User {
  id: string;
  email: string;
  company_name: string;
  is_active: boolean;
  created_at: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, companyName: string) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<void>;
  fetchUser: () => Promise<void>;
  clearError: () => void;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Configure axios defaults
axios.defaults.baseURL = API_URL;

// Add token to requests
axios.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle token refresh
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        await useAuthStore.getState().refreshAccessToken();
        const token = useAuthStore.getState().accessToken;
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return axios(originalRequest);
      } catch (refreshError) {
        useAuthStore.getState().logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const formData = new FormData();
          formData.append('username', email);
          formData.append('password', password);
          
          const response = await axios.post('/api/auth/login', formData);
          const { access_token, refresh_token } = response.data;
          
          set({
            accessToken: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
          });
          
          // Fetch user data
          await get().fetchUser();
          
          set({ isLoading: false });
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || 'Login failed',
            isLoading: false,
          });
          throw error;
        }
      },
      
      register: async (email: string, password: string, companyName: string) => {
        set({ isLoading: true, error: null });
        
        try {
          await axios.post('/api/auth/register', {
            email,
            password,
            company_name: companyName,
          });
          
          // Auto-login after registration
          await get().login(email, password);
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || 'Registration failed',
            isLoading: false,
          });
          throw error;
        }
      },
      
      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          error: null,
        });
        
        // Clear axios default header
        delete axios.defaults.headers.common['Authorization'];
      },
      
      refreshAccessToken: async () => {
        const refreshToken = get().refreshToken;
        if (!refreshToken) throw new Error('No refresh token');
        
        try {
          const response = await axios.post('/api/auth/refresh', {
            refresh_token: refreshToken,
          });
          
          const { access_token, refresh_token } = response.data;
          
          set({
            accessToken: access_token,
            refreshToken: refresh_token,
          });
        } catch (error) {
          set({ isAuthenticated: false });
          throw error;
        }
      },
      
      fetchUser: async () => {
        try {
          const response = await axios.get('/api/auth/me');
          set({ user: response.data });
        } catch (error) {
          set({ isAuthenticated: false });
          throw error;
        }
      },
      
      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);