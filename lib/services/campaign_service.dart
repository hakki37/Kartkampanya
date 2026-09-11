import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'card_service.dart';

String normalizeCampaignText(String v) => _cleanText(v).toLowerCase().trim()
    .replaceAll('ı', 'i').replaceAll('İ', 'i').replaceAll('ğ', 'g').replaceAll('Ğ', 'g')
    .replaceAll('ü', 'u').replaceAll('Ü', 'u').replaceAll('ş', 's').replaceAll('Ş', 's')
    .replaceAll('ö', 'o').replaceAll('Ö', 'o').replaceAll('ç', 'c').replaceAll('Ç', 'c');

String _cleanText(String value) {
  var v = value
      .replaceAll(RegExp(r'<[^>]*>'), ' ')
      .replaceAll(RegExp(r'\s+'), ' ')
      .trim();
  v = v.replaceAllMapped(RegExp(r'&#x([0-9a-fA-F]+);'), (m) {
    final n = int.tryParse(m.group(1)!, radix: 16);
    return n == null ? m.group(0)! : String.fromCharCode(n);
  });
  v = v.replaceAllMapped(RegExp(r'&#(\d+);'), (m) {
    final n = int.tryParse(m.group(1)!);
    return n == null ? m.group(0)! : String.fromCharCode(n);
  });
  const entities = {
    '&amp;': '&', '&quot;': '"', '&apos;': "'", '&nbsp;': ' ',
    '&lt;': '<', '&gt;': '>', '&ndash;': '–', '&mdash;': '—',
    '&rsquo;': '’', '&lsquo;': '‘', '&rdquo;': '”', '&ldquo;': '“',
  };
  for (final e in entities.entries) {
    v = v.replaceAll(e.key, e.value);
  }
  return v.replaceAll(RegExp(r'^\s*(?:-->|->|[-•]+)\s*'), '').trim();
}

String _bestDescription(Map<String, dynamic> m) {
  final candidates = [
    '${m['campaign_text'] ?? ''}',
    '${m['description'] ?? ''}',
    '${m['conditions'] ?? ''}',
    '${m['terms'] ?? ''}',
  ].map(_cleanText).where((x) => x.isNotEmpty).toList();
  const junk = [
    'başvuru işlemleri ayrıcalıklar', 'başvuru işlemleri', 'ayrıcalıklar fırsat',
    'platinum dünyası', 'milplus.com.tr', 'çerez politikası', 'gizlilik politikası',
  ];
  for (final text in candidates) {
    final low = normalizeCampaignText(text);
    if (!junk.any(low.contains)) return text;
  }
  return candidates.isEmpty ? '' : candidates.first;
}

class Campaign {
  final Map<String, dynamic> data;
  const Campaign(this.data);
  String get id => '${data['id'] ?? data['source_url'] ?? ''}';
  String get brand => _cleanText('${data['merchant'] ?? data['brand'] ?? data['bank_name'] ?? 'Kampanya'}');
  String get title => _cleanText('${data['title'] ?? 'Yeni Kampanya'}');
  String get description => _cleanText('${data['_clean_description'] ?? data['campaign_text'] ?? data['description'] ?? data['conditions'] ?? ''}');
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
      Supabase.instance.client.from('campaign_rules').select('*'),
      Supabase.instance.client.from('banks').select('*').order('name'),
      Supabase.instance.client.from('categories').select('*'),
    ]);
    final raw = List<Map<String, dynamic>>.from(r[0]);
    final rules = List<Map<String, dynamic>>.from(r[1]);
    final banks = List<Map<String, dynamic>>.from(r[2]);
    final cats = List<Map<String, dynamic>>.from(r[3]);
    final bankNames = {for (final b in banks) '${b['id']}': '${b['name'] ?? b['bank_name'] ?? ''}'};
    final catNames = {for (final c in cats) '${c['id']}': '${c['name'] ?? ''}'};
    final out = <Campaign>[];

    for (final src in raw) {
      final m = Map<String, dynamic>.from(src);
      final bid = '${m['bank_id'] ?? ''}', cid = '${m['category_id'] ?? ''}';
      if ('${m['bank_name'] ?? ''}'.trim().isEmpty && bankNames[bid] != null) m['bank_name'] = bankNames[bid];
      if ('${m['category'] ?? ''}'.trim().isEmpty && catNames[cid] != null) m['category'] = catNames[cid];
      m['title'] = _cleanText('${m['title'] ?? ''}');
      m['merchant'] = _cleanText('${m['merchant'] ?? ''}');
      m['source_url'] = '${m['source_url'] ?? m['detail_url'] ?? m['url'] ?? ''}'.trim();
      m['campaign_text'] = _cleanText('${m['campaign_text'] ?? ''}');
      m['description'] = _cleanText('${m['description'] ?? ''}');
      m['conditions'] = _cleanText('${m['conditions'] ?? ''}');
      m['terms'] = _cleanText('${m['terms'] ?? ''}');
      if (!_real(m)) continue;
      final id = '${m['id'] ?? ''}';
      m['_rules'] = rules.where((x) => '${x['campaign_id'] ?? ''}' == id).map(Map<String, dynamic>.from).toList();
      m['_clean_description'] = _bestDescription(m);
      final blob = normalizeCampaignText([m['title'], m['merchant'], m['campaign_text'], m['description'], m['conditions'], m['terms']].where((x) => x != null).join(' '));
      if ('${m['card_name'] ?? ''}'.trim().isEmpty) {
        const known = {'world': 'World', 'axess': 'Axess', 'bonus': 'Bonus', 'maximum': 'Maximum', 'paraf': 'Paraf', 'cardfinans': 'CardFinans', 'bankkart': 'Bankkart', 'wings': 'Wings', 'free': 'Free', 'advantage': 'Advantage'};
        for (final e in known.entries) { if (blob.contains(e.key)) { m['card_name'] = e.value; break; } }
      }
      if ('${m['network'] ?? ''}'.trim().isEmpty) {
        if (RegExp(r'\bvisa\b').hasMatch(blob)) m['network'] = 'Visa';
        else if (RegExp(r'\bmastercard\b').hasMatch(blob)) m['network'] = 'Mastercard';
        else if (RegExp(r'\btroy\b').hasMatch(blob)) m['network'] = 'Troy';
      }
      out.add(Campaign(m));
    }
    final seen = <String>{};
    cache = out.where((c) => seen.add(c.id.isNotEmpty ? 'id:${c.id}' : '${normalizeCampaignText(c.sourceUrl)}|${normalizeCampaignText(c.title)}')).toList();
    return cache;
  }

  bool _real(Map<String, dynamic> c) {
    final t = normalizeCampaignText('${c['title'] ?? ''}'), u = '${c['source_url'] ?? ''}'.trim();
    if (t.isEmpty || u.isEmpty) return false;
    const blocked = ['kvkk', 'aydinlatma metni', 'cerez politikasi', 'gizlilik politikasi', 'sifre belirleme', 'internet alisveris yetkisi', 'visa tek tikla ode', 'test kampany'];
    if (blocked.any(t.contains)) return false;
    final active = c['is_active'];
    if (active is bool && !active) return false;
    final now = DateTime.now(), start = Campaign.parseDate('${c['start_date'] ?? ''}'), end = Campaign.parseDate('${c['end_date'] ?? ''}');
    if (start != null && start.isAfter(DateTime(now.year, now.month, now.day))) return false;
    if (end != null && end.isBefore(DateTime(now.year, now.month, now.day))) return false;
    return '${c['bank_id'] ?? ''}'.trim().isNotEmpty || '${c['bank_name'] ?? ''}'.trim().isNotEmpty;
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
    };
    bool eq(String x, String y) {
      if (x == y) return true;
      if ({x, ...(aliases[x] ?? const <String>[])}.intersection({y, ...(aliases[y] ?? const <String>[])}).isNotEmpty) return true;
      const f = ['world', 'bonus', 'axess', 'wings', 'free', 'maximum', 'paraf', 'bankkart', 'cardfinans', 'advantage', 'play', 'adios', 'saglam kart', 'happy card'];
      return f.any((z) => (x == z && y.startsWith('$z ')) || (y == z && x.startsWith('$z ')));
    }
    return parts.any((p) => eq(p, a));
  }

  bool matchesCard(Campaign c, UserCard card) {
    final rules = (c.data['_rules'] as List?)?.whereType<Map<String, dynamic>>().toList() ?? const [];
    if (rules.isNotEmpty) {
      return rules.any((r) =>
          _matches('${r['bank_name'] ?? r['bank'] ?? r['card_bank'] ?? ''}', card.bank) &&
          _matches('${r['card_name'] ?? r['card'] ?? ''}', card.card) &&
          _matches('${r['network'] ?? ''}', card.network) &&
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
