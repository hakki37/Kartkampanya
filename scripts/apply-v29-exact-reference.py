from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')


def replace_class(src, name, replacement):
    start = src.find('class ' + name)
    if start < 0:
        raise SystemExit(name + ' not found')
    brace = src.find('{', start)
    depth = 0
    quote = None
    esc = False
    for i in range(brace, len(src)):
        ch = src[i]
        if quote:
            if esc: esc = False
            elif ch == '\\': esc = True
            elif ch == quote: quote = None
        elif ch in "'\"": quote = ch
        elif ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return src[:start] + replacement + src[i+1:]
    raise SystemExit(name + ' end not found')


def replace_method(src, state_name, method_name, replacement):
    state = src.find('class ' + state_name)
    start = src.find('  @override\n  Widget ' + method_name, state)
    if start < 0:
        raise SystemExit(state_name + ' ' + method_name + ' not found')
    brace = src.find('{', start)
    depth = 0
    quote = None
    esc = False
    for i in range(brace, len(src)):
        ch = src[i]
        if quote:
            if esc: esc = False
            elif ch == '\\': esc = True
            elif ch == quote: quote = None
        elif ch in "'\"": quote = ch
        elif ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return src[:start] + replacement + src[i+1:]
    raise SystemExit(method_name + ' end not found')

# Exact light reference palette.
s = s.replace("""      theme: ThemeData(\n        useMaterial3: true,\n        colorScheme: ColorScheme.fromSeed(\n          seedColor: const Color(0xFF5B4BDB),\n          brightness: Brightness.dark,\n        ),\n        scaffoldBackgroundColor: const Color(0xFF081120),\n        appBarTheme: const AppBarTheme(\n          elevation: 0,\n          backgroundColor: const Color(0xFF081120),\n          foregroundColor: Colors.white,\n        ),\n        cardTheme: const CardThemeData(\n          elevation: 0,\n          margin: EdgeInsets.zero,\n          surfaceTintColor: Colors.transparent,\n        ),\n      ),""", """      theme: ThemeData(\n        useMaterial3: true,\n        brightness: Brightness.light,\n        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF6B3FEF), brightness: Brightness.light),\n        scaffoldBackgroundColor: const Color(0xFFF9F8FD),\n        appBarTheme: const AppBarTheme(elevation: 0, scrolledUnderElevation: 0, backgroundColor: Color(0xFFF9F8FD), foregroundColor: Color(0xFF20202B)),\n        inputDecorationTheme: const InputDecorationTheme(\n          filled: true, fillColor: Colors.white,\n          border: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(16)), borderSide: BorderSide(color: Color(0xFFE0DCE9))),\n          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(16)), borderSide: BorderSide(color: Color(0xFFE0DCE9))),\n          focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(16)), borderSide: BorderSide(color: Color(0xFF6B3FEF), width: 1.4)),\n          contentPadding: EdgeInsets.symmetric(horizontal: 14, vertical: 14),\n        ),\n        cardTheme: const CardThemeData(elevation: 0, margin: EdgeInsets.zero, surfaceTintColor: Colors.transparent),\n      ),""", 1)

# Add exact reference helpers once.
if 'String _v29CleanTitle(' not in s:
    marker = 'class SmartCampaignCard extends StatelessWidget {'
    helpers = r'''String _v29CleanTitle(Map<String,dynamic> c) {
  final raw = decodeHtmlEntities('${c['title'] ?? ''}').replaceAll(RegExp(r'\s+'), ' ').trim();
  final bad = RegExp(r'(men[uü]|kampanyalar|kredi kartlar[iı]|banka kartlar[iı]|[oö]deme kolayl[iı]klar[iı]|blog|hemen ba[sş]vur|ba[sş]vur arama)', caseSensitive:false);
  if (raw.length > 80 && bad.hasMatch(raw)) {
    final merchant = decodeHtmlEntities('${c['merchant'] ?? ''}').trim();
    final reward = '${c['reward_type'] ?? ''}'.trim();
    final value = '${c['reward_value'] ?? c['reward'] ?? ''}'.trim();
    if (merchant.isNotEmpty && value.isNotEmpty) return '$merchant’ta $value ${reward.isNotEmpty ? reward : 'Avantaj'}';
    if (merchant.isNotEmpty) return merchant;
  }
  return raw.isEmpty ? 'Kampanya' : raw;
}

String _v29MerchantLogo(String merchant) {
  final m = _norm(merchant);
  const map = <String,String>{
    'petrol ofisi':'https://cdn.brandfetch.io/petrolofisi.com/w/600/h/600/logo',
    'migros':'https://cdn.brandfetch.io/migros.com.tr/w/600/h/600/logo',
    'trendyol':'https://cdn.brandfetch.io/trendyol.com/w/600/h/600/logo',
    'shell':'https://cdn.brandfetch.io/shell.com/w/600/h/600/logo',
    'starbucks':'https://cdn.brandfetch.io/starbucks.com/w/600/h/600/logo',
    'ispark':'https://cdn.brandfetch.io/ispark.istanbul/w/600/h/600/logo',
    'amazon':'https://cdn.brandfetch.io/amazon.com/w/600/h/600/logo',
    'hepsiburada':'https://cdn.brandfetch.io/hepsiburada.com/w/600/h/600/logo',
  };
  for (final e in map.entries) { if (m.contains(e.key)) return e.value; }
  return '';
}

String _v29DateText(Map<String,dynamic> c) {
  final start = '${c['start_date'] ?? ''}'.trim();
  final end = '${c['end_date'] ?? ''}'.trim();
  String fmt(String x) {
    final d = DateTime.tryParse(x);
    if (d == null) return x;
    return '${d.day}-${d.month} ${d.year}';
  }
  if (start.isNotEmpty && end.isNotEmpty) return '${fmt(start)} - ${fmt(end)}';
  if (end.isNotEmpty) return 'Son ${fmt(end)}';
  return 'Süresiz';
}

class _V29Logo extends StatelessWidget {
  final String url;
  const _V29Logo(this.url);
  @override Widget build(BuildContext context) => Container(width:104,height:104,decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(20)),alignment:Alignment.center,padding:const EdgeInsets.all(10),child:url.isEmpty?const Icon(Icons.local_offer_rounded,color:Color(0xFF6B3FEF),size:46):Image.network(url,fit:BoxFit.contain,errorBuilder:(_,__,___)=>const Icon(Icons.local_offer_rounded,color:Color(0xFF6B3FEF),size:46)));
}

'''
    s = s.replace(marker, helpers + marker, 1)

# Exact 5-tab bottom navigation from the reference.
start = s.find('class MainShell extends StatefulWidget {')
if start >= 0:
    end = s.find('class CampaignsPage extends StatefulWidget {', start)
    if end > start:
        shell = r'''class MainShell extends StatefulWidget {
  const MainShell({super.key});
  @override State<MainShell> createState()=>_MainShellState();
}
class _MainShellState extends State<MainShell> {
  int index=0;
  final cards=<UserCard>[];
  @override void initState(){super.initState();loadCards();}
  Future<void> loadCards() async {
    final uid=Supabase.instance.client.auth.currentUser!.id;
    final rows=await Supabase.instance.client.from('user_cards').select().eq('user_id',uid).order('created_at');
    if(!mounted)return;
    setState(()=>cards..clear()..addAll(List<Map<String,dynamic>>.from(rows).map((m)=>UserCard(id:'${m['id']}',bank:'${m['bank_name']}',card:'${m['card_name']}',network:'${m['network']}',customerType:'${m['customer_type']??'Bireysel'}',cardType:'${m['card_type']??'Kredi'}'))));
  }
  Future<void> addCard(UserCard c)async{final uid=Supabase.instance.client.auth.currentUser!.id;await Supabase.instance.client.from('user_cards').insert({'user_id':uid,'bank_name':c.bank,'card_name':c.card,'network':c.network,'customer_type':c.customerType,'card_type':c.cardType});await loadCards();}
  Future<void> deleteCard(UserCard c)async{await Supabase.instance.client.from('user_cards').delete().eq('id',c.id);await loadCards();}
  @override Widget build(BuildContext context){
    final pages=<Widget>[CampaignsPage(cards:cards,mode:'home'),CampaignsPage(cards:cards,mode:'all'),MyCardsPage(cards:cards,onAdd:addCard,onDelete:deleteCard),const CategoriesPage(),const ProfilePage()];
    return Scaffold(backgroundColor:const Color(0xFFF9F8FD),body:SafeArea(child:IndexedStack(index:index,children:pages)),bottomNavigationBar:NavigationBar(backgroundColor:Colors.white,indicatorColor:const Color(0xFFE9DFFF),height:76,selectedIndex:index,onDestinationSelected:(v)=>setState(()=>index=v),destinations:const[
      NavigationDestination(icon:Icon(Icons.home_outlined),selectedIcon:Icon(Icons.home_rounded),label:'Ana Sayfa'),
      NavigationDestination(icon:Icon(Icons.local_offer_outlined),selectedIcon:Icon(Icons.local_offer_rounded),label:'Kampanyalar'),
      NavigationDestination(icon:Icon(Icons.credit_card_outlined),selectedIcon:Icon(Icons.credit_card_rounded),label:'Kartlarım'),
      NavigationDestination(icon:Icon(Icons.grid_view_outlined),selectedIcon:Icon(Icons.grid_view_rounded),label:'Kategoriler'),
      NavigationDestination(icon:Icon(Icons.person_outline_rounded),selectedIcon:Icon(Icons.person_rounded),label:'Profil'),
    ]));
  }
}

'''
        s = s[:start] + shell + s[end:]

# Reference campaign-list screen: search + horizontal chips + compact catalog cards.
build = r'''  @override
  Widget build(BuildContext context) {
    final isHome = widget.mode == 'home';
    return Scaffold(
      backgroundColor: const Color(0xFFF9F8FD),
      body: FutureBuilder<List<Map<String,dynamic>>>(
        future: future,
        builder: (context,snapshot) {
          var rows = List<Map<String,dynamic>>.from(snapshot.data ?? const <Map<String,dynamic>>[]);
          if(search.text.trim().isNotEmpty){final q=_norm(search.text);rows=rows.where((c)=>_norm([c['title'],c['merchant'],c['category'],c['description'],c['campaign_text']].where((x)=>x!=null).join(' ')).contains(q)).toList();}
          if(category.isNotEmpty)rows=rows.where((c)=>campaignSection(c)==category||'${c['category']??''}'==category).toList();
          if(showFavoritesOnly)rows=rows.where((c)=>favoriteIds.contains(campaignId(c))).toList();
          if(widget.mode=='matched'&&widget.cards.isNotEmpty)rows=rows.where((c)=>widget.cards.any((card)=>cardMatches(c,card))).toList();
          return RefreshIndicator(onRefresh:()async{setState(()=>future=fetchCampaigns());await future;},child:ListView(padding:const EdgeInsets.fromLTRB(21,12,21,18),children:[
            if(!isHome) ...[
              Row(children:[Expanded(child:TextField(controller:search,onChanged:(_)=>setState((){}),textInputAction:TextInputAction.search,onSubmitted:(_)=>searchNow(),decoration:const InputDecoration(prefixIcon:Icon(Icons.search_rounded),hintText:'Kampanya, banka veya kategori ara...'))),const SizedBox(width:10),OutlinedButton.icon(onPressed:()=>showFilterSheet(),icon:const Icon(Icons.tune_rounded,size:18),label:const Text('Filtrele'),style:OutlinedButton.styleFrom(foregroundColor:const Color(0xFF3E216F),side:const BorderSide(color:Color(0xFFD9C9F9)),backgroundColor:const Color(0xFFF1EAFF),shape:RoundedRectangleBorder(borderRadius:BorderRadius.circular(15)),padding:const EdgeInsets.symmetric(horizontal:12,vertical:14))) ]),
              const SizedBox(height:12),
              SingleChildScrollView(scrollDirection:Axis.horizontal,child:Row(children:[_v29Chip('Tümü',category.isEmpty,()=>setState(()=>category='')),_v29Chip('Market',category=='Market',()=>setState(()=>category='Market')),_v29Chip('Akaryakıt',category=='Akaryakıt',()=>setState(()=>category='Akaryakıt')),_v29Chip('Yemek',category=='Restoran',()=>setState(()=>category='Restoran')),_v29Chip('Seyahat',category=='Seyahat',()=>setState(()=>category='Seyahat')),_v29Chip('Online',category=='E-ticaret',()=>setState(()=>category='E-ticaret'))])),
              const SizedBox(height:14),
            ],
            if(isHome && search.text.isEmpty) ...[
              const SizedBox(height:2),
              Row(children:[const Expanded(child:Text('Sana Özel Kampanyalar',style:TextStyle(fontSize:22,fontWeight:FontWeight.w900,color:Color(0xFF1F1D28)))),IconButton(onPressed:()=>setState(()=>future=fetchCampaigns()),icon:const Icon(Icons.refresh_rounded,color:Color(0xFF514C59)))]),
              const SizedBox(height:10),
            ],
            if(snapshot.connectionState==ConnectionState.waiting)const Padding(padding:EdgeInsets.all(45),child:Center(child:CircularProgressIndicator())),
            if(snapshot.hasError)const Padding(padding:EdgeInsets.all(30),child:Center(child:Text('Kampanyalar yüklenemedi.\nAşağı çekerek tekrar dene.',textAlign:TextAlign.center))),
            if(snapshot.connectionState!=ConnectionState.waiting&&!snapshot.hasError&&rows.isEmpty)const Padding(padding:EdgeInsets.all(30),child:Center(child:Text('Bu filtreye uygun kampanya bulunamadı.'))),
            if(snapshot.connectionState!=ConnectionState.waiting&&!snapshot.hasError)...rows.map((c)=>SmartCampaignCard(campaign:c,isFavorite:favoriteIds.contains(campaignId(c)),isCompared:compareIds.contains(campaignId(c)),showAllCampaigns:showAllCampaigns,expiringSoon:isExpiringSoon(c),daysRemaining:daysLeft(c),onFavorite:()=>toggleFavorite(c),onCompare:()=>toggleCompare(c),onOpenUrl:openCampaignUrl,requiredSteps:requiredSteps(c),completedSteps:currentProgress(c),onProgressChange:(d)=>changeProgress(c,d)))
          ]));
        },
      ),
    );
  }
  Widget _v29Chip(String text,bool selected,VoidCallback onTap)=>Padding(padding:const EdgeInsets.only(right:8),child:InkWell(onTap:onTap,borderRadius:BorderRadius.circular(20),child:Container(padding:const EdgeInsets.symmetric(horizontal:18,vertical:11),decoration:BoxDecoration(color:selected?const Color(0xFF7B45EF):const Color(0xFFF0EDF7),borderRadius:BorderRadius.circular(20),border:Border.all(color:selected?const Color(0xFF7B45EF):const Color(0xFFE4DFED))),child:Text(text,style:TextStyle(color:selected?Colors.white:const Color(0xFF3D3947),fontSize:13,fontWeight:FontWeight.w700)))));
  }
'''
s = replace_method(s,'_CampaignsPageState','build',build)

# Exact compact card matching the second uploaded reference.
smart = r'''class SmartCampaignCard extends StatelessWidget {
  final Map<String,dynamic> campaign;
  final bool isFavorite,isCompared,showAllCampaigns,expiringSoon;
  final int daysRemaining,requiredSteps,completedSteps;
  final VoidCallback onFavorite,onCompare;
  final Future<void> Function(String url) onOpenUrl;
  final ValueChanged<int> onProgressChange;
  const SmartCampaignCard({super.key,required this.campaign,required this.isFavorite,required this.isCompared,required this.showAllCampaigns,required this.expiringSoon,required this.daysRemaining,required this.onFavorite,required this.onCompare,required this.onOpenUrl,required this.requiredSteps,required this.completedSteps,required this.onProgressChange});
  @override Widget build(BuildContext context){
    final merchant=decodeHtmlEntities('${campaign['merchant']??''}').trim();
    final title=_v29CleanTitle(campaign);
    final category=decodeHtmlEntities('${campaign['category']??''}').trim();
    final bank=decodeHtmlEntities('${campaign['bank_name']??''}').trim();
    final network=decodeHtmlEntities('${campaign['network']??''}').trim();
    final logo=_v29MerchantLogo(merchant);
    final left=daysRemaining;
    final date=_v29DateText(campaign);
    String description=decodeHtmlEntities('${campaign['campaign_text']??campaign['description']??''}').replaceAll(RegExp(r'\s+'),' ').trim();
    if(description.isEmpty)description='Kampanya koşullarını ve detaylarını görmek için Detaylar bölümünü açın.';
    if(description.length>125)description='${description.substring(0,125).trimRight()}...';
    final benefit=_catalogBenefitText(campaign);
    String badge='';
    if(expiringSoon&&left>=0)badge=left==0?'Son Gün':'Son $left Gün';
    else if('${campaign['is_special']??''}'=='true')badge='Size Özel';
    else if(title.toLowerCase().contains('popüler')||title.toLowerCase().contains('popular'))badge='Popüler';
    return Container(margin:const EdgeInsets.only(bottom:12),decoration:BoxDecoration(color:const Color(0xFFFCFBFE),borderRadius:BorderRadius.circular(22),border:Border.all(color:const Color(0xFFDCD8E6),width:1.2)),child:InkWell(borderRadius:BorderRadius.circular(22),onTap:()=>Navigator.of(context).push(MaterialPageRoute(builder:(_)=>CampaignDetailPage(campaign:campaign))),child:Padding(padding:const EdgeInsets.fromLTRB(13,13,13,12),child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[
      Row(crossAxisAlignment:CrossAxisAlignment.start,children:[_V29Logo(logo),const SizedBox(width:13),Expanded(child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[
        Row(crossAxisAlignment:CrossAxisAlignment.start,children:[Expanded(child:Text(title,maxLines:2,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:18,fontWeight:FontWeight.w900,height:1.05,color:Color(0xFF17151F)))),if(badge.isNotEmpty)Container(margin:const EdgeInsets.only(left:6),padding:const EdgeInsets.symmetric(horizontal:9,vertical:7),decoration:BoxDecoration(color:badge.toLowerCase().contains('son')?const Color(0xFFFFDDE0):const Color(0xFFE7DEFF),borderRadius:BorderRadius.circular(18)),child:Text(badge,style:TextStyle(fontSize:10,fontWeight:FontWeight.w900,color:badge.toLowerCase().contains('son')?const Color(0xFFC62F43):const Color(0xFF5A35B8))))]),
        const SizedBox(height:8),Text(description,maxLines:3,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:13,height:1.18,color:Color(0xFF615C68))),
      ])),IconButton(onPressed:onFavorite,visualDensity:VisualDensity.compact,padding:EdgeInsets.zero,icon:Icon(isFavorite?Icons.star_rounded:Icons.star_border_rounded,color:const Color(0xFF5A5662),size:30))]),
      const SizedBox(height:10),
      Wrap(spacing:7,runSpacing:7,children:[if(category.isNotEmpty)_v29InfoChip(Icons.local_gas_station_rounded,category),if(bank.isNotEmpty)_v29InfoChip(Icons.credit_card_rounded,bank),if(network.isNotEmpty)_v29InfoChip(Icons.calendar_month_rounded,date)]),
      const SizedBox(height:10),
      Row(children:[
        if(benefit.trim().isNotEmpty)Expanded(child:Text('🎁 $benefit',maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:11,fontWeight:FontWeight.w800,color:Color(0xFF5C21B6)))) else const Spacer(),
        IconButton(onPressed:onCompare,visualDensity:VisualDensity.compact,icon:Icon(isCompared?Icons.compare_arrows_rounded:Icons.compare_arrows_rounded,color:const Color(0xFF5D5963))),
        const SizedBox(width:3),
        FilledButton(onPressed:()=>Navigator.of(context).push(MaterialPageRoute(builder:(_)=>CampaignDetailPage(campaign:campaign))),style:FilledButton.styleFrom(backgroundColor:const Color(0xFF6D3FEF),foregroundColor:Colors.white,padding:const EdgeInsets.symmetric(horizontal:18,vertical:12),shape:RoundedRectangleBorder(borderRadius:BorderRadius.circular(18))),child:const Text('Detaylar →',style:TextStyle(fontSize:13,fontWeight:FontWeight.w900)))
      ])
    ]))));
  }
  Widget _v29InfoChip(IconData icon,String text)=>Container(padding:const EdgeInsets.symmetric(horizontal:11,vertical:8),decoration:BoxDecoration(color:const Color(0xFFF0ECFA),borderRadius:BorderRadius.circular(18)),child:Row(mainAxisSize:MainAxisSize.min,children:[Icon(icon,size:15,color:const Color(0xFF302A3A)),const SizedBox(width:5),Text(text,maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:10,fontWeight:FontWeight.w700,color:Color(0xFF383342)))]));
}
'''
s = replace_class(s,'SmartCampaignCard',smart)

p.write_text(s,encoding='utf-8')
print('v29 exact reference UI applied')
