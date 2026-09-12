import 'dart:io';

import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  try {
    await Firebase.initializeApp();
  } catch (_) {
    return;
  }
}

class NotificationService {
  NotificationService._();
  static final instance = NotificationService._();

  final _local = FlutterLocalNotificationsPlugin();
  bool _ready = false;
  static const _channel = AndroidNotificationChannel(
    'campaigns',
    'Kampanya Bildirimleri',
    description: 'Kartınıza uygun yeni kampanyalar',
    importance: Importance.high,
  );

  Future<void> initialize() async {
    if (_ready) return;
    try {
      await Firebase.initializeApp();
      FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);

      const android = AndroidInitializationSettings('@mipmap/ic_launcher');
      const settings = InitializationSettings(android: android);
      await _local.initialize(settings);
      await _local
          .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>()
          ?.createNotificationChannel(_channel);

      final messaging = FirebaseMessaging.instance;
      await messaging.requestPermission(alert: true, badge: true, sound: true);

      final token = await messaging.getToken();
      if (token != null) await _saveToken(token);
      messaging.onTokenRefresh.listen(_saveToken);

      FirebaseMessaging.onMessage.listen(_showForegroundNotification);
      _ready = true;
    } catch (e) {
      // Firebase yapılandırması henüz eklenmemişse uygulama çalışmaya devam eder.
      debugPrint('Bildirim servisi hazır değil: $e');
    }
  }

  Future<void> _saveToken(String token) async {
    final uid = Supabase.instance.client.auth.currentUser?.id;
    if (uid == null || token.isEmpty) return;
    try {
      await Supabase.instance.client.from('user_push_tokens').upsert({
        'user_id': uid,
        'token': token,
        'platform': Platform.isAndroid ? 'android' : 'other',
        'enabled': true,
        'updated_at': DateTime.now().toUtc().toIso8601String(),
      });
    } catch (e) {
      debugPrint('Bildirim token kaydı yapılamadı: $e');
    }
  }

  Future<void> _showForegroundNotification(RemoteMessage message) async {
    final notification = message.notification;
    if (notification == null) return;
    await _local.show(
      message.hashCode,
      notification.title ?? 'Kart Kampanya',
      notification.body ?? 'Kartınıza uygun yeni bir kampanya geldi.',
      const NotificationDetails(
        android: AndroidNotificationDetails(
          'campaigns',
          'Kampanya Bildirimleri',
          channelDescription: 'Kartınıza uygun yeni kampanyalar',
          importance: Importance.high,
          priority: Priority.high,
          icon: '@mipmap/ic_launcher',
        ),
      ),
    );
  }
}
