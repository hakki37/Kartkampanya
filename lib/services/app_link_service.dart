import 'dart:io';

import 'package:android_intent_plus/android_intent.dart';
import 'package:url_launcher/url_launcher.dart';

/// Banka uygulamasını açmayı kampanya arayüzünden izole eder.
/// Uygulama yoksa veya açılamıyorsa mevcut web adresine geri döner.
class AppLinkService {
  AppLinkService._();
  static final instance = AppLinkService._();

  // Android Google Play'deki güncel banka uygulama paketleri.
  static const _packages = <String, String>{
    'Akbank': 'com.akbank.android.apps.akbank_direkt',
    'Garanti BBVA': 'com.garanti.cepsubesi',
    'Yapı Kredi': 'com.ykb.android',
    'İş Bankası': 'com.pozitron.iscep',
    'Ziraat Bankası': 'com.ziraat.ziraatmobil',
    'Halkbank': 'com.tmobtech.halkbank',
    'QNB': 'com.finansbank.mobile.cepsube',
    'DenizBank': 'com.denizbank.mobildeniz',
    'TEB': 'com.teb',
    'VakıfBank': 'com.vakifbank.mobile',
    'Kuveyt Türk': 'com.kuveytturk.mobil',
    'Türkiye Finans': 'com.tfkb',
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
      final packageName = _packages[_normalizeBankName(bankName)];
      if (packageName != null) {
        try {
          final intent = AndroidIntent(
            action: 'android.intent.action.MAIN',
            category: 'android.intent.category.LAUNCHER',
            package: packageName,
          );

          // Paket cihazda gerçekten yüklü değilse intent'i çalıştırmıyoruz.
          // Aksi halde Android bazı durumlarda implicit resolver'a düşüp
          // Play Store'u varsayılan uygulama olarak açabiliyor.
          final canOpen = await intent.canResolveActivity() ?? false;
          if (canOpen) {
            await intent.launch();
            return;
          }
        } catch (_) {
          // Uygulama açılamazsa web kampanya adresine düş.
        }
      }
    }

    await launchUrl(fallback, mode: LaunchMode.externalApplication);
  }

  String _normalizeBankName(String value) {
    final name = value.trim().toLowerCase();
    const aliases = <String, String>{
      'iş bankası': 'İş Bankası',
      'is bankasi': 'İş Bankası',
      'qnb finansbank': 'QNB',
      'türkiye finans katılım bankası': 'Türkiye Finans',
      'turkiye finans katilim bankasi': 'Türkiye Finans',
      'teb bankası': 'TEB',
      'teb bankasi': 'TEB',
    };
    return aliases[name] ?? value.trim();
  }
}
