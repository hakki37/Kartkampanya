import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'card_service.dart';

String normalizeCampaignText(String v) => _cleanText(v).toLowerCase().trim()
    .replaceAll('ı', 'i').replaceAll('İ', 'i').replaceAll('ğ', 'g').replaceAll('Ğ', 'g')
    .replaceAll('ü', 'u').replaceAll('Ü', 'u').replaceAll('ş', 's').replaceAll('Ş', 's')
    .replaceAll('ö', 'o').replaceAll('Ö', 'o').replaceAll('ç', 'c').replaceAll('Ç', 'c');

String _cleanText(String value) {
  var v = value
      .replaceAll(RegExp(r'<script[\s\S]*?</script>', caseSensitive: false), ' ')
      .replaceAll(RegExp(r'<style[\s\S]*?</style>', caseSensitive: false), ' ')
      .replaceAll(RegExp(r'<[^>]*>'), ' ')
      .replaceAll(RegExp(r'[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F\u200B-\u200D\uFEFF]'), ' ')
      .replaceAll('\u00A0', ' ')
      .replaceAll(RegExp(r'\s+'), ' ')
      .trim();
  for (var i = 0; i < 3; i++) {
    final before = v;
    v = v.replaceAllMapped(RegExp(r'&#x([0-9a-fA-F]+);'), (m) {
      final n = int.tryParse(m.group(1)!, radix: 16);
      return n == null ? m.group(0)! : String.fromCharCode(n);
    });
    v = v.replaceAllMapped(RegExp(r'&#(\d+);'), (m) {
      final n = int.tryParse(m.group(1)!);
      return n == null ? m.group(0)! : String.fromCharCode(n);
    });
    const entities = {
      '&amp;': '&', '&quot;': '"', '&apos;': "'", '&nbsp;': ' ', '&lt;': '<', '&gt;': '>',
      '&ndash;': '–', '&mdash;': '—', '&rsquo;': '’', '&lsquo;': '‘', '&rdquo;': '”', '&ldquo;': '“',
      '&hellip;': '…', '&bull;': '•', '&trade;': '™', '&reg;': '®', '&copy;': '©',
      '&uuml;': 'ü', '&ouml;': 'ö', '&ccedil;': 'ç', '&Uuml;': 'Ü', '&Ouml;': 'Ö', '&Ccedil;': 'Ç',
    };
    for (final e in entities.entries) v = v.replaceAll(e.key, e.value);
    if (v == before) break;
  }
  return v
      .replaceAll('%%', '%')
      .replaceAll(RegExp(r'^\s*(?:-->|->|[-•]+)\s*'), '')
      .replaceAll(RegExp(r'\s+([,.;:!?])'), r'\1')
      .trim();
}

class Campaign {
  final Map<String, dynamic> data;
  const Campaign(this.data);
  String get id => '${data['id'] ?? data['source_url'] ?? ''}';
  String get brand => _cleanText('${data['merchant'] ?? data['brand'] ?? data['bank_name'] ?? 'Kampanya'}');
  String get title => _cleanText('${data['title'] ?? 'Yeni Kampanya'}');
  String get description => _cleanText('${data['_clean_description'] ?? data['description'] ?? ''}');
  String get category => _cleanText('${data['category'] ?? 'Diğer Kampanyalar'}');
  String get bankName => _cleanText('${data['bank_name'] ?? data['bank'] ?? ''}');
  String get cardName => _cleanText('${data['card_name'] ?? ''}');
  String get network => _cleanText('${data['network'] ?? ''}');
  String get sourceUrl => '${data['source_url'] ?? data['detail_url'] ?? data['url'] ?? ''}'.trim();
  String get dateRangeLabel {
    final s = '${data['start_date'] ?? ''}'.trim(), e = '${data['end_date'] ?? ''}'.trim();
    if (s.isEmpty && e.isEmpty) return 'Tarih bilgisi yok';
    if (s.isEmpty) return e;
    if (e.isEmpty) return s;
    return '$s - $e';
  }
  DateTime? get endDate => parseDate('${data['end_date'] ?? ''}');
  Color get brandColor {
    const m = {'Petrol Ofisi': Color(0xFFE30613), 'Shell': Color(0xFFFFC107), 'Migros': Color(0xFFF37021), 'Trendyol': Color(0xFFF27A1A), 'Starbucks': Color(0xFF00754A)};
    return m[brand] ?? const Color(0xFF6D3DF5);
  }
  String get badgeLabel {
    final d = endDate;
    if (d == null) return 'Aktif';
    final days = d.difference(DateTime.now()).inDays;
    if (days >= 0 && days <= 3) return days == 0 ? 'Bugün bitiyor' : 'Son $days Gün';
    return 'Aktif';
  }
  BadgeType get badgeType {
    final d = endDate;
    if (d != null) {
      final days = d.difference(DateTime.now()).inDays;
      if (days >= 0 && days <= 3) return BadgeType.urgent;
    }
    return BadgeType.normal;
  }
  static DateTime? parseDate(String v) {
    v = v.trim();
    if (v.isEmpty) return null;
    final iso = DateTime.tryParse(v);
    if (iso != null) return iso;
    final m = RegExp(r'^(\d{1,2})[./-](\d{1,2})[./-](\d{4})').firstMatch(v);
    if (m == null) return null;
    return DateTime(int.parse(m.group(3)!), int.parse(m.group(2)!), int.parse(m.group(1)!));
  }
}

enum BadgeType { urgent, normal, special, popular }

String _bestDescription(Map<String, dynamic> m) {
  final title = _cleanText('${m['title'] ?? ''}');
  final candidates = <String>[
    '${m['description'] ?? ''}', '${m['campaign_text'] ?? ''}', '${m['terms'] ?? ''}',
  ].map(_cleanText).where((x) => x.isNotEmpty).toList();
  if (candidates.isEmpty) return '';

  String score(String text) {
    final low = normalizeCampaignText(text);
    var s = text.length.toDouble();
    if (low.contains('%') || RegExp(r'\b\d+[.,]?\d*\s*tl\b').hasMatch(low)) s += 80;
    if (RegExp(r'\b(?:taksit|bonus|puan|indirim|avantaj|hediye|ucretsiz|ücretsiz|worldpuan|chip para|parafpara)\b').hasMatch(low)) s += 70;
    if (low.contains('başvuru işlemleri') || low.contains('platinum dünyası') || low.contains('internet şubesi')) s -= 500;
    return s.toString();
  }

  var best = candidates.first;
  var bestScore = double.parse(score(best));
  for (final candidate in candidates.skip(1)) {
    final candidateScore = double.parse(score(candidate));
    if (candidateScore > bestScore) { best = candidate; bestScore = candidateScore; }
  }

  var text = best;
  final normalizedTitle = normalizeCampaignText(title);
  final normalizedText = normalizeCampaignText(text);
  if (normalizedTitle.isNotEmpty) {
    final last = normalizedText.lastIndexOf(normalizedTitle);
    if (last >= 0 && last < normalizedText.length) {
      final rawIndex = text.toLowerCase().lastIndexOf(title.toLowerCase());
      if (rawIndex >= 0) text = text.substring(rawIndex + title.length).trim();
    }
  }

  text = text.replaceFirst(RegExp(r'^\s*(?:Ana Sayfa\s*>\s*Kampanyalar\s*>\s*)+', caseSensitive: false), '').trim();
  const cutMarkers = [
    'İlginizi Çekebilecek Kampanyalar', 'VakıfBank Web Siteleri', 'Facebook Twitter instagram Youtube',
    'Hızlı Linkler', 'Sıkça Sorulan Sorular', 'Çerez Tercihleri', 'Bizi Takip Edin:', 'Footer', 'Site Haritası',
  ];
  for (final marker in cutMarkers) {
    final idx = normalizeCampaignText(text).indexOf(normalizeCampaignText(marker));
    if (idx > 0) text = text.substring(0, idx).trim();
  }

  text = _cleanText(text);
  final low = normalizeCampaignText(text);
  const junkPhrases = [
    'başvuru işlemleri ayrıcalıklar', 'platinum dünyası', 'milplus.com.tr', 'çerez politikası',
    'gizlilik politikası', 'internet şubesi', 'bankkart mobil uygulaması', 'sitemize erişimde geçici bir hata',
    'tarayıcınız desteklenmiyor', 'aradığınız kriterlerde bir kampanya bulunamamıştır',
    'bu kategoride şu an için bir kampanyamız bulunmamaktadır', 'parafcard.dependencies', 'parafcard.site',
    'içeriğe atla bireysel kurumsal', 'içeriğe atla ürün ve hizmet ücretleri',
  ];
  if (text.length < 25 || junkPhrases.any(low.contains)) return '';
  return text;
}

String _inferCategory(String current, String title, String description) {
  final existing = _cleanText(current);
  if (existing.isNotEmpty && normalizeCampaignText(existing) != 'diğer kampanyalar') return existing;
  final text = normalizeCampaignText('$title $description');
  const groups = <String, List<String>>{
    'Akaryakıt': ['akaryakıt', 'akaryakit', 'benzin', 'motorin', 'yakıtmatik', 'petrol ofisi', 'shell', 'opet', 'totalenergies', 'istasyon'],
    'Otomotiv': ['otomotiv', 'araç bakım', 'arac bakim', 'lastik', 'yedek parça', 'yedek parca', 'araç kiralama', 'arac kiralama', 'ispark', 'şarj', 'sarj'],
    'Market': ['market', 'gıda', 'gida', 'a101', 'migros', 'carrefour', 'bim', 'şok'],
    'Restoran': ['restoran', 'restaurant', 'kahve', 'cafe', 'fast food', 'starbucks', 'coffy', 'domino'],
    'E-ticaret': ['e-ticaret', 'eticaret', 'online alışveriş', 'online alisveris', 'internet alışveriş', 'internet alisveris', 'hepsiburada', 'trendyol', 'n11', 'pazarama'],
    'Elektronik': ['elektronik', 'telefon', 'bilgisayar', 'televizyon', 'tablet', 'teknoloji'],
    'Giyim': ['giyim', 'ayakkabı', 'ayakkabi', 'çanta', 'canta', 'zara', 'koton', 'nike', 'boyner', 'bershka'],
    'Ev & Yaşam': ['mobilya', 'dekorasyon', 'ev aletleri', 'beyaz eşya', 'beyaz esya', 'evidea', 'koçtaş', 'koctas'],
    'Seyahat': ['seyahat', 'uçak', 'ucak', 'otel', 'rezervasyon', 'turizm', 'havalimanı', 'havalimani', 'tatil'],
    'Eğlence': ['eğlence', 'eglence', 'sinema', 'oyun', 'müzik', 'muzik', 'netflix', 'spotify', 'steam'],
    'Sağlık & Kişisel Bakım': ['sağlık', 'saglik', 'eczane', 'hastane', 'veteriner', 'kozmetik', 'kişisel bakım', 'kisisel bakim'],
    'Spor': ['spor', 'fitness', 'gym'],
  };
  for (final entry in groups.entries) { if (entry.value.any(text.contains)) return entry.key; }
  return existing.isEmpty ? 'Diğer Kampanyalar' : existing;
}

String _inferMerchant(String current, String title, String description) {
  final existing = _cleanText(current);
  if (existing.isNotEmpty) return existing;
  final text = normalizeCampaignText('$title $description');
  const brands = <String, String>{
    'petrol ofisi': 'Petrol Ofisi', 'shell': 'Shell', 'migros': 'Migros', 'trendyol': 'Trendyol',
    'hepsiburada': 'Hepsiburada', 'n11': 'n11', 'pazarama': 'Pazarama', 'starbucks': 'Starbucks',
    'a101': 'A101', 'nike': 'Nike', 'boyner': 'Boyner', 'koton': 'Koton', 'zara': 'Zara',
    'bershka': 'Bershka', 'saat&saat': 'Saat&Saat', 'd&r': 'D&R', 'skechers': 'Skechers',
    'lc waikiki': 'LC Waikiki', 'idefix': 'Idefix', 'casper': 'Casper', 'mudo': 'Mudo',
    'evidea': 'Evidea', 'vivense': 'Vivense', 'halalbooking': 'Halalbooking', 'ispark': 'İSPARK',
    'iklimsa': 'İklimsa', 'tatilbudur': 'TatilBudur', 'ets': 'ETS', 'enuygun': 'ENUYGUN',
    'domino': "Domino's", 'coffy': 'Coffy', 'farfetch': 'FARFETCH', 'treva': 'Treva',
  };
  for (final entry in brands.entries) { if (text.contains(entry.key)) return entry.value; }
  return '';
}

class CampaignService {
  CampaignService._();
  static final instance = CampaignService._();
  final Set<String> favoriteIds = <String>{};
  List<Campaign> cache = const [];
  List<String> get categories => const ['Tümü', 'Akaryakıt', 'Otomotiv', 'Market', 'Restoran', 'E-ticaret', 'Elektronik', 'Giyim', 'Ev & Yaşam', 'Seyahat', 'Eğlence', 'Sağlık & Kişisel Bakım', 'Spor', 'Diğer Kampanyalar'];

  Future<void> loadUserState() async {
    final uid = Supabase.instance.client.auth.currentUser?.id;
    if (uid == null) return;
    try {
      final rows = await Supabase.instance.client.from('user_favorites').select('campaign_id').eq('user_id', uid);
      favoriteIds..clear()..addAll(List<Map<String, dynamic>>.from(rows).map((r) => '${r['campaign_id'] ?? ''}').where((x) => x.isNotEmpty));
    } catch (_) {}
  }

  bool isFavorite(String id) => favoriteIds.contains(id);
  Future<void> toggleFavorite(String id) async {
    final uid = Supabase.instance.client.auth.currentUser?.id;
    final on = !favoriteIds.contains(id);
    if (on) favoriteIds.add(id); else favoriteIds.remove(id);
    if (uid == null || id.isEmpty) return;
    try {
      if (on) {
        await Supabase.instance.client.from('user_favorites').upsert({'user_id': uid, 'campaign_id': int.tryParse(id) ?? id});
      } else {
        await Supabase.instance.client.from('user_favorites').delete().eq('user_id', uid).eq('campaign_id', int.tryParse(id) ?? id);
      }
    } catch (_) {}
  }

  Future<List<Campaign>> fetchCampaigns() async {
    final r = await Future.wait([
      Supabase.instance.client.from('active_campaigns').select('*').order('id', ascending: false),
      Supabase.instance.client.from('campaign_rules').select('*').order('id', ascending: false),
      Supabase.instance.client.from('banks').select('*').order('name'),
      Supabase.instance.client.from('categories').select('*'),
    ]);
    final raw = List<Map<String, dynamic>>.from(r[0]);
    final rules = List<Map<String, dynamic>>.from(r[1]);
    final banks = List<Map<String, dynamic>>.from(r[2]);
    final cats = List<Map<String, dynamic>>.from(r[3]);
    final bankNames = {for (final b in banks) '${b['id']}': '${b['name'] ?? b['bank_name'] ?? ''}'};
    final catNames = {for (final c in cats) '${c['id']}': '${c['name'] ?? ''}'};
    final rulesByCampaign = <String, List<Map<String, dynamic>>>{};
    for (final rule in rules) {
      final id = '${rule['campaign_id'] ?? ''}'.trim();
      if (id.isNotEmpty) rulesByCampaign.putIfAbsent(id, () => <Map<String, dynamic>>[]).add(Map<String, dynamic>.from(rule));
    }

    final out = <Campaign>[];
    for (final src in raw) {
      final m = Map<String, dynamic>.from(src);
      final bid = '${m['bank_id'] ?? ''}', cid = '${m['category_id'] ?? ''}', id = '${m['id'] ?? ''}';
      if ('${m['bank_name'] ?? ''}'.trim().isEmpty && bankNames[bid] != null) m['bank_name'] = bankNames[bid];
      if ('${m['category'] ?? ''}'.trim().isEmpty && catNames[cid] != null) m['category'] = catNames[cid];
      m['title'] = _cleanText('${m['title'] ?? ''}');
      m['merchant'] = _cleanText('${m['merchant'] ?? ''}');
      m['source_url'] = '${m['source_url'] ?? ''}'.trim();
      m['description'] = _cleanText('${m['description'] ?? ''}');
      m['_rules'] = rulesByCampaign[id] ?? const <Map<String, dynamic>>[];

      final campaignRules = m['_rules'] as List;
      if (campaignRules.isNotEmpty) {
        final firstRule = campaignRules.first as Map<String, dynamic>;
        if ('${m['card_name'] ?? ''}'.trim().isEmpty && '${firstRule['card_name'] ?? ''}'.trim().isNotEmpty) m['card_name'] = firstRule['card_name'];
        if ('${m['network'] ?? ''}'.trim().isEmpty && '${firstRule['network'] ?? ''}'.trim().isNotEmpty) m['network'] = firstRule['network'];
        if ('${m['customer_type'] ?? ''}'.trim().isEmpty && '${firstRule['customer_type'] ?? ''}'.trim().isNotEmpty) m['customer_type'] = firstRule['customer_type'];
        if ('${m['card_type'] ?? ''}'.trim().isEmpty && '${firstRule['card_type'] ?? ''}'.trim().isNotEmpty) m['card_type'] = firstRule['card_type'];
        if ('${m['campaign_text'] ?? ''}'.trim().isEmpty && '${firstRule['campaign_text'] ?? ''}'.trim().isNotEmpty) m['campaign_text'] = firstRule['campaign_text'];
        if ('${m['terms'] ?? ''}'.trim().isEmpty && '${firstRule['terms'] ?? ''}'.trim().isNotEmpty) m['terms'] = firstRule['terms'];
      }

      m['_clean_description'] = _bestDescription(m);
      if (!_real(m)) continue;
      final blob = normalizeCampaignText([m['title'], m['_clean_description'], m['merchant']].where((x) => x != null).join(' '));
      if ('${m['card_name'] ?? ''}'.trim().isEmpty) {
        const known = {'world': 'World', 'axess': 'Axess', 'bonus': 'Bonus', 'maximum': 'Maximum', 'paraf': 'Paraf', 'cardfinans': 'CardFinans', 'bankkart': 'Bankkart', 'wings': 'Wings', 'free': 'Free', 'advantage': 'Advantage', 'saglam kart': 'Sağlam Kart', 'happy card': 'Happy Card'};
        for (final e in known.entries) { if (blob.contains(e.key)) { m['card_name'] = e.value; break; } }
      }
      if ('${m['network'] ?? ''}'.trim().isEmpty) {
        if (RegExp(r'\bvisa\b').hasMatch(blob)) m['network'] = 'Visa';
        else if (RegExp(r'\bmastercard\b').hasMatch(blob)) m['network'] = 'Mastercard';
        else if (RegExp(r'\btroy\b').hasMatch(blob)) m['network'] = 'Troy';
      }
      m['merchant'] = _inferMerchant('${m['merchant'] ?? ''}', '${m['title'] ?? ''}', '${m['_clean_description'] ?? ''}');
      m['category'] = _inferCategory('${m['category'] ?? ''}', '${m['title'] ?? ''}', '${m['_clean_description'] ?? ''}');
      out.add(Campaign(m));
    }

    final seen = <String>{};
    cache = out.where((c) {
      final key = normalizeCampaignText(c.sourceUrl).isNotEmpty ? normalizeCampaignText(c.sourceUrl) : '${normalizeCampaignText(c.title)}|${normalizeCampaignText(c.bankName)}';
      return seen.add(key);
    }).toList();
    return cache;
  }

  bool _real(Map<String, dynamic> c) {
    final t = normalizeCampaignText('${c['title'] ?? ''}');
    final u = '${c['source_url'] ?? ''}'.trim();
    final description = normalizeCampaignText('${c['_clean_description'] ?? ''}');
    if (t.isEmpty || u.isEmpty || description.isEmpty) return false;
    if (!u.startsWith('http://') && !u.startsWith('https://')) return false;

    const blocked = [
      'kvkk', 'aydinlatma metni', 'cerez politikasi', 'gizlilik politikasi', 'sifre belirleme',
      'internet alisveris yetkisi', 'visa tek tikla ode', 'test kampany', 'tarayiciniz desteklenmiyor',
      'sunucuda gecici bir hata', 'kampanyalar | axess', 'kampanyalar | kampanyalar',
      'kampanya sonuclari', 'kampanya arsivi', 'biten kampanyalar', 'gecmis kampanyalar',
    ];
    if (blocked.any(t.contains)) return false;

    const genericTitles = [
      'hobi ve oyuncak', 'sigorta ve bireysel emeklilik', 'kampanyalar', 'tüm kampanyalar',
      'gecmis kampanyalar', 'kampanyalar sayfasi', 'kampanyalar sayfası', 'genel kampanyalar',
      'diğer kampanyalar', 'turuncu firsatlar', 'güncel kampanyalar', 'guncel kampanyalar',
      'kredi karti kampanyalari', 'kredi kartı kampanyaları', 'surdurulebilirlik kampanyalari',
      'gastroclub ayricaliklari', 'finansman kampanyalari', 'sigorta kampanyalari',
      'yatirim kampanyalari', 'dijital bankacilik kampanyalari', 'ticari kampanyalar',
      'yapı sektörü ve iklimlendirme', 'yapi sektoru ve iklimlendirme', 'turizm ve seyahat',
      'mobilya ve dekorasyon', 'market ve gida', 'market ve gıda', 'elektronik ve telekomünikasyon',
      'elektronik ve telekomunikasyon', 'e-ticaret', 'giyim ve aksesuar', 'beyaz eşya ve ev aletleri',
      'beyaz esya ve ev aletleri', 'akaryakıt', 'akaryakit', 'kuyum, optik ve saat',
      'eğitim, kitap ve kırtasiye', 'egitim, kitap ve kirtasiye',
    ];
    if (genericTitles.contains(t)) return false;
    if (t.startsWith('kampanyalar') || t.startsWith('guncel kampanyalar')) return false;

    final urlLow = normalizeCampaignText(u);
    const archiveUrlParts = ['/arsiv', 'gecmis-kampanyalar', 'kampanya-arsivi', 'kampanya-sonuclari'];
    if (archiveUrlParts.any(urlLow.contains)) return false;

    final active = c['is_active'];
    if (active is bool && !active) return false;
    final now = DateTime.now(), today = DateTime(now.year, now.month, now.day);
    final start = Campaign.parseDate('${c['start_date'] ?? ''}');
    final end = Campaign.parseDate('${c['end_date'] ?? ''}');
    if (start != null && end != null && end.isBefore(start)) return false;
    if (start != null && start.isAfter(today)) return false;
    if (end != null && end.isBefore(today)) return false;

    final bank = '${c['bank_id'] ?? ''}'.trim().isNotEmpty || '${c['bank_name'] ?? ''}'.trim().isNotEmpty;
    if (!bank) return false;
    final hasOfferSignal = RegExp(r'(?:%\s*\d+|\d[\d., ]*\s*tl|\d+\s*taksit|bonus|puan|indirim|avantaj|hediye|ucretsiz|ücretsiz|faizsiz)', caseSensitive: false).hasMatch('$t $description');
    final hasRule = (c['_rules'] as List?)?.isNotEmpty == true;
    if (start == null && end == null && !hasOfferSignal && !hasRule) return false;
    return true;
  }

  bool _matches(String rule, String actual) {
    final r = normalizeCampaignText(rule), a = normalizeCampaignText(actual);
    if (r.isEmpty || r == '*' || r == 'all' || r == 'tum' || r == 'hepsi') return true;
    if (a.isEmpty) return false;
    final parts = r.split(RegExp(r'[,;/|]')).map((x) => x.trim()).where((x) => x.isNotEmpty);
    const aliases = {
      'kredi': ['kredi', 'kredi karti', 'credit'], 'kredi karti': ['kredi', 'kredi karti', 'credit'],
      'banka': ['banka', 'banka karti', 'bankamatik', 'debit'], 'bankamatik': ['banka', 'banka karti', 'bankamatik', 'debit'],
      'bireysel': ['bireysel', 'individual'], 'ticari': ['ticari', 'business', 'commercial'],
      'troy': ['troy'], 'visa': ['visa'], 'mastercard': ['mastercard'],
    };
    bool eq(String x, String y) {
      if (x == y) return true;
      if ({x, ...(aliases[x] ?? const <String>[])}.intersection({y, ...(aliases[y] ?? const <String>[])}).isNotEmpty) return true;
      const f = ['world', 'bonus', 'axess', 'wings', 'free', 'maximum', 'paraf', 'bankkart', 'cardfinans', 'advantage', 'play', 'adios', 'saglam kart', 'happy card'];
      return f.any((z) => (x == z && y.startsWith('$z ')) || (y == z && x.startsWith('$z ')));
    }
    return parts.any((p) => eq(p, a));
  }

  bool _matchesNetworkRule(Map<String, dynamic> rule, String actual) {
    final explicit = '${rule['network'] ?? ''}'.trim();
    if (explicit.isNotEmpty) return _matches(explicit, actual);
    final eligible = rule['eligible_networks'];
    if (eligible is List && eligible.isNotEmpty) return eligible.any((x) => _matches('$x', actual));
    return true;
  }

  bool matchesCard(Campaign c, UserCard card) {
    final rules = (c.data['_rules'] as List?)?.whereType<Map<String, dynamic>>().toList() ?? const [];
    if (rules.isNotEmpty) {
      return rules.any((r) =>
          _matches('${r['bank_name'] ?? r['bank'] ?? r['card_bank'] ?? ''}', card.bank) &&
          _matches('${r['card_name'] ?? r['card'] ?? ''}', card.card) &&
          _matchesNetworkRule(r, card.network) &&
          _matches('${r['customer_type'] ?? r['customerType'] ?? ''}', card.customerType) &&
          _matches('${r['card_type'] ?? r['cardType'] ?? ''}', card.cardType));
    }
    return _matches('${c.data['bank_name'] ?? c.data['bank'] ?? ''}', card.bank) &&
        _matches('${c.data['card_name'] ?? ''}', card.card) &&
        _matches('${c.data['network'] ?? ''}', card.network) &&
        _matches('${c.data['customer_type'] ?? ''}', card.customerType) &&
        _matches('${c.data['card_type'] ?? ''}', card.cardType);
  }

  bool matchesAnyCard(Campaign c, List<UserCard> cards) => cards.any((x) => matchesCard(c, x));
}
