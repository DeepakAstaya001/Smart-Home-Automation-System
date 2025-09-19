import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:local_auth/local_auth.dart';
import 'package:camera/camera.dart';
import 'package:lottie/lottie.dart';

import '../providers/security_provider.dart';
import '../services/biometric_service.dart';
import '../services/camera_service.dart';
import '../widgets/security_camera_grid.dart';
import '../widgets/access_log_list.dart';
import '../widgets/emergency_button.dart';

class SecurityScreen extends ConsumerStatefulWidget {
  const SecurityScreen({super.key});

  @override
  ConsumerState<SecurityScreen> createState() => _SecurityScreenState();
}

class _SecurityScreenState extends ConsumerState<SecurityScreen>
    with TickerProviderStateMixin {
  late AnimationController _alertAnimationController;
  late AnimationController _scanAnimationController;
  bool _isScanning = false;

  @override
  void initState() {
    super.initState();
    _alertAnimationController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
    _scanAnimationController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );
  }

  @override
  void dispose() {
    _alertAnimationController.dispose();
    _scanAnimationController.dispose();
    super.dispose();
  }

  Future<void> _performBiometricAuth() async {
    setState(() => _isScanning = true);
    _scanAnimationController.repeat();
    
    try {
      final isAuthenticated = await BiometricService.instance.authenticate();
      if (isAuthenticated) {
        ref.read(securityProvider.notifier).toggleSecuritySystem();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Security system toggled successfully')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Authentication failed: $e')),
      );
    } finally {
      setState(() => _isScanning = false);
      _scanAnimationController.stop();
    }
  }

  @override
  Widget build(BuildContext context) {
    final securityState = ref.watch(securityProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Security Center'),
        backgroundColor: securityState.isArmed ? Colors.red : Colors.green,
        actions: [
          IconButton(
            onPressed: () {
              // Navigate to security settings
            },
            icon: const Icon(Icons.settings),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Security Status Card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Security System',
                              style: theme.textTheme.headlineSmall,
                            ),
                            const SizedBox(height: 8),
                            Row(
                              children: [
                                Container(
                                  width: 12,
                                  height: 12,
                                  decoration: BoxDecoration(
                                    color: securityState.isArmed ? Colors.red : Colors.green,
                                    shape: BoxShape.circle,
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  securityState.isArmed ? 'ARMED' : 'DISARMED',
                                  style: theme.textTheme.bodyLarge?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: securityState.isArmed ? Colors.red : Colors.green,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                        GestureDetector(
                          onTap: _performBiometricAuth,
                          child: Container(
                            width: 80,
                            height: 80,
                            decoration: BoxDecoration(
                              color: securityState.isArmed ? Colors.red : Colors.green,
                              shape: BoxShape.circle,
                              boxShadow: [
                                BoxShadow(
                                  color: (securityState.isArmed ? Colors.red : Colors.green)
                                      .withOpacity(0.3),
                                  blurRadius: 10,
                                  spreadRadius: 2,
                                ),
                              ],
                            ),
                            child: _isScanning
                                ? Lottie.asset(
                                    'assets/animations/fingerprint_scan.json',
                                    controller: _scanAnimationController,
                                  )
                                : Icon(
                                    securityState.isArmed ? Icons.lock : Icons.lock_open,
                                    color: Colors.white,
                                    size: 40,
                                  ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    if (securityState.isArmed) ...[
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.red.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.red.withOpacity(0.3)),
                        ),
                        child: Row(
                          children: [
                            AnimatedBuilder(
                              animation: _alertAnimationController,
                              builder: (context, child) {
                                _alertAnimationController.repeat(reverse: true);
                                return FadeTransition(
                                  opacity: _alertAnimationController,
                                  child: const Icon(Icons.warning, color: Colors.red),
                                );
                              },
                            ),
                            const SizedBox(width: 8),
                            const Expanded(
                              child: Text(
                                'Security system is active. All sensors are monitoring.',
                                style: TextStyle(color: Colors.red),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),

            const SizedBox(height: 20),

            // Emergency Controls
            Text(
              'Emergency Controls',
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: EmergencyButton(
                    label: 'Panic Alert',
                    icon: Icons.emergency,
                    color: Colors.red,
                    onPressed: () {
                      ref.read(securityProvider.notifier).triggerPanicAlert();
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: EmergencyButton(
                    label: 'Fire Alert',
                    icon: Icons.local_fire_department,
                    color: Colors.orange,
                    onPressed: () {
                      ref.read(securityProvider.notifier).triggerFireAlert();
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: EmergencyButton(
                    label: 'Medical',
                    icon: Icons.local_hospital,
                    color: Colors.blue,
                    onPressed: () {
                      ref.read(securityProvider.notifier).triggerMedicalAlert();
                    },
                  ),
                ),
              ],
            ),

            const SizedBox(height: 20),

            // Security Cameras
            Text(
              'Security Cameras',
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            SecurityCameraGrid(
              cameras: securityState.cameras,
              onCameraSelected: (camera) {
                // Navigate to camera detail
              },
            ),

            const SizedBox(height: 20),

            // Sensor Status
            Text(
              'Sensor Status',
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Card(
              child: Column(
                children: securityState.sensors.map((sensor) {
                  return ListTile(
                    leading: CircleAvatar(
                      backgroundColor: sensor.isActive ? Colors.green : Colors.grey,
                      child: Icon(
                        _getSensorIcon(sensor.type),
                        color: Colors.white,
                        size: 20,
                      ),
                    ),
                    title: Text(sensor.name),
                    subtitle: Text(sensor.location),
                    trailing: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          sensor.isActive ? 'Active' : 'Inactive',
                          style: TextStyle(
                            color: sensor.isActive ? Colors.green : Colors.grey,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        if (sensor.lastTriggered != null)
                          Text(
                            'Last: ${_formatTime(sensor.lastTriggered!)}',
                            style: theme.textTheme.bodySmall,
                          ),
                      ],
                    ),
                    onTap: () {
                      // Show sensor details
                    },
                  );
                }).toList(),
              ),
            ),

            const SizedBox(height: 20),

            // Access Log
            Text(
              'Recent Access Log',
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            AccessLogList(
              logs: securityState.accessLogs,
              onViewAll: () {
                // Navigate to full access log
              },
            ),
          ],
        ),
      ),
    );
  }

  IconData _getSensorIcon(String type) {
    switch (type.toLowerCase()) {
      case 'motion':
        return Icons.directions_walk;
      case 'door':
        return Icons.door_front_door;
      case 'window':
        return Icons.window;
      case 'smoke':
        return Icons.smoke_free;
      case 'gas':
        return Icons.gas_meter;
      case 'glass':
        return Icons.broken_image;
      default:
        return Icons.sensors;
    }
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final difference = now.difference(time);
    
    if (difference.inDays > 0) {
      return '${difference.inDays}d ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}m ago';
    } else {
      return 'Just now';
    }
  }
}