import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:permission_handler/permission_handler.dart';

import 'src/app.dart';
import 'src/services/notification_service.dart';
import 'src/services/permission_service.dart';
import 'src/services/storage_service.dart';

final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
    FlutterLocalNotificationsPlugin();

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Firebase
  await Firebase.initializeApp();
  
  // Initialize local storage
  await StorageService.instance.initialize();
  
  // Initialize notifications
  await NotificationService.instance.initialize();
  
  // Request permissions
  await PermissionService.instance.requestAllPermissions();
  
  runApp(
    const ProviderScope(
      child: SmartHomeApp(),
    ),
  );
}