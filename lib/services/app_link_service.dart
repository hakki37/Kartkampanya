import 'dart:io';

import 'package:android_intent_plus/android_intent.dart';
import 'package:url_launcher/url_launcher.dart';

/// Keeps bank-app launching isolated from the campaign UI.
/// If a supported bank app is not installed (or cannot be opened),
/// the original campaign URL is opened as before.
class AppLinkService {
  AppLinkService._();
  static final instance = AppLinkService._();

  static const _packages = <String, String>{
    'Akbank': 'com.akbank.android.apps.akbank_digital',
    'Garanti BBVA': 'com.garanti.cepsubesi',
    'Yapı Kredi': 'com.ykb.android',
    'İş Bankası': 'com.isbank.iscep',
    'Ziraat Bankası': 'com.ziraat.ziraatmobil',
    'Halkbank': 'com.halkbank.mobile',
    'QNB': 'com.qnbfinansbank.mobile',
    'DenizBank': 'com.denizbank.mobildeniz',
    'TEB': 'com.teb.ceponet',
    'VakıfBank': 'com.vakifbank.mobile',
    'Kuveyt Türk': 'com.kuveytturk.mobil',
    'Türkiye Finans': 'com.turkiyefinans.mobile',
    'Albaraka Türk': 'com.albaraka.mobile',
    'ING': 'com.ingbanktr.ingmobil',
    'Fibabanka': 'com.fibabanka.mobile',
    'HSBC': 'com.hsbc.hsbc',
    'Odeabank': 'com.odeabank.mobile',
    'Enpara': 'com.qnbfinansbank.enpara',
  };

  Future<void> openCampaign({
    required String bankName,
    required String sourceUrl,
  }) async {
    final fallback = Uri.tryParse(sourceUrl);
    if (fallback == null || !fallback.hasScheme) return;

    if (Platform.isAndroid) {
      final packageName = _packages[bankName];
      if (packageName != null) {
        try {
          final intent = AndroidIntent(
            action: 'android.intent.action.MAIN',
            category: 'android.intent.category.LAUNCHER',
            package: packageName,
          );
          if (await intent.canResolveActivity()) {
            await intent.launch();
            return;
          }
        } catch (_) {
          // Never block the original campaign URL if app launch fails.
        }
      }
    }

    await launchUrl(fallback, mode: LaunchMode.externalApplication);
  }
}
