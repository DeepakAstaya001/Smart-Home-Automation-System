import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lottie/lottie.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:flutter_tts/flutter_tts.dart';

import '../providers/home_provider.dart';
import '../providers/voice_provider.dart';
import '../widgets/device_control_card.dart';
import '../widgets/energy_dashboard.dart';
import '../widgets/security_status_card.dart';
import '../widgets/weather_card.dart';
import '../widgets/quick_actions.dart';
import '../widgets/voice_control_button.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late AnimationController _voiceAnimationController;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _voiceAnimationController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
    
    // Start animation
    _animationController.forward();
    
    // Initialize home data
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(homeProvider.notifier).loadHomeData();
    });
  }

  @override
  void dispose() {
    _animationController.dispose();
    _voiceAnimationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final homeState = ref.watch(homeProvider);
    final voiceState = ref.watch(voiceProvider);
    final theme = Theme.of(context);

    return Scaffold(
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: () async {
            await ref.read(homeProvider.notifier).refreshData();
          },
          child: CustomScrollView(
            slivers: [
              // App Bar
              SliverAppBar(
                expandedHeight: 120,
                floating: true,
                pinned: true,
                backgroundColor: theme.primaryColor,
                flexibleSpace: FlexibleSpaceBar(
                  title: AnimatedBuilder(
                    animation: _animationController,
                    builder: (context, child) {
                      return FadeTransition(
                        opacity: _animationController,
                        child: SlideTransition(
                          position: Tween<Offset>(
                            begin: const Offset(0, 0.5),
                            end: Offset.zero,
                          ).animate(CurvedAnimation(
                            parent: _animationController,
                            curve: Curves.easeOut,
                          )),
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Smart Home',
                                style: theme.textTheme.headlineSmall?.copyWith(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                'Welcome back, ${homeState.userName}',
                                style: theme.textTheme.bodyMedium?.copyWith(
                                  color: Colors.white70,
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
                actions: [
                  IconButton(
                    onPressed: () {
                      // Navigate to settings
                    },
                    icon: const Icon(Icons.settings, color: Colors.white),
                  ),
                  IconButton(
                    onPressed: () {
                      // Navigate to notifications
                    },
                    icon: Stack(
                      children: [
                        const Icon(Icons.notifications, color: Colors.white),
                        if (homeState.unreadNotifications > 0)
                          Positioned(
                            right: 0,
                            top: 0,
                            child: Container(
                              padding: const EdgeInsets.all(2),
                              decoration: BoxDecoration(
                                color: Colors.red,
                                borderRadius: BorderRadius.circular(10),
                              ),
                              constraints: const BoxConstraints(
                                minWidth: 16,
                                minHeight: 16,
                              ),
                              child: Text(
                                '${homeState.unreadNotifications}',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 10,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),
                ],
              ),

              // Quick Status Cards
              SliverPadding(
                padding: const EdgeInsets.all(16),
                sliver: SliverToBoxAdapter(
                  child: AnimatedBuilder(
                    animation: _animationController,
                    builder: (context, child) {
                      return FadeTransition(
                        opacity: Tween<double>(begin: 0, end: 1).animate(
                          CurvedAnimation(
                            parent: _animationController,
                            curve: const Interval(0.2, 1.0, curve: Curves.easeOut),
                          ),
                        ),
                        child: SlideTransition(
                          position: Tween<Offset>(
                            begin: const Offset(0, 0.3),
                            end: Offset.zero,
                          ).animate(CurvedAnimation(
                            parent: _animationController,
                            curve: const Interval(0.2, 1.0, curve: Curves.easeOut),
                          )),
                          child: SizedBox(
                            height: 160,
                            child: ListView(
                              scrollDirection: Axis.horizontal,
                              children: [
                                WeatherCard(weather: homeState.weather),
                                const SizedBox(width: 16),
                                SecurityStatusCard(
                                  isArmed: homeState.securityArmed,
                                  onToggle: (value) {
                                    ref.read(homeProvider.notifier)
                                        .toggleSecurity(value);
                                  },
                                ),
                                const SizedBox(width: 16),
                                EnergyDashboard(
                                  currentUsage: homeState.currentPowerUsage,
                                  dailyUsage: homeState.dailyEnergyUsage,
                                  monthlyCost: homeState.monthlyEnergyCost,
                                ),
                              ],
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ),

              // Quick Actions
              SliverPadding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                sliver: SliverToBoxAdapter(
                  child: AnimatedBuilder(
                    animation: _animationController,
                    builder: (context, child) {
                      return FadeTransition(
                        opacity: Tween<double>(begin: 0, end: 1).animate(
                          CurvedAnimation(
                            parent: _animationController,
                            curve: const Interval(0.4, 1.0, curve: Curves.easeOut),
                          ),
                        ),
                        child: SlideTransition(
                          position: Tween<Offset>(
                            begin: const Offset(0, 0.3),
                            end: Offset.zero,
                          ).animate(CurvedAnimation(
                            parent: _animationController,
                            curve: const Interval(0.4, 1.0, curve: Curves.easeOut),
                          )),
                          child: QuickActions(
                            onSceneActivated: (scene) {
                              ref.read(homeProvider.notifier).activateScene(scene);
                            },
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ),

              // Device Controls
              SliverPadding(
                padding: const EdgeInsets.all(16),
                sliver: SliverToBoxAdapter(
                  child: AnimatedBuilder(
                    animation: _animationController,
                    builder: (context, child) {
                      return FadeTransition(
                        opacity: Tween<double>(begin: 0, end: 1).animate(
                          CurvedAnimation(
                            parent: _animationController,
                            curve: const Interval(0.6, 1.0, curve: Curves.easeOut),
                          ),
                        ),
                        child: SlideTransition(
                          position: Tween<Offset>(
                            begin: const Offset(0, 0.3),
                            end: Offset.zero,
                          ).animate(CurvedAnimation(
                            parent: _animationController,
                            curve: const Interval(0.6, 1.0, curve: Curves.easeOut),
                          )),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Device Controls',
                                style: theme.textTheme.headlineSmall?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 16),
                              ...homeState.devices.map((device) => Padding(
                                padding: const EdgeInsets.only(bottom: 12),
                                child: DeviceControlCard(
                                  device: device,
                                  onToggle: (value) {
                                    ref.read(homeProvider.notifier)
                                        .toggleDevice(device.id, value);
                                  },
                                  onSliderChanged: (value) {
                                    ref.read(homeProvider.notifier)
                                        .setDeviceValue(device.id, value);
                                  },
                                ),
                              )),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ),
            ],
          ),
        ),
      ),

      // Voice Control FAB
      floatingActionButton: VoiceControlButton(
        isListening: voiceState.isListening,
        onPressed: () async {
          if (voiceState.isListening) {
            await ref.read(voiceProvider.notifier).stopListening();
            _voiceAnimationController.stop();
          } else {
            await ref.read(voiceProvider.notifier).startListening();
            _voiceAnimationController.repeat();
          }
        },
        animationController: _voiceAnimationController,
      ),

      // Voice Command Overlay
      body: Stack(
        children: [
          // Main content here
          
          // Voice overlay
          if (voiceState.isListening)
            Positioned.fill(
              child: Container(
                color: Colors.black54,
                child: Center(
                  child: Card(
                    margin: const EdgeInsets.all(32),
                    child: Padding(
                      padding: const EdgeInsets.all(24),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Lottie.asset(
                            'assets/animations/voice_listening.json',
                            width: 120,
                            height: 120,
                            controller: _voiceAnimationController,
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'Listening...',
                            style: theme.textTheme.headlineSmall,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            voiceState.recognizedText.isEmpty
                                ? 'Say something...'
                                : voiceState.recognizedText,
                            style: theme.textTheme.bodyLarge,
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 16),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                            children: [
                              TextButton(
                                onPressed: () {
                                  ref.read(voiceProvider.notifier).stopListening();
                                  _voiceAnimationController.stop();
                                },
                                child: const Text('Cancel'),
                              ),
                              ElevatedButton(
                                onPressed: () {
                                  ref.read(voiceProvider.notifier)
                                      .processCommand(voiceState.recognizedText);
                                },
                                child: const Text('Execute'),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}