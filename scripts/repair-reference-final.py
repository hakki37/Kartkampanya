from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')


def block_end(src, start):
    brace = src.find('{', start)
    if brace < 0:
        raise SystemExit('opening brace not found')
    depth = 0
    quote = None
    esc = False
    line_comment = False
    block_comment = False
    i = brace
    while i < len(src):
        ch = src[i]
        nxt = src[i + 1] if i + 1 < len(src) else ''
        if line_comment:
            if ch == '\n':
                line_comment = False
        elif block_comment:
            if ch == '*' and nxt == '/':
                block_comment = False
                i += 1
        elif quote:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == quote:
                quote = None
        else:
            if ch == '/' and nxt == '/':
                line_comment = True
                i += 1
            elif ch == '/' and nxt == '*':
                block_comment = True
                i += 1
            elif ch in "'\"":
                quote = ch
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return i + 1
        i += 1
    raise SystemExit('closing brace not found')


def replace_class(src, name, replacement):
    marker = 'class ' + name
    start = src.find(marker)
    if start < 0:
        raise SystemExit(name + ' not found')
    return src[:start] + replacement + src[block_end(src, start):]


def remove_duplicate_class(src, name):
    marker = 'class ' + name
    first = src.find(marker)
    if first < 0:
        return src
    while True:
        second = src.find(marker, first + 1)
        if second < 0:
            return src
        src = src[:second] + src[block_end(src, second):]


def replace_method(src, state_name, method_name, replacement):
    state = src.find('class ' + state_name)
    if state < 0:
        raise SystemExit(state_name + ' not found')
    marker = '  @override\n  Widget ' + method_name
    start = src.find(marker, state)
    if start < 0:
        raise SystemExit(state_name + '.' + method_name + ' not found')
    return src[:start] + replacement + src[block_end(src, start):]


# Remove duplicate generated helper classes before rebuilding the affected screens.
s = remove_duplicate_class(s, '_LoginPageState')
s = remove_duplicate_class(s, '_MainShellState')
s = remove_duplicate_class(s, '_HomeCat')

# Keep campaign cards simple and robust. The existing state/fetch/matching logic remains intact.
build = r'''  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<Map<String, dynamic>>>(
      future: future,
      builder: (context, snapshot) {
        var rows = snapshot.data ?? <Map<String, dynamic>>[];

        if (search.text.trim().isNotEmpty) {
          final q = _norm(search.text);
          rows = rows.where((c) {
            final text = [
              c['title'],
              c['merchant'],
              c['category'],
              c['description'],
              c['campaign_text'],
            ].where((x) => x != null).join(' ');
            return _norm(text).contains(q);
          }).toList();
        }

        if (category.isNotEmpty) {
          rows = rows.where((c) =>
              campaignSection(c) == category ||
              '${c['category'] ?? ''}' == category).toList();
        }

        if (showFavoritesOnly) {
          rows = rows.where((c) => favoriteIds.contains(campaignId(c))).toList();
        }

        if (widget.mode == 'matched' && widget.cards.isNotEmpty) {
          rows = rows.where((c) =>
              widget.cards.any((card) => cardMatches(c, card))).toList();
        }

        final visibleRows = widget.mode == 'home' ? rows.take(8).toList() : rows;

        return Scaffold(
          backgroundColor: const Color(0xFFF8F7FC),
          body: RefreshIndicator(
            onRefresh: () async {
              setState(() {
                future = fetchCampaigns();
              });
              await future;
            },
            child: ListView(
              padding: const EdgeInsets.fromLTRB(16, 14, 16, 30),
              children: [
                Row(
                  children: [
                    Container(
                      width: 42,
                      height: 42,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFF8B5CF6), Color(0xFF5B21B6)],
                        ),
                        borderRadius: BorderRadius.circular(13),
                      ),
                      child: const Icon(Icons.credit_card_rounded, color: Colors.white),
                    ),
                    const SizedBox(width: 10),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Kart Kampanya',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.w900,
                              color: Color(0xFF211D2D),
                            ),
                          ),
                          Text(
                            'Tüm Banka Kampanyaları Tek Uygulamada',
                            style: TextStyle(fontSize: 10, color: Color(0xFF777187)),
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      onPressed: () => setState(() => future = fetchCampaigns()),
                      icon: const Icon(Icons.refresh_rounded),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: search,
                  onChanged: (_) => setState(() {}),
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Icons.search_rounded),
                    hintText: 'Kampanya, marka veya kategori ara...',
                  ),
                ),
                const SizedBox(height: 10),
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: [
                      _pill(
                        '▦',
                        'Tümü',
                        category.isEmpty && !showFavoritesOnly,
                        () => setState(() {
                          category = '';
                          showFavoritesOnly = false;
                        }),
                      ),
                      _pill(
                        '✧',
                        'Bana Uygun',
                        widget.mode == 'matched',
                        () => setState(() => category = ''),
                      ),
                      _pill(
                        '♥',
                        'Favoriler',
                        showFavoritesOnly,
                        () => setState(() => showFavoritesOnly = !showFavoritesOnly),
                      ),
                    ],
                  ),
                ),
                if (widget.mode == 'home') ...[
                  const SizedBox(height: 14),
                  Container(
                    height: 145,
                    padding: const EdgeInsets.all(17),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF5424CF), Color(0xFF8C62F7)],
                      ),
                      borderRadius: BorderRadius.circular(23),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Yaz Fırsatları\nDevam Ediyor!',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 23,
                            height: 1.0,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                        const SizedBox(height: 8),
                        const Text(
                          'Alışverişte kazancının\ntam zamanını yakala.',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                        const Spacer(),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 6),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(13),
                          ),
                          child: const Text(
                            'Tüm Kampanyalar  →',
                            style: TextStyle(
                              color: Color(0xFF5B21B6),
                              fontSize: 10,
                              fontWeight: FontWeight.w900,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'Kategoriler',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w900,
                      color: Color(0xFF211D2D),
                    ),
                  ),
                  const SizedBox(height: 9),
                  GridView.count(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    crossAxisCount: 4,
                    crossAxisSpacing: 8,
                    mainAxisSpacing: 8,
                    childAspectRatio: 1.02,
                    children: const [
                      _HomeCat('⛽', 'Akaryakıt', 0xFFFFE4E8),
                      _HomeCat('🛒', 'Market', 0xFFE1F8EF),
                      _HomeCat('🍴', 'Restoran', 0xFFFFEAD8),
                      _HomeCat('🛍', 'E-Ticaret', 0xFFE8E1FF),
                      _HomeCat('📱', 'Elektronik', 0xFFE1EEFF),
                      _HomeCat('✈', 'Seyahat', 0xFFFFE8D8),
                      _HomeCat('👕', 'Giyim', 0xFFFFE2F1),
                      _HomeCat('⌂', 'Ev & Yaşam', 0xFFE3F4E9),
                    ],
                  ),
                  const SizedBox(height: 16),
                ],
                if (snapshot.connectionState == ConnectionState.waiting)
                  const Padding(
                    padding: EdgeInsets.all(40),
                    child: Center(child: CircularProgressIndicator()),
                  ),
                if (snapshot.hasError)
                  const Padding(
                    padding: EdgeInsets.all(30),
                    child: Center(
                      child: Text(
                        'Kampanyalar yüklenemedi.\nAşağı çekerek tekrar dene.',
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ),
                if (snapshot.connectionState != ConnectionState.waiting &&
                    !snapshot.hasError &&
                    visibleRows.isEmpty)
                  const Padding(
                    padding: EdgeInsets.all(30),
                    child: Center(child: Text('Kampanya bulunamadı.')),
                  ),
                if (snapshot.connectionState != ConnectionState.waiting && !snapshot.hasError)
                  ...visibleRows.map(
                    (c) => Card(
                      margin: const EdgeInsets.only(bottom: 10),
                      color: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(18),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(14),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Expanded(
                                  child: Text(
                                    '${c['title'] ?? c['campaign_text'] ?? 'Kampanya'}',
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                    style: const TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.w900,
                                      color: Color(0xFF211D2D),
                                    ),
                                  ),
                                ),
                                IconButton(
                                  onPressed: () => setState(() {
                                    final id = campaignId(c);
                                    if (favoriteIds.contains(id)) {
                                      favoriteIds.remove(id);
                                    } else {
                                      favoriteIds.add(id);
                                    }
                                  }),
                                  icon: Icon(
                                    favoriteIds.contains(campaignId(c))
                                        ? Icons.favorite
                                        : Icons.favorite_border,
                                    color: const Color(0xFF6D3DF5),
                                  ),
                                ),
                              ],
                            ),
                            if (c['merchant'] != null)
                              Text(
                                '${c['merchant']}',
                                style: const TextStyle(
                                  fontWeight: FontWeight.w700,
                                  color: Color(0xFF6D3DF5),
                                ),
                              ),
                            const SizedBox(height: 6),
                            Text(
                              '${c['campaign_text'] ?? c['description'] ?? c['conditions'] ?? ''}',
                              maxLines: 4,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(
                                fontSize: 12,
                                color: Color(0xFF55515F),
                                height: 1.35,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              campaignSection(c),
                              style: const TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.w800,
                                color: Color(0xFF777187),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _pill(String icon, String label, bool selected, VoidCallback onTap) {
    return Padding(
      padding: const EdgeInsets.only(right: 7),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(15),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
          decoration: BoxDecoration(
            color: selected ? const Color(0xFF6D3DF5) : const Color(0xFFEFEAF9),
            borderRadius: BorderRadius.circular(15),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                icon,
                style: TextStyle(
                  color: selected ? Colors.white : const Color(0xFF6D3DF5),
                ),
              ),
              const SizedBox(width: 5),
              Text(
                label,
                style: TextStyle(
                  color: selected ? Colors.white : const Color(0xFF4B4655),
                  fontSize: 11,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
'''

s = replace_method(s, '_CampaignsPageState', 'build', build)

# Replace CategoriesPage completely with a balanced implementation.
cat = r'''class CategoriesPage extends StatelessWidget {
  const CategoriesPage({super.key});

  @override
  Widget build(BuildContext context) {
    const data = [
      ['▦', 'Tümü', 0xFFE9DEFF],
      ['⛽', 'Akaryakıt', 0xFFFFE4E8],
      ['🛒', 'Market', 0xFFE1F8EF],
      ['🍴', 'Restoran', 0xFFFFEAD8],
      ['🛍', 'E-Ticaret', 0xFFE8E1FF],
      ['📱', 'Elektronik', 0xFFE1EEFF],
      ['👕', 'Giyim', 0xFFFFE2F1],
      ['✈', 'Seyahat', 0xFFFFE8D8],
      ['🚗', 'Otomotiv', 0xFFE3F0FF],
      ['⌂', 'Ev & Yaşam', 0xFFE3F4E9],
      ['💊', 'Sağlık', 0xFFFFE4EF],
      ['🎬', 'Eğlence', 0xFFE9E2FF],
      ['📚', 'Eğitim', 0xFFE1F4FF],
      ['💼', 'Finans', 0xFFE8F5E9],
      ['•', 'Diğer', 0xFFF0EDF5],
    ];

    return ListView(
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 30),
      children: [
        const Text(
          'Kategoriler',
          style: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.w900,
            color: Color(0xFF211D2D),
          ),
        ),
        const SizedBox(height: 6),
        const Text(
          'Kampanyaları kategoriye göre keşfet.',
          style: TextStyle(color: Color(0xFF777187)),
        ),
        const SizedBox(height: 16),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: data.length,
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 3,
            crossAxisSpacing: 10,
            mainAxisSpacing: 10,
            childAspectRatio: 1,
          ),
          itemBuilder: (context, i) {
            final x = data[i];
            return Container(
              decoration: BoxDecoration(
                color: Color(x[2] as int),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(x[0] as String, style: const TextStyle(fontSize: 27)),
                  const SizedBox(height: 6),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    child: Text(
                      x[1] as String,
                      maxLines: 2,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF353146),
                      ),
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ],
    );
  }
}
'''

s = replace_class(s, 'CategoriesPage', cat)

# Add exactly one HomeCat helper at the end if the generated source does not contain one.
if 'class _HomeCat extends StatelessWidget' not in s:
    s += r'''

class _HomeCat extends StatelessWidget {
  final String icon;
  final String label;
  final int bg;

  const _HomeCat(this.icon, this.label, this.bg);

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Color(bg),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(icon, style: const TextStyle(fontSize: 20)),
          const SizedBox(height: 3),
          Text(
            label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
              fontSize: 9,
              color: Color(0xFF353146),
              fontWeight: FontWeight.w800,
            ),
          ),
        ],
      ),
    );
  }
}
'''

p.write_text(s, encoding='utf-8')
print('compile-safe reference repair applied')
