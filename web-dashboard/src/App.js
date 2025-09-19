import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, useTheme } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';

// Components
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import LoadingScreen from './components/Common/LoadingScreen';

// Pages
import Dashboard from './pages/Dashboard';
import DeviceControl from './pages/DeviceControl';
import SecurityCenter from './pages/SecurityCenter';
import EnergyManagement from './pages/EnergyManagement';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import Login from './pages/Login';

// Hooks
import { useAuth } from './hooks/useAuth';
import { useWebSocket } from './contexts/WebSocketContext';

// Services
import { authService } from './services/authService';

function App() {
  const theme = useTheme();
  const { isAuthenticated, loading } = useAuth();
  const { connected } = useWebSocket();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [initialLoading, setInitialLoading] = useState(true);

  useEffect(() => {
    // Initialize app
    const initializeApp = async () => {
      try {
        await authService.checkAuthStatus();
      } catch (error) {
        console.error('App initialization error:', error);
      } finally {
        setTimeout(() => setInitialLoading(false), 1500);
      }
    };

    initializeApp();
  }, []);

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  if (initialLoading) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <Login />
      </motion.div>
    );
  }

  return (
    <Box
      sx={{
        display: 'flex',
        height: '100vh',
        backgroundColor: theme.palette.background.default,
      }}
    >
      {/* Sidebar */}
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          transition: theme.transitions.create(['margin', 'width'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          marginLeft: sidebarOpen ? 0 : `-240px`,
        }}
      >
        {/* Header */}
        <Header
          onMenuClick={handleSidebarToggle}
          sidebarOpen={sidebarOpen}
          connected={connected}
        />

        {/* Page Content */}
        <Box
          sx={{
            flexGrow: 1,
            overflow: 'auto',
            p: 3,
          }}
        >
          <AnimatePresence mode="wait">
            <Routes>
              <Route
                path="/"
                element={
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Dashboard />
                  </motion.div>
                }
              />
              <Route
                path="/devices"
                element={
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    <DeviceControl />
                  </motion.div>
                }
              />
              <Route
                path="/security"
                element={
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    <SecurityCenter />
                  </motion.div>
                }
              />
              <Route
                path="/energy"
                element={
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    <EnergyManagement />
                  </motion.div>
                }
              />
              <Route
                path="/analytics"
                element={
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Analytics />
                  </motion.div>
                }
              />
              <Route
                path="/settings"
                element={
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Settings />
                  </motion.div>
                }
              />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </AnimatePresence>
        </Box>
      </Box>
    </Box>
  );
}

export default App;