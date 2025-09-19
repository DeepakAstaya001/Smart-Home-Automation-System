import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Avatar,
  IconButton,
  Fab,
  Dialog,
  Chip,
  useTheme,
} from '@mui/material';
import {
  Lightbulb,
  Air,
  Security,
  ThermostatAuto,
  Mic,
  MicOff,
  VolumeUp,
  Settings,
  Refresh,
  PowerSettingsNew,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useDispatch, useSelector } from 'react-redux';

// Components
import DeviceCard from '../components/Dashboard/DeviceCard';
import WeatherWidget from '../components/Dashboard/WeatherWidget';
import EnergyChart from '../components/Dashboard/EnergyChart';
import SecurityStatus from '../components/Dashboard/SecurityStatus';
import QuickActions from '../components/Dashboard/QuickActions';
import VoiceControl from '../components/Dashboard/VoiceControl';
import SystemHealth from '../components/Dashboard/SystemHealth';
import RecentActivity from '../components/Dashboard/RecentActivity';

// Hooks
import { useVoiceControl } from '../hooks/useVoiceControl';
import { useDevices } from '../hooks/useDevices';
import { useWebSocket } from '../contexts/WebSocketContext';

// Actions
import { fetchDashboardData } from '../store/slices/dashboardSlice';

const Dashboard = () => {
  const theme = useTheme();
  const dispatch = useDispatch();
  const { devices, loading } = useDevices();
  const { isListening, startListening, stopListening } = useVoiceControl();
  const { sendMessage } = useWebSocket();
  
  const [voiceDialogOpen, setVoiceDialogOpen] = useState(false);
  const [greeting, setGreeting] = useState('');

  const dashboardData = useSelector((state) => state.dashboard);

  useEffect(() => {
    // Set greeting based on time of day
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good Morning');
    else if (hour < 18) setGreeting('Good Afternoon');
    else setGreeting('Good Evening');

    // Fetch dashboard data
    dispatch(fetchDashboardData());
  }, [dispatch]);

  const handleVoiceToggle = () => {
    if (isListening) {
      stopListening();
      setVoiceDialogOpen(false);
    } else {
      startListening();
      setVoiceDialogOpen(true);
    }
  };

  const handleDeviceToggle = (deviceId, newState) => {
    sendMessage({
      type: 'DEVICE_CONTROL',
      payload: {
        deviceId,
        state: newState,
      },
    });
  };

  const handleQuickAction = (action) => {
    sendMessage({
      type: 'QUICK_ACTION',
      payload: { action },
    });
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        delayChildren: 0.1,
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: 'spring',
        stiffness: 100,
      },
    },
  };

  return (
    <Box sx={{ width: '100%', height: '100%' }}>
      {/* Header Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 3,
          }}
        >
          <Box>
            <Typography variant="h3" sx={{ fontWeight: 'bold', mb: 1 }}>
              {greeting}!
            </Typography>
            <Typography variant="h6" color="text.secondary">
              Welcome to your Smart Home Dashboard
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <IconButton
              onClick={() => dispatch(fetchDashboardData())}
              sx={{
                backgroundColor: theme.palette.background.paper,
                '&:hover': {
                  backgroundColor: theme.palette.action.hover,
                },
              }}
            >
              <Refresh />
            </IconButton>
            <IconButton
              sx={{
                backgroundColor: theme.palette.background.paper,
                '&:hover': {
                  backgroundColor: theme.palette.action.hover,
                },
              }}
            >
              <Settings />
            </IconButton>
          </Box>
        </Box>
      </motion.div>

      {/* Quick Stats */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <motion.div variants={itemVariants}>
              <Card
                sx={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', mr: 2 }}>
                      <Lightbulb />
                    </Avatar>
                    <Box>
                      <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                        {dashboardData.activeLights || 0}
                      </Typography>
                      <Typography variant="body2">Lights On</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <motion.div variants={itemVariants}>
              <Card
                sx={{
                  background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                  color: 'white',
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', mr: 2 }}>
                      <ThermostatAuto />
                    </Avatar>
                    <Box>
                      <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                        {dashboardData.temperature || 0}°C
                      </Typography>
                      <Typography variant="body2">Temperature</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <motion.div variants={itemVariants}>
              <Card
                sx={{
                  background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                  color: 'white',
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', mr: 2 }}>
                      <PowerSettingsNew />
                    </Avatar>
                    <Box>
                      <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                        {dashboardData.powerUsage || 0}W
                      </Typography>
                      <Typography variant="body2">Power Usage</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <motion.div variants={itemVariants}>
              <Card
                sx={{
                  background: dashboardData.securityArmed
                    ? 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
                    : 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
                  color: dashboardData.securityArmed ? 'white' : 'black',
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Avatar
                      sx={{
                        bgcolor: dashboardData.securityArmed
                          ? 'rgba(255,255,255,0.2)'
                          : 'rgba(0,0,0,0.1)',
                        mr: 2,
                      }}
                    >
                      <Security />
                    </Avatar>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                        {dashboardData.securityArmed ? 'ARMED' : 'DISARMED'}
                      </Typography>
                      <Typography variant="body2">Security</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        </Grid>
      </motion.div>

      {/* Main Content Grid */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <Grid container spacing={3}>
          {/* Weather Widget */}
          <Grid item xs={12} md={4}>
            <motion.div variants={itemVariants}>
              <WeatherWidget />
            </motion.div>
          </Grid>

          {/* Quick Actions */}
          <Grid item xs={12} md={4}>
            <motion.div variants={itemVariants}>
              <QuickActions onActionClick={handleQuickAction} />
            </motion.div>
          </Grid>

          {/* System Health */}
          <Grid item xs={12} md={4}>
            <motion.div variants={itemVariants}>
              <SystemHealth />
            </motion.div>
          </Grid>

          {/* Device Controls */}
          <Grid item xs={12} lg={8}>
            <motion.div variants={itemVariants}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Device Controls
                  </Typography>
                  <Grid container spacing={2}>
                    {devices.map((device) => (
                      <Grid item xs={12} sm={6} md={4} key={device.id}>
                        <DeviceCard
                          device={device}
                          onToggle={(newState) =>
                            handleDeviceToggle(device.id, newState)
                          }
                        />
                      </Grid>
                    ))}
                  </Grid>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          {/* Recent Activity */}
          <Grid item xs={12} lg={4}>
            <motion.div variants={itemVariants}>
              <RecentActivity />
            </motion.div>
          </Grid>

          {/* Energy Chart */}
          <Grid item xs={12} md={8}>
            <motion.div variants={itemVariants}>
              <EnergyChart />
            </motion.div>
          </Grid>

          {/* Security Status */}
          <Grid item xs={12} md={4}>
            <motion.div variants={itemVariants}>
              <SecurityStatus />
            </motion.div>
          </Grid>
        </Grid>
      </motion.div>

      {/* Voice Control FAB */}
      <Fab
        color={isListening ? 'secondary' : 'primary'}
        onClick={handleVoiceToggle}
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          width: 64,
          height: 64,
          animation: isListening ? 'pulse 1s infinite' : 'none',
          '@keyframes pulse': {
            '0%': {
              transform: 'scale(1)',
              boxShadow: '0 0 0 0 rgba(33, 150, 243, 0.7)',
            },
            '70%': {
              transform: 'scale(1.05)',
              boxShadow: '0 0 0 10px rgba(33, 150, 243, 0)',
            },
            '100%': {
              transform: 'scale(1)',
              boxShadow: '0 0 0 0 rgba(33, 150, 243, 0)',
            },
          },
        }}
      >
        {isListening ? <MicOff /> : <Mic />}
      </Fab>

      {/* Voice Control Dialog */}
      <VoiceControl
        open={voiceDialogOpen}
        onClose={() => setVoiceDialogOpen(false)}
        isListening={isListening}
      />
    </Box>
  );
};

export default Dashboard;