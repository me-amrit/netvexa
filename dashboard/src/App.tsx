import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

import { useAuthStore } from './store/authStore';
import PrivateRoute from './components/PrivateRoute';
import Layout from './components/Layout';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Agents from './pages/Agents';
import AgentDetail from './pages/AgentDetail';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import ApiKeys from './pages/ApiKeys';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

function App() {
  const { isAuthenticated, fetchUser } = useAuthStore();

  useEffect(() => {
    // Try to fetch user data if we have tokens
    if (isAuthenticated) {
      fetchUser().catch(() => {
        // Token might be expired
      });
    }
  }, [isAuthenticated, fetchUser]);

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                iconTheme: {
                  primary: '#4ade80',
                  secondary: '#fff',
                },
              },
              error: {
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#fff',
                },
              },
            }}
          />
          
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={
              isAuthenticated ? <Navigate to="/dashboard" /> : <Login />
            } />
            <Route path="/register" element={
              isAuthenticated ? <Navigate to="/dashboard" /> : <Register />
            } />
            
            {/* Private routes */}
            <Route element={<PrivateRoute />}>
              <Route element={<Layout />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/agents" element={<Agents />} />
                <Route path="/agents/:id" element={<AgentDetail />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/api-keys" element={<ApiKeys />} />
              </Route>
            </Route>
            
            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/dashboard" />} />
          </Routes>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;