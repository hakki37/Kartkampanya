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
    i = brace
    while i < len(src):
        ch = src[i]
        if quote:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return src[:start] + replacement + src[i + 1:]
        i += 1
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
    i = brace
    while i < len(src):
        ch = src[i]
        if quote:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return src[:start] + replacement + src[i + 1:]
        i += 1
    raise SystemExit(method_name + ' end not found')

# Reference palette.
s = s.replace("""      theme: ThemeData(\n        useMaterial3: true,\n        colorScheme: ColorScheme.fromSeed(\n          seedColor: const Color(0xFF5B4BDB),\n          brightness: Brightness.dark,\n        ),\n        scaffoldBackgroundColor: const Color(0xFF081120),\n        appBarTheme: const AppBarTheme(\n          elevation: 0,\n          backgroundColor: const Color(0xFF081120),\n          foregroundColor: Colors.white,\n        ),\n        cardTheme: const CardThemeData(\n          elevation: 0,\n          margin: EdgeInsets.zero,\n          surfaceTintColor: Colors.transparent,\n        ),\n      ),""", """      theme: ThemeData(\n        useMaterial3: true,\n        brightness: Brightness.light,\n        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF6D3DF5), brightness: Brightness.light),\n        scaffoldBackgroundColor: const Color(0xFFF8F7FC),\n        appBarTheme: const AppBarTheme(elevation: 0, scrolledUnderElevation: 0, backgroundColor: Color(0xFFF8F7FC), foregroundColor: Color(0xFF211D2D)),\n        inputDecorationTheme: const InputDecorationTheme(\n          filled: true, fillColor: Colors.white,\n          border: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(16)), borderSide: BorderSide(color: Color(0xFFE5E1EF))),\n          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(16)), borderSide: BorderSide(color: Color(0xFFE5E1EF))),\n          focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(16)), borderSide: BorderSide(color: Color(0xFF6D3DF5), width: 1.5)),\n        ),\n        cardTheme: const CardThemeData(elevation: 0, margin: EdgeInsets.zero, surfaceTintColor: Colors.transparent),\n      ),""", 1)

login = r'''class LoginPage extends StatefulWidget {
  const LoginPage({super.key});
  @override State<LoginPage> createState() => _LoginPageState();
}
class _LoginPageState extends State<LoginPage> {
  final email = TextEditingController();
  final password = TextEditingController();
  bool register = false;
  bool busy = false;
  String? error;
  Future<void> submit() async {
    setState(() { busy = true; error = null; });
    try {
      final auth = Supabase.instance.client.auth;
      if (register) {
        await auth.signUp(email: email.text.trim(), password: password.text);
      } else {
        await auth.signInWithPassword(email: email.text.trim(), password: password.text);
      }
    } catch (e) { if (mounted) setState(() => error = e.toString()); }
    finally { if (mounted) setState(() => busy = false); }
  }
  @override Widget build(BuildContext context) {
    return Scaffold(backgroundColor: const Color(0xFFF8F7FC), body: SafeArea(child: SingleChildScrollView(padding: const EdgeInsets.fromLTRB(24, 42, 24, 24), child: Column(children: [
      Container(width: 76, height: 76, decoration: BoxDecoration(gradient: const LinearGradient(colors: [Color(0xFF8B5CF6), Color(0xFF5B21B6)]), borderRadius: BorderRadius.circular(22)), child: const Icon(Icons.credit_card_rounded, color: Colors.white, size: 42)),
      const SizedBox(height: 14), const Text('Kart Kampanya', style: TextStyle(fontSize: 27, fontWeight: FontWeight.w900, color: Color(0xFF17142A))),
      const SizedBox(height: 5), const Text('Tüm Banka Kampanyaları Tek Uygulamada', style: TextStyle(color: Color(0xFF777187), fontSize: 13)),
      const SizedBox(height: 25),
      Container(padding: const EdgeInsets.all(4), decoration: BoxDecoration(color: const Color(0xFFEDEAF7), borderRadius: BorderRadius.circular(15)), child: Row(children: [
        Expanded(child: _tab('Giriş Yap', !register, () => setState(() { register = false; error = null; }))),
        Expanded(child: _tab('Kayıt Ol', register, () => setState(() { register = true; error = null; }))),
      ])),
      const SizedBox(height: 18),
      TextField(controller: email, keyboardType: TextInputType.emailAddress, decoration: const InputDecoration(prefixIcon: Icon(Icons.mail_outline_rounded), hintText: 'E-posta adresi')),
      const SizedBox(height: 12), TextField(controller: password, obscureText: true, decoration: const InputDecoration(prefixIcon: Icon(Icons.lock_outline_rounded), hintText: 'Şifre')),
      if (error != null) Padding(padding: const EdgeInsets.only(top: 10), child: Text(error!, style: const TextStyle(color: Color(0xFFD32F2F), fontSize: 12))),
      const SizedBox(height: 12), SizedBox(width: double.infinity, height: 50, child: FilledButton(onPressed: busy ? null : submit, style: FilledButton.styleFrom(backgroundColor: const Color(0xFF6D3DF5), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15))), child: Text(busy ? 'Bekleyin...' : (register ? 'Kayıt Ol' : 'Giriş Yap'), style: const TextStyle(fontWeight: FontWeight.w900)))),
      const SizedBox(height: 12), TextButton(onPressed: busy ? null : () => setState(() => register = !register), child: Text(register ? 'Zaten hesabım var → Giriş Yap' : 'Hesabım yok → Kayıt Ol')),
    ]))));
  }
  Widget _tab(String text, bool selected, VoidCallback onTap) => InkWell(onTap: onTap, borderRadius: BorderRadius.circular(12), child: Container(padding: const EdgeInsets.symmetric(vertical: 11), alignment: Alignment.center, decoration: BoxDecoration(color: selected ? Colors.white : Colors.transparent, borderRadius: BorderRadius.circular(12)), child: Text(text, style: TextStyle(color: selected ? const Color(0xFF5B21B6) : const Color(0xFF777187), fontWeight: FontWeight.w900))));
}
'''
s = replace_class(s, 'LoginPage', login)

shell = r'''class MainShell extends StatefulWidget {
  const MainShell({super.key});
  @override State<MainShell> createState() => _MainShellState();
}
class _MainShellState extends State<MainShell> {
  int index = 0;
  final cards = <UserCard>[];
  @override void initState() { super.initState(); loadCards(); }
  Future<void> loadCards() async {
    final uid = Supabase.instance.client.auth.currentUser!.id;
    final rows = await Supabase.instance.client.from('user_cards').select().eq('user_id', uid).order('created_at');
    if (!mounted) return;
    setState(() { cards..clear()..addAll(List<Map<String,dynamic>>.from(rows).map((m) => UserCard(id:'${m['id']}', bank:'${m['bank_name']}', card:'${m['card_name']}', network:'${m['network']}', customerType:'${m['customer_type'] ?? 'Bireysel'}', cardType:'${m['card_type'] ?? 'Kredi'}'))); });
  }
  Future<void> addCard(UserCard card) async { final uid=Supabase.instance.client.auth.currentUser!.id; await Supabase.instance.client.from('user_cards').insert({'user_id':uid,'bank_name':card.bank,'card_name':card.card,'network':card.network,'customer_type':card.customerType,'card_type':card.cardType}); await loadCards(); }
  Future<void> deleteCard(UserCard card) async { await Supabase.instance.client.from('user_cards').delete().eq('id',card.id); await loadCards(); }
  @override Widget build(BuildContext context) {
    final pages=<Widget>[CampaignsPage(cards:cards,mode:'home'),CampaignsPage(cards:cards,mode:'matched'),MyCardsPage(cards:cards,onAdd:addCard,onDelete:deleteCard),const CategoriesPage(),const ProfilePage()];
    return Scaffold(backgroundColor:const Color(0xFFF8F7FC),body:SafeArea(child:IndexedStack(index:index,children:pages)),bottomNavigationBar:NavigationBar(backgroundColor:Colors.white,indicatorColor:const Color(0xFFEAE2FF),selectedIndex:index,onDestinationSelected:(v)=>setState(()=>index=v),destinations:const[
      NavigationDestination(icon:Icon(Icons.home_outlined),selectedIcon:Icon(Icons.home_rounded),label:'Ana Sayfa'),
      NavigationDestination(icon:Icon(Icons.auto_awesome_outlined),selectedIcon:Icon(Icons.auto_awesome),label:'Kartıma Uygun'),
      NavigationDestination(icon:Icon(Icons.credit_card_outlined),selectedIcon:Icon(Icons.credit_card),label:'Bendeki Kartlar'),
      NavigationDestination(icon:Icon(Icons.grid_view_outlined),selectedIcon:Icon(Icons.grid_view_rounded),label:'Kategoriler'),
      NavigationDestination(icon:Icon(Icons.person_outline_rounded),selectedIcon:Icon(Icons.person_rounded),label:'Profil'),
    ]));
  }
}
'''
s = replace_class(s, 'MainShell', shell)

# Keep all matching/fetch logic but replace only the screen renderer.
build = r'''  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F7FC),
      body: FutureBuilder<List<Map<String,dynamic>>>(
        future: future,
        builder: (context, snapshot) {
          var rows = snapshot.data ?? <Map<String,dynamic>>[];
          if (search.text.trim().isNotEmpty) {
            final q = _norm(search.text);
            rows = rows.where((c) => _norm([c['title'],c['merchant'],c['category'],c['description'],c['campaign_text']].where((x)=>x!=null).join(' ')).contains(q)).toList();
          }
          if (category.isNotEmpty) rows = rows.where((c) => campaignSection(c) == category || '${c['category'] ?? ''}' == category).toList();
          if (showFavoritesOnly) rows = rows.where((c) => favoriteIds.contains(campaignId(c))).toList();
          if (widget.mode == 'matched' && widget.cards.isNotEmpty) rows = rows.where((c) => widget.cards.any((card)=>cardMatches(c,card))).toList();
          return RefreshIndicator(
            onRefresh: () async { setState(() { future = fetchCampaigns(); }); await future; },
            child: ListView(padding: const EdgeInsets.fromLTRB(16, 14, 16, 30), children: [
              Row(children: [
                Container(width: 40,height: 40,decoration:BoxDecoration(gradient:const LinearGradient(colors:[Color(0xFF8B5CF6),Color(0xFF5B21B6)]),borderRadius:BorderRadius.circular(12)),child:const Icon(Icons.credit_card_rounded,color:Colors.white,size:24)),
                const SizedBox(width:10),
                const Expanded(child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[Text('Kart Kampanya',style:TextStyle(fontSize:20,fontWeight:FontWeight.w900,color:Color(0xFF211D2D))),Text('Tüm Banka Kampanyaları Tek Uygulamada',style:TextStyle(fontSize:10,color:Color(0xFF777187)))])),
                IconButton(onPressed:()=>setState(()=>future=fetchCampaigns()),icon:const Icon(Icons.refresh_rounded,color:Color(0xFF4B4655))),
              ]),
              const SizedBox(height:12),
              TextField(controller:search,onChanged:(_)=>setState((){}),onSubmitted:(_)=>searchNow(),decoration:const InputDecoration(prefixIcon:Icon(Icons.search_rounded),hintText:'Kampanya, marka veya kategori ara...')),
              const SizedBox(height:11),
              SingleChildScrollView(scrollDirection:Axis.horizontal,child:Row(children:[_pill('▦','Tümü',category.isEmpty&&!showFavoritesOnly,()=>setState(()=>category='')),_pill('✧','Bana Uygun',widget.mode=='matched',()=>setState(()=>category='')),_pill('♥','Favoriler',showFavoritesOnly,()=>setState(()=>showFavoritesOnly=!showFavoritesOnly)),_pill('◷','Son Eklenen',false,()=>setState(()=>rows.sort((a,b)=>'${b['id']}'.compareTo('${a['id']}'))))])),
              if (widget.mode == 'home') ...[
                const SizedBox(height:14),
                Container(height:145,padding:const EdgeInsets.all(17),decoration:BoxDecoration(gradient:const LinearGradient(colors:[Color(0xFF5424CF),Color(0xFF8C62F7)]),borderRadius:BorderRadius.circular(23)),child:Stack(children:[const Positioned(right:10,top:2,child:Text('☀️',style:TextStyle(fontSize:28))),const Positioned(right:12,bottom:0,child:Text('🏖️',style:TextStyle(fontSize:40))),Column(crossAxisAlignment:CrossAxisAlignment.start,children:[const Text('Yaz Fırsatları\nDevam Ediyor!',style:TextStyle(color:Colors.white,fontSize:23,height:1.0,fontWeight:FontWeight.w900)),const SizedBox(height:8),const Text('Alışverişte kazancının\ntam zamanını yakala.',style:TextStyle(color:Colors.white,fontSize:11,fontWeight:FontWeight.w700)),const Spacer(),Container(padding:const EdgeInsets.symmetric(horizontal:11,vertical:6),decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(13)),child:const Text('Tüm Kampanyalar  →',style:TextStyle(color:Color(0xFF5B21B6),fontSize:10,fontWeight:FontWeight.w900)))])]),
                const SizedBox(height:16),
                const Text('Kategoriler',style:TextStyle(fontSize:18,fontWeight:FontWeight.w900,color:Color(0xFF211D2D))),
                const SizedBox(height:9),
                GridView.count(shrinkWrap:true,physics:const NeverScrollableScrollPhysics(),crossAxisCount:4,crossAxisSpacing:8,mainAxisSpacing:8,childAspectRatio:1.02,children:const[_HomeCat('⛽','Akaryakıt',0xFFFFE4E8),_HomeCat('🛒','Market',0xFFE1F8EF),_HomeCat('🍴','Restoran',0xFFFFEAD8),_HomeCat('🛍','E-Ticaret',0xFFE8E1FF),_HomeCat('📱','Elektronik',0xFFE1EEFF),_HomeCat('✈','Seyahat',0xFFFFE8D8),_HomeCat('👕','Giyim',0xFFFFE2F1),_HomeCat('⌂','Ev & Yaşam',0xFFE3F4E9)]),
                const SizedBox(height:16),
              ],
              if (snapshot.connectionState == ConnectionState.waiting) const Center(child:Padding(padding:EdgeInsets.all(40),child:CircularProgressIndicator())),
              if (snapshot.hasError) const Center(child:Padding(padding:EdgeInsets.all(30),child:Text('Kampanyalar yüklenemedi.\nAşağı çekerek tekrar dene.',textAlign:TextAlign.center))),
              if (snapshot.connectionState != ConnectionState.waiting && !snapshot.hasError && rows.isEmpty) const Center(child:Padding(padding:EdgeInsets.all(30),child:Text('Bu filtreye uygun kampanya bulunamadı.'))),
              if (snapshot.connectionState != ConnectionState.waiting && !snapshot.hasError) ...rows.map((c)=>SmartCampaignCard(campaign:c,isFavorite:favoriteIds.contains(campaignId(c)),isCompared:compareIds.contains(campaignId(c)),showAllCampaigns:showAllCampaigns,expiringSoon:isExpiringSoon(c),daysRemaining:daysLeft(c),onFavorite:()=>toggleFavorite(c),onCompare:()=>toggleCompare(c),onOpenUrl:openCampaignUrl,requiredSteps:requiredSteps(c),completedSteps:currentProgress(c),onProgressChange:(d)=>changeProgress(c,d)))
            ]),
          );
        },
      ),
    );
  }
  Widget _pill(String icon,String label,bool selected,VoidCallback onTap)=>Padding(padding:const EdgeInsets.only(right:7),child:InkWell(onTap:onTap,borderRadius:BorderRadius.circular(15),child:Container(padding:const EdgeInsets.symmetric(horizontal:15,vertical:10),decoration:BoxDecoration(color:selected?const Color(0xFF6D3DF5):const Color(0xFFEFEAF9),borderRadius:BorderRadius.circular(15)),child:Row(children:[Text(icon,style:TextStyle(color:selected?Colors.white:const Color(0xFF6D3DF5))),const SizedBox(width:6),Text(label,style:TextStyle(color:selected?Colors.white:const Color(0xFF4B4655),fontSize:11,fontWeight:FontWeight.w900))]))));
}
class _HomeCat extends StatelessWidget { final String icon,label; final int bg; const _HomeCat(this.icon,this.label,this.bg); @override Widget build(BuildContext context)=>Container(decoration:BoxDecoration(color:Color(bg),borderRadius:BorderRadius.circular(16)),child:Column(mainAxisAlignment:MainAxisAlignment.center,children:[Text(icon,style:const TextStyle(fontSize:21)),const SizedBox(height:4),Text(label,maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:9,fontWeight:FontWeight.w800,color:Color(0xFF353146)))])); }
'''
s = replace_method(s, '_CampaignsPageState', 'build', build)

smart = r'''class SmartCampaignCard extends StatelessWidget {
  final Map<String,dynamic> campaign;
  final bool isFavorite,isCompared,showAllCampaigns,expiringSoon;
  final int daysRemaining,requiredSteps,completedSteps;
  final VoidCallback onFavorite,onCompare;
  final Future<void> Function(String url) onOpenUrl;
  final ValueChanged<int> onProgressChange;
  const SmartCampaignCard({super.key,required this.campaign,required this.isFavorite,required this.isCompared,required this.showAllCampaigns,required this.expiringSoon,required this.daysRemaining,required this.onFavorite,required this.onCompare,required this.onOpenUrl,required this.requiredSteps,required this.completedSteps,required this.onProgressChange});
  @override Widget build(BuildContext context) {
    final title=decodeHtmlEntities('${campaign['title']??''}').trim();
    final merchant=decodeHtmlEntities('${campaign['merchant']??''}').trim();
    final category=decodeHtmlEntities('${campaign['category']??''}').trim();
    final cards=(campaign['_cards'] as List?)?.whereType<UserCard>().toList()??<UserCard>[];
    final reward=campaign['_calculatedReward']??campaign['_reward'];
    return Card(margin:const EdgeInsets.only(bottom:12),color:Colors.white,shape:RoundedRectangleBorder(borderRadius:BorderRadius.circular(18)),child:InkWell(borderRadius:BorderRadius.circular(18),onTap:()=>Navigator.of(context).push(MaterialPageRoute(builder:(_)=>CampaignDetailPage(campaign:campaign))),child:Padding(padding:const EdgeInsets.all(13),child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[
      Row(children:[Container(width:55,height:55,decoration:BoxDecoration(color:const Color(0xFFF0EBFF),borderRadius:BorderRadius.circular(14)),child:const Icon(Icons.local_offer_rounded,color:Color(0xFF6D3DF5),size:28)),const SizedBox(width:11),Expanded(child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[if(merchant.isNotEmpty)Text(merchant,maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:10,color:Color(0xFF777187),fontWeight:FontWeight.w800)),Text(title.isEmpty?'Kampanya':title,maxLines:3,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:15,height:1.15,color:Color(0xFF211D2D),fontWeight:FontWeight.w900))])),IconButton(onPressed:onFavorite,icon:Icon(isFavorite?Icons.favorite_rounded:Icons.favorite_border_rounded,color:isFavorite?const Color(0xFFE33F77):const Color(0xFF777187)))]),
      if(category.isNotEmpty)Padding(padding:const EdgeInsets.only(top:8),child:Container(padding:const EdgeInsets.symmetric(horizontal:8,vertical:4),decoration:BoxDecoration(color:const Color(0xFFEDE7FF),borderRadius:BorderRadius.circular(9)),child:Text(category,style:const TextStyle(fontSize:9,color:Color(0xFF5B21B6),fontWeight:FontWeight.w900)))),
      if(cards.isNotEmpty)Padding(padding:const EdgeInsets.only(top:8),child:Text('💳 ${cards.map((c)=>'${c.bank} • ${c.card} • ${c.network}').join(' | ')}',maxLines:2,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:10,fontWeight:FontWeight.w700))),
      if(reward!=null)Padding(padding:const EdgeInsets.only(top:7),child:Text('🎁 ${(reward as num).toDouble().toStringAsFixed(0)} TL avantaj',style:const TextStyle(fontWeight:FontWeight.w900,color:Color(0xFF5B21B6)))),
      if(expiringSoon)Padding(padding:const EdgeInsets.only(top:6),child:Text(daysRemaining==0?'Son gün bugün':'Son $daysRemaining gün',style:const TextStyle(fontSize:10,fontWeight:FontWeight.w800,color:Color(0xFFD33A3A)))),
      Row(children:[const Spacer(),TextButton.icon(onPressed:onCompare,icon:Icon(isCompared?Icons.check_circle_rounded:Icons.compare_arrows_rounded,size:18),label:Text(isCompared?'Seçildi':'Karşılaştır'))]),
    ]))));
  }
}
'''
s = replace_class(s, 'SmartCampaignCard', smart)

# Add a real profile tab if the base source does not already contain one.
if 'class ProfilePage extends StatelessWidget' not in s:
    marker = 'class CategoriesPage extends StatelessWidget {'
    profile = r'''class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});
  @override Widget build(BuildContext context) {
    final email=Supabase.instance.client.auth.currentUser?.email??'';
    return ListView(padding:const EdgeInsets.all(18),children:[const Text('Profil',style:TextStyle(fontSize:28,fontWeight:FontWeight.w900,color:Color(0xFF211D2D))),const SizedBox(height:18),Container(padding:const EdgeInsets.all(18),decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(18)),child:Column(children:[Container(width:70,height:70,decoration:BoxDecoration(color:const Color(0xFFE7DEFF),shape:BoxShape.circle),alignment:Alignment.center,child:const Text('K',style:TextStyle(fontSize:30,fontWeight:FontWeight.w900,color:Color(0xFF6D3DF5)))),const SizedBox(height:10),const Text('Kart Kampanya',style:TextStyle(fontSize:18,fontWeight:FontWeight.w900)),if(email.isNotEmpty)Text(email,style:const TextStyle(fontSize:11,color:Color(0xFF777187)))])),const SizedBox(height:12),ListTile(tileColor:Colors.white,shape:RoundedRectangleBorder(borderRadius:BorderRadius.circular(15)),leading:const Icon(Icons.credit_card_rounded),title:const Text('Bendeki Kartlar'),trailing:const Icon(Icons.chevron_right_rounded)),const SizedBox(height:8),ListTile(tileColor:Colors.white,shape:RoundedRectangleBorder(borderRadius:BorderRadius.circular(15)),leading:const Icon(Icons.favorite_rounded),title:const Text('Favori Kampanyalar'),trailing:const Icon(Icons.chevron_right_rounded)),const SizedBox(height:18),FilledButton.icon(onPressed:()=>Supabase.instance.client.auth.signOut(),icon:const Icon(Icons.logout_rounded),label:const Text('Çıkış Yap'))]);
  }
}

'''
    s = s.replace(marker, profile + marker, 1)

categories = r'''class CategoriesPage extends StatelessWidget {
  const CategoriesPage({super.key});
  @override Widget build(BuildContext context) {
    const data=[['▦','Tümü',0xFFEDE7FF],['⛽','Akaryakıt',0xFFFFE4E8],['🛒','Market',0xFFE1F8EF],['🍴','Restoran',0xFFFFEAD8],['🛍','E-Ticaret',0xFFE8E1FF],['👕','Giyim',0xFFFFE2F1],['📱','Elektronik',0xFFE1EEFF],['✈','Seyahat',0xFFFFE8D8],['🚗','Otomotiv',0xFFE3F0FF],['⌂','Ev & Yaşam',0xFFE3F4E9],['💊','Sağlık & Güzellik',0xFFFFE4EF],['🎬','Eğlence',0xFFE9E2FF],['📚','Eğitim',0xFFE1F4FF],['💼','Finans',0xFFE8F5E9],['•','Diğer',0xFFF0EDF5]];
    return ListView(padding:const EdgeInsets.fromLTRB(18,18,18,30),children:[const Text('Kategoriler',style:TextStyle(fontSize:28,fontWeight:FontWeight.w900,color:Color(0xFF211D2D))),const SizedBox(height:16),GridView.builder(shrinkWrap:true,physics:const NeverScrollableScrollPhysics(),itemCount:data.length,gridDelegate:const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount:3,crossAxisSpacing:10,mainAxisSpacing:10,childAspectRatio:1.05),itemBuilder:(_,i){final x=data[i];return Container(decoration:BoxDecoration(color:Color(x[2] as int),borderRadius:BorderRadius.circular(18)),child:Column(mainAxisAlignment:MainAxisAlignment.center,children:[Text(x[0] as String,style:const TextStyle(fontSize:25)),const SizedBox(height:6),Padding(padding:const EdgeInsets.symmetric(horizontal:5),child:Text(x[1] as String,maxLines:2,textAlign:TextAlign.center,style:const TextStyle(fontSize:10,fontWeight:FontWeight.w800,color:Color(0xFF353146))))]));}})]);
  }
}
'''
s = replace_class(s, 'CategoriesPage', categories)

p.write_text(s,encoding='utf-8')
print('final reference UI applied')
