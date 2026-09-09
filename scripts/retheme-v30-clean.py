from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

def replace_class(src, name, replacement):
    marker = f'class {name}'
    start = src.find(marker)
    if start < 0:
        raise SystemExit(f'{name} not found')
    brace = src.find('{', start)
    depth = 0
    for i in range(brace, len(src)):
        if src[i] == '{':
            depth += 1
        elif src[i] == '}':
            depth -= 1
            if depth == 0:
                return src[:start] + replacement + src[i + 1:]
    raise SystemExit(f'{name} end not found')

# Reference palette: white/lilac surfaces, strong purple accent, soft cards.
old_theme = """      theme: ThemeData(\n        useMaterial3: true,\n        colorScheme: ColorScheme.fromSeed(\n          seedColor: const Color(0xFF5B4BDB),\n          brightness: Brightness.dark,\n        ),\n        scaffoldBackgroundColor: const Color(0xFF081120),\n        appBarTheme: const AppBarTheme(\n          elevation: 0,\n          backgroundColor: const Color(0xFF081120),\n          foregroundColor: Colors.white,\n        ),\n        cardTheme: const CardThemeData(\n          elevation: 0,\n          margin: EdgeInsets.zero,\n          surfaceTintColor: Colors.transparent,\n        ),\n      ),"""
new_theme = """      theme: ThemeData(\n        useMaterial3: true,\n        brightness: Brightness.light,\n        colorScheme: ColorScheme.fromSeed(\n          seedColor: const Color(0xFF6D3DF5),\n          brightness: Brightness.light,\n        ),\n        scaffoldBackgroundColor: const Color(0xFFF8F7FC),\n        appBarTheme: const AppBarTheme(\n          elevation: 0,\n          scrolledUnderElevation: 0,\n          backgroundColor: Color(0xFFF8F7FC),\n          foregroundColor: Color(0xFF17142A),\n        ),\n        inputDecorationTheme: const InputDecorationTheme(\n          filled: true,\n          fillColor: Colors.white,\n          border: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(16)), borderSide: BorderSide(color: Color(0xFFE5E1EF))),\n          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(16)), borderSide: BorderSide(color: Color(0xFFE5E1EF))),\n          focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(16)), borderSide: BorderSide(color: Color(0xFF6D3DF5), width: 1.5)),\n        ),\n        cardTheme: const CardThemeData(elevation: 0, margin: EdgeInsets.zero, surfaceTintColor: Colors.transparent),\n      ),"""
if old_theme in s:
    s = s.replace(old_theme, new_theme, 1)

login = r'''class LoginPage extends StatefulWidget {
  const LoginPage({super.key});
  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final email = TextEditingController();
  final password = TextEditingController();
  bool register = false;
  bool busy = false;
  bool remember = true;
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
    } catch (e) {
      if (mounted) setState(() => error = e.toString());
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F7FC),
      body: SafeArea(child: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(24, 42, 24, 24),
        child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 430), child: Column(children: [
          Container(width: 76, height: 76, decoration: BoxDecoration(gradient: const LinearGradient(colors: [Color(0xFF8B5CF6), Color(0xFF5B21B6)]), borderRadius: BorderRadius.circular(22), boxShadow: const [BoxShadow(color: Color(0x256D3DF5), blurRadius: 18, offset: Offset(0, 8))]), child: const Icon(Icons.credit_card_rounded, color: Colors.white, size: 42)),
          const SizedBox(height: 14),
          const Text('Kart Kampanya', style: TextStyle(fontSize: 27, fontWeight: FontWeight.w900, color: Color(0xFF17142A))),
          const SizedBox(height: 5),
          const Text('Tek Uygulamada, Tüm Fırsatlar', style: TextStyle(color: Color(0xFF777187), fontSize: 14, fontWeight: FontWeight.w600)),
          const SizedBox(height: 26),
          Container(padding: const EdgeInsets.all(4), decoration: BoxDecoration(color: const Color(0xFFEDEAF7), borderRadius: BorderRadius.circular(15)), child: Row(children: [
            Expanded(child: _tab('Giriş Yap', !register, () => setState(() { register = false; error = null; }))),
            Expanded(child: _tab('Kayıt Ol', register, () => setState(() { register = true; error = null; }))),
          ])),
          const SizedBox(height: 18),
          TextField(controller: email, keyboardType: TextInputType.emailAddress, decoration: const InputDecoration(prefixIcon: Icon(Icons.mail_outline_rounded), hintText: 'E-posta adresi')),
          const SizedBox(height: 12),
          TextField(controller: password, obscureText: true, decoration: const InputDecoration(prefixIcon: Icon(Icons.lock_outline_rounded), hintText: 'Şifre', suffixIcon: Icon(Icons.visibility_outlined))),
          if (error != null) Padding(padding: const EdgeInsets.only(top: 10), child: Text(error!, style: const TextStyle(color: Color(0xFFD32F2F), fontSize: 12))),
          const SizedBox(height: 10),
          Row(children: [Checkbox(value: remember, onChanged: (v) => setState(() => remember = v ?? true), activeColor: const Color(0xFF6D3DF5)), const Text('Beni hatırla', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600)), const Spacer(), TextButton(onPressed: () {}, child: const Text('Şifremi Unuttum?', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800)))]),
          const SizedBox(height: 4),
          SizedBox(width: double.infinity, height: 50, child: FilledButton(onPressed: busy ? null : submit, style: FilledButton.styleFrom(backgroundColor: const Color(0xFF6D3DF5), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15))), child: Text(busy ? 'Bekleyin...' : (register ? 'Kayıt Ol' : 'Giriş Yap'), style: const TextStyle(fontWeight: FontWeight.w900)))),
          const SizedBox(height: 12),
          const Text('veya', style: TextStyle(color: Color(0xFF938DA1))),
          const SizedBox(height: 10),
          SizedBox(width: double.infinity, height: 48, child: OutlinedButton(onPressed: () {}, style: OutlinedButton.styleFrom(side: const BorderSide(color: Color(0xFFE2DEEA)), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15))), child: const Text('G  Google ile Giriş Yap', style: TextStyle(color: Color(0xFF332F40), fontWeight: FontWeight.w800)))),
          const SizedBox(height: 28),
          const Text('Kampanyaları kaçırma, avantajını yaşa! ♡', style: TextStyle(color: Color(0xFF888193), fontSize: 12, fontWeight: FontWeight.w600)),
        ])),
      )),
    );
  }

  Widget _tab(String text, bool selected, VoidCallback onTap) => InkWell(onTap: onTap, borderRadius: BorderRadius.circular(12), child: Container(padding: const EdgeInsets.symmetric(vertical: 11), decoration: BoxDecoration(color: selected ? Colors.white : Colors.transparent, borderRadius: BorderRadius.circular(12), boxShadow: selected ? const [BoxShadow(color: Color(0x10000000), blurRadius: 7)] : null), alignment: Alignment.center, child: Text(text, style: TextStyle(color: selected ? const Color(0xFF5B21B6) : const Color(0xFF777187), fontWeight: FontWeight.w900, fontSize: 13))));
}
'''
s = replace_class(s, 'LoginPage', login)

shell = r'''class MainShell extends StatefulWidget {
  const MainShell({super.key});
  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int index = 0;
  final cards = <UserCard>[];
  @override
  void initState() { super.initState(); loadCards(); }
  Future<void> loadCards() async {
    final uid = Supabase.instance.client.auth.currentUser!.id;
    final rows = await Supabase.instance.client.from('user_cards').select().eq('user_id', uid).order('created_at');
    if (!mounted) return;
    setState(() { cards..clear()..addAll(List<Map<String,dynamic>>.from(rows).map((m)=>UserCard(id:'${m['id']}', bank:'${m['bank_name']}', card:'${m['card_name']}', network:'${m['network']}', customerType:'${m['customer_type'] ?? 'Bireysel'}', cardType:'${m['card_type'] ?? 'Kredi'}'))); });
  }
  Future<void> addCard(UserCard card) async { final uid=Supabase.instance.client.auth.currentUser!.id; await Supabase.instance.client.from('user_cards').insert({'user_id':uid,'bank_name':card.bank,'card_name':card.card,'network':card.network,'customer_type':card.customerType,'card_type':card.cardType}); await loadCards(); }
  Future<void> deleteCard(UserCard card) async { await Supabase.instance.client.from('user_cards').delete().eq('id', card.id); await loadCards(); }
  @override
  Widget build(BuildContext context) {
    final pages=<Widget>[CampaignsPage(cards:cards,mode:'home'),CampaignsPage(cards:cards,mode:'matched'),MyCardsPage(cards:cards,onAdd:addCard,onDelete:deleteCard),const CategoriesPage(),const ProfilePage()];
    return Scaffold(backgroundColor:const Color(0xFFF8F7FC),body:SafeArea(child:IndexedStack(index:index,children:pages)),bottomNavigationBar:NavigationBar(backgroundColor:Colors.white,indicatorColor:const Color(0xFFEAE2FF),height:70,selectedIndex:index,onDestinationSelected:(v)=>setState(()=>index=v),destinations:const[
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

# Light reference campaign card.
smart = r'''class SmartCampaignCard extends StatelessWidget {
  final Map<String,dynamic> campaign;
  final bool isFavorite,isCompared,showAllCampaigns,expiringSoon;
  final int daysRemaining,requiredSteps,completedSteps;
  final VoidCallback onFavorite,onCompare;
  final Future<void> Function(String url) onOpenUrl;
  final ValueChanged<int> onProgressChange;
  const SmartCampaignCard({super.key,required this.campaign,required this.isFavorite,required this.isCompared,required this.showAllCampaigns,required this.expiringSoon,required this.daysRemaining,required this.onFavorite,required this.onCompare,required this.onOpenUrl,required this.requiredSteps,required this.completedSteps,required this.onProgressChange});
  String t(dynamic v)=>v==null?'':'$v'.trim();
  String logoUrl(){ for(final k in ['logo_url','image_url','merchant_logo','brand_logo']){final v=t(campaign[k]);if(v.isNotEmpty)return v;} return ''; }
  @override
  Widget build(BuildContext context){
    final title=t(campaign['title']).isEmpty?'Kampanya':t(campaign['title']);
    final merchant=t(campaign['merchant']);
    final cat=t(campaign['category']).isEmpty?campaignSection(campaign):t(campaign['category']);
    final logo=logoUrl();
    return InkWell(borderRadius:BorderRadius.circular(18),onTap:()=>Navigator.of(context).push(MaterialPageRoute(builder:(_)=>CampaignDetailPage(campaign:campaign))),child:Container(margin:const EdgeInsets.only(bottom:12),padding:const EdgeInsets.fromLTRB(13,13,10,13),decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(18),border:Border.all(color:const Color(0xFFE7E3EF)),boxShadow:const[BoxShadow(color:Color(0x0A000000),blurRadius:10,offset:Offset(0,3))]),child:Row(crossAxisAlignment:CrossAxisAlignment.start,children:[
      Container(width:58,height:58,decoration:BoxDecoration(color:const Color(0xFFF3F0FA),borderRadius:BorderRadius.circular(13)),child:logo.isNotEmpty?ClipRRect(borderRadius:BorderRadius.circular(13),child:Image.network(logo,fit:BoxFit.contain,errorBuilder:(_,__,___)=>const Icon(Icons.local_offer_rounded,color:Color(0xFF6D3DF5),size:27))):const Icon(Icons.local_offer_rounded,color:Color(0xFF6D3DF5),size:27)),
      const SizedBox(width:11),Expanded(child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[if(merchant.isNotEmpty)Text(merchant,maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:10,color:Color(0xFF777187),fontWeight:FontWeight.w800)),const SizedBox(height:2),Text(title,maxLines:3,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:14,height:1.15,color:Color(0xFF211D2D),fontWeight:FontWeight.w900)),const SizedBox(height:7),Row(children:[Container(padding:const EdgeInsets.symmetric(horizontal:8,vertical:4),decoration:BoxDecoration(color:const Color(0xFFEDE7FF),borderRadius:BorderRadius.circular(9)),child:Text(cat,style:const TextStyle(fontSize:9,color:Color(0xFF5B21B6),fontWeight:FontWeight.w900))),if(expiringSoon)...[const SizedBox(width:6),Container(padding:const EdgeInsets.symmetric(horizontal:7,vertical:4),decoration:BoxDecoration(color:const Color(0xFFFFE7E7),borderRadius:BorderRadius.circular(9)),child:Text('Son $daysRemaining Gün',style:const TextStyle(fontSize:8,color:Color(0xFFD33A3A),fontWeight:FontWeight.w900)))]])),IconButton(onPressed:onFavorite,icon:Icon(isFavorite?Icons.favorite_rounded:Icons.favorite_border_rounded,color:isFavorite?const Color(0xFFE33F77):const Color(0xFF777187),size:22)),
    ]))); }
}
'''
s = replace_class(s, 'SmartCampaignCard', smart)

# Reference-style campaign page. Keep existing fetch/matching/state methods intact.
state = s.find('class _CampaignsPageState extends State<CampaignsPage> {')
start = s.find('  @override\n  Widget build(BuildContext context) {', state)
if start < 0: raise SystemExit('Campaign build not found')
brace=s.find('{',start);depth=0
for i in range(brace,len(s)):
    if s[i]=='{': depth+=1
    elif s[i]=='}':
        depth-=1
        if depth==0: end=i+1; break
else: raise SystemExit('Campaign build end not found')

build = r'''  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<Map<String,dynamic>>>(future:future,builder:(context,snapshot){
      var campaigns=snapshot.data ?? <Map<String,dynamic>>[];
      if(search.text.trim().isNotEmpty){final q=_norm(search.text);campaigns=campaigns.where((c)=>_norm([c['title'],c['merchant'],c['category'],c['description'],c['campaign_text']].where((x)=>x!=null).join(' ')).contains(q)).toList();}
      if(category.isNotEmpty)campaigns=campaigns.where((c)=>campaignSection(c)==category||'${c['category']??''}'==category).toList();
      if(showFavoritesOnly)campaigns=campaigns.where((c)=>favoriteIds.contains(campaignId(c))).toList();
      final groups=<String,List<Map<String,dynamic>>>{};for(final c in campaigns){groups.putIfAbsent(campaignSection(c),()=>[]).add(c);}
      return RefreshIndicator(onRefresh:()async{setState(()=>future=fetchCampaigns());await future;},child:CustomScrollView(slivers:[
        SliverPadding(padding:const EdgeInsets.fromLTRB(16,14,16,0),sliver:SliverToBoxAdapter(child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[
          Row(children:[Container(width:38,height:38,decoration:BoxDecoration(gradient:const LinearGradient(colors:[Color(0xFF8B5CF6),Color(0xFF5B21B6)]),borderRadius:BorderRadius.circular(11)),child:const Icon(Icons.credit_card_rounded,color:Colors.white,size:23)),const SizedBox(width:9),const Expanded(child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[Text('Kart Kampanya',style:TextStyle(fontSize:19,fontWeight:FontWeight.w900,color:Color(0xFF17142A))),Text('Tüm Banka Kampanyaları Tek Uygulamada',style:TextStyle(fontSize:10,color:Color(0xFF777187),fontWeight:FontWeight.w600))])),IconButton(onPressed:()=>setState(()=>future=fetchCampaigns()),icon:const Icon(Icons.notifications_none_rounded,color:Color(0xFF383344))),]),
          const SizedBox(height:12),TextField(controller:search,onChanged:(_)=>setState((){}),decoration:const InputDecoration(prefixIcon:Icon(Icons.search_rounded,color:Color(0xFF777187)),hintText:'Kampanya ara...')),
          const SizedBox(height:13),
          SizedBox(height:54,child:SingleChildScrollView(scrollDirection:Axis.horizontal,child:Row(children:[_filter('▦','Tümü',!showFavoritesOnly&&category.isEmpty,(){setState((){category='';showFavoritesOnly=false;});}),_filter('✧','Bana Uygun',widget.mode=='matched',(){setState(()=>category='');}),_filter('♥','Favoriler',showFavoritesOnly,(){setState(()=>showFavoritesOnly=!showFavoritesOnly);}),_filter('◷','Son Eklenen',false,(){}),]))),
          if(widget.mode=='home')...[
            const SizedBox(height:14),
            Container(height:138,padding:const EdgeInsets.fromLTRB(16,15,14,14),decoration:BoxDecoration(gradient:const LinearGradient(colors:[Color(0xFF4D22C8),Color(0xFF8B5CF6),Color(0xFFD6A7FF)]),borderRadius:BorderRadius.circular(22)),child:Stack(children:[const Positioned(right:12,top:4,child:Text('☀️',style:TextStyle(fontSize:28))),const Positioned(right:18,bottom:0,child:Text('🏖️',style:TextStyle(fontSize:43))),Column(crossAxisAlignment:CrossAxisAlignment.start,children:[const Text('Yaz Fırsatları\nDevam Ediyor!',style:TextStyle(color:Colors.white,fontSize:22,height:1.0,fontWeight:FontWeight.w900)),const SizedBox(height:7),const Text('Alışverişte kazancının\ntam zamanını yakala.',style:TextStyle(color:Colors.white,fontSize:11,fontWeight:FontWeight.w700)),const Spacer(),Container(padding:const EdgeInsets.symmetric(horizontal:11,vertical:6),decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(13)),child:const Text('Tüm Kampanyalar  →',style:TextStyle(color:Color(0xFF5B21B6),fontSize:10,fontWeight:FontWeight.w900)))])]),
            const SizedBox(height:16),
          ],
          if(widget.mode=='home')const Text('Kategoriler',style:TextStyle(fontSize:18,fontWeight:FontWeight.w900,color:Color(0xFF211D2D))),
          if(widget.mode=='home')const SizedBox(height:9),
          if(widget.mode=='home')SizedBox(height:96,child:GridView.count(crossAxisCount:4,crossAxisSpacing:8,mainAxisSpacing:8,childAspectRatio:1.0,physics:const NeverScrollableScrollPhysics(),children:const[
            _HomeCat('⛽','Akaryakıt',0xFFFFE4E8),_HomeCat('🛒','Market',0xFFE1F8EF),_HomeCat('🍴','Restoran',0xFFFFEAD8),_HomeCat('🛍','E-Ticaret',0xFFE8E1FF),
            _HomeCat('📱','Elektronik',0xFFE1EEFF),_HomeCat('✈️','Seyahat',0xFFFFE8D8),_HomeCat('👕','Giyim',0xFFFFE2F1),_HomeCat('⌂','Ev & Yaşam',0xFFE3F4E9),
          ]),
          const SizedBox(height:14),
        ]))),
        if(snapshot.connectionState==ConnectionState.waiting)const SliverFillRemaining(hasScrollBody:false,child:Center(child:CircularProgressIndicator()))
        else if(snapshot.hasError)SliverFillRemaining(hasScrollBody:false,child:Center(child:Text('Kampanyalar yüklenemedi.\nAşağı çekerek tekrar dene.',textAlign:TextAlign.center,style:TextStyle(color:Color(0xFF777187)))))
        else if(groups.isEmpty)const SliverFillRemaining(hasScrollBody:false,child:Center(child:Text('Bu filtreye uygun kampanya bulunamadı.',style:TextStyle(color:Color(0xFF777187)))))
        else ...groups.entries.map((e)=>SliverPadding(padding:const EdgeInsets.fromLTRB(16,0,16,4),sliver:SliverToBoxAdapter(child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[Row(children:[Expanded(child:Text('${emoji(e.key)}  ${e.key}',style:const TextStyle(fontSize:19,fontWeight:FontWeight.w900,color:Color(0xFF211D2D)))),Text('${e.value.length} kampanya',style:const TextStyle(fontSize:11,color:Color(0xFF777187),fontWeight:FontWeight.w700))]),const SizedBox(height:8),...e.value.map((c)=>SmartCampaignCard(campaign:c,isFavorite:favoriteIds.contains(campaignId(c)),isCompared:compareIds.contains(campaignId(c)),showAllCampaigns:showAllCampaigns,expiringSoon:isExpiringSoon(c),daysRemaining:daysLeft(c),onFavorite:()=>toggleFavorite(c),onCompare:()=>toggleCompare(c),onOpenUrl:openCampaignUrl,requiredSteps:requiredSteps(c),completedSteps:campaignProgress[campaignId(c)]??0,onProgressChange:(v)=>setState(()=>campaignProgress[campaignId(c)]=v))).toList()])))
      ]));
    });
  }

  Widget _filter(String icon,String label,bool selected,VoidCallback onTap)=>Padding(padding:const EdgeInsets.only(right:7),child:InkWell(onTap:onTap,borderRadius:BorderRadius.circular(15),child:Container(width:105,decoration:BoxDecoration(color:selected?const Color(0xFF6D3DF5):const Color(0xFFF0EEF5),borderRadius:BorderRadius.circular(15)),child:Row(mainAxisAlignment:MainAxisAlignment.center,children:[Text(icon,style:TextStyle(color:selected?Colors.white:const Color(0xFF6D3DF5),fontSize:17)),const SizedBox(width:6),Text(label,style:TextStyle(color:selected?Colors.white:const Color(0xFF4B4655),fontSize:11,fontWeight:FontWeight.w900))]))));
}

class _HomeCat extends StatelessWidget {
  final String icon,label; final int bg;
  const _HomeCat(this.icon,this.label,this.bg);
  @override Widget build(BuildContext context)=>Container(decoration:BoxDecoration(color:Color(bg),borderRadius:BorderRadius.circular(16)),child:Column(mainAxisAlignment:MainAxisAlignment.center,children:[Text(icon,style:const TextStyle(fontSize:21)),const SizedBox(height:4),Text(label,maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:9,color:Color(0xFF353146),fontWeight:FontWeight.w800))]));
}
'''
s = s[:start] + build + s[end:]

mycards = r'''class MyCardsPage extends StatefulWidget {
  final List<UserCard> cards;
  final Future<void> Function(UserCard) onAdd;
  final Future<void> Function(UserCard) onDelete;
  const MyCardsPage({super.key,required this.cards,required this.onAdd,required this.onDelete});
  @override State<MyCardsPage> createState()=>_MyCardsPageState();
}
class _MyCardsPageState extends State<MyCardsPage>{
  String bank='Garanti BBVA',card='Bonus',network='Visa',customer='Bireysel',type='Kredi';
  @override Widget build(BuildContext context)=>Scaffold(backgroundColor:const Color(0xFFF8F7FC),appBar:AppBar(title:const Text('Bendeki Kartlar',style:TextStyle(fontSize:23,fontWeight:FontWeight.w900)),actions:[IconButton(onPressed:showAdd,icon:const Icon(Icons.add_circle_rounded,color:Color(0xFF6D3DF5),size:30))]),body:ListView(padding:const EdgeInsets.fromLTRB(16,8,16,28),children:[
    Container(padding:const EdgeInsets.all(15),decoration:BoxDecoration(gradient:const LinearGradient(colors:[Color(0xFF6D3DF5),Color(0xFF9B7BFF)]),borderRadius:BorderRadius.circular(20)),child:const Row(children:[Icon(Icons.credit_card_rounded,color:Colors.white,size:30),SizedBox(width:11),Expanded(child:Text('Kartlarını ekle, sana uygun\nkampanyaları kaçırma.',style:TextStyle(color:Colors.white,fontSize:15,fontWeight:FontWeight.w800)))])),const SizedBox(height:16),
    if(widget.cards.isEmpty)const Padding(padding:EdgeInsets.symmetric(vertical:50),child:Center(child:Text('Henüz kart eklemedin.',style:TextStyle(color:Color(0xFF777187),fontWeight:FontWeight.w700))))
    else ...widget.cards.map((c)=>Container(margin:const EdgeInsets.only(bottom:10),padding:const EdgeInsets.all(13),decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(17),border:Border.all(color:const Color(0xFFE5E1EF))),child:Row(children:[Container(width:48,height:48,decoration:BoxDecoration(color:const Color(0xFFF0EAFF),borderRadius:BorderRadius.circular(12)),child:const Icon(Icons.credit_card_rounded,color:Color(0xFF6D3DF5))),const SizedBox(width:11),Expanded(child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[Text(c.bank,style:const TextStyle(fontSize:11,color:Color(0xFF777187),fontWeight:FontWeight.w800)),Text(c.card,style:const TextStyle(fontSize:15,color:Color(0xFF211D2D),fontWeight:FontWeight.w900)),Text('${c.cardType} • ${c.customerType}',style:const TextStyle(fontSize:10,color:Color(0xFF777187)))])),Container(padding:const EdgeInsets.symmetric(horizontal:9,vertical:6),decoration:BoxDecoration(color:const Color(0xFFF2F1F6),borderRadius:BorderRadius.circular(10)),child:Text(c.network,style:const TextStyle(fontSize:10,fontWeight:FontWeight.w900,color:Color(0xFF393443)))),IconButton(onPressed:()=>widget.onDelete(c),icon:const Icon(Icons.more_vert_rounded,color:Color(0xFF777187)))])))
  ]);
  Future<void> showAdd()async{await showDialog(context:context,builder:(_)=>AlertDialog(title:const Text('Kart Ekle',style:TextStyle(fontWeight:FontWeight.w900)),content:SingleChildScrollView(child:Column(mainAxisSize:MainAxisSize.min,children:[DropdownButtonFormField<String>(value:bank,decoration:const InputDecoration(labelText:'Banka'),items:const['Garanti BBVA','Yapı Kredi','İş Bankası','Akbank','Ziraat Bankası','VakıfBank','QNB','TEB','DenizBank','ING','HSBC'].map((x)=>DropdownMenuItem(value:x,child:Text(x))).toList(),onChanged:(v)=>bank=v??bank),DropdownButtonFormField<String>(value:card,decoration:const InputDecoration(labelText:'Kart'),items:const['Bonus','World','Maximum','Axess','Bankkart','Paraf','CardFinans','Wings','Free'].map((x)=>DropdownMenuItem(value:x,child:Text(x))).toList(),onChanged:(v)=>card=v??card),DropdownButtonFormField<String>(value:network,decoration:const InputDecoration(labelText:'Kart ağı'),items:const['Visa','Mastercard','Troy'].map((x)=>DropdownMenuItem(value:x,child:Text(x))).toList(),onChanged:(v)=>network=v??network)])),actions:[TextButton(onPressed:()=>Navigator.pop(context),child:const Text('Vazgeç')),FilledButton(onPressed:()async{await widget.onAdd(UserCard(id:'',bank:bank,card:card,network:network,customerType:customer,cardType:type));if(mounted)Navigator.pop(context);},child:const Text('Ekle'))]));}
}
'''
s = replace_class(s, 'MyCardsPage', mycards)

categories = r'''class CategoriesPage extends StatelessWidget {
  const CategoriesPage({super.key});
  static const data=<List<Object>>[
    ['▦','Tümü',0xFFE9DEFF],['⛽','Akaryakıt',0xFFFFE4E8],['🛒','Market',0xFFE1F8EF],['🍴','Restoran',0xFFFFEAD8],['🛍','E-Ticaret',0xFFE8E1FF],['👕','Giyim',0xFFFFE2F1],['📱','Elektronik',0xFFE1EEFF],['✈','Seyahat',0xFFFFE8D8],['🚗','Otomotiv',0xFFE1F5F4],['⌂','Ev & Yaşam',0xFFE3F4E9],['✚','Sağlık & Güzellik',0xFFE7F7EA],['🎬','Eğlence',0xFFFFE0EC],['🎓','Eğitim',0xFFFFE5F0],['▥','Finans',0xFFE1EEFF],['••','Diğer',0xFFE8EAF4]
  ];
  @override Widget build(BuildContext context)=>Scaffold(backgroundColor:const Color(0xFFF8F7FC),appBar:AppBar(title:const Text('Kategoriler',style:TextStyle(fontSize:23,fontWeight:FontWeight.w900)),actions:[IconButton(onPressed:(){},icon:const Icon(Icons.search_rounded))]),body:GridView.builder(padding:const EdgeInsets.fromLTRB(16,8,16,28),itemCount:data.length,gridDelegate:const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount:3,crossAxisSpacing:10,mainAxisSpacing:10,childAspectRatio:.98),itemBuilder:(_,i){final x=data[i];return Container(decoration:BoxDecoration(color:Color(x[2] as int),borderRadius:BorderRadius.circular(20)),child:Column(mainAxisAlignment:MainAxisAlignment.center,children:[Text(x[0] as String,style:const TextStyle(fontSize:28)),const SizedBox(height:7),Text(x[1] as String,textAlign:TextAlign.center,style:const TextStyle(fontSize:10,color:Color(0xFF302D40),fontWeight:FontWeight.w900))]));}));
}
'''
s = replace_class(s, 'CategoriesPage', categories)

profile = r'''class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});
  @override Widget build(BuildContext context){final u=Supabase.instance.client.auth.currentUser;final email=u?.email??'';return Scaffold(backgroundColor:const Color(0xFFF8F7FC),appBar:AppBar(title:const Text('Profil',style:TextStyle(fontSize:23,fontWeight:FontWeight.w900)),actions:[IconButton(onPressed:(){},icon:const Icon(Icons.settings_outlined))]),body:ListView(padding:const EdgeInsets.all(18),children:[Center(child:Container(width:76,height:76,decoration:BoxDecoration(color:const Color(0xFFE7DEFF),shape:BoxShape.circle),alignment:Alignment.center,child:const Text('H',style:TextStyle(fontSize:32,color:Color(0xFF6D3DF5),fontWeight:FontWeight.w900)))),const SizedBox(height:9),const Center(child:Text('Kart Kampanya Kullanıcısı',style:TextStyle(fontSize:18,fontWeight:FontWeight.w900,color:Color(0xFF211D2D)))),Center(child:Text(email,style:const TextStyle(fontSize:11,color:Color(0xFF777187))),),const SizedBox(height:22),...['Bendeki Kartlar','Favori Kampanyalar','Bildirimler','Ayarlar','Yardım & Destek'].map((x)=>Container(margin:const EdgeInsets.only(bottom:9),decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(15),border:Border.all(color:const Color(0xFFE5E1EF))),child:ListTile(title:Text(x,style:const TextStyle(fontWeight:FontWeight.w700)),trailing:const Icon(Icons.chevron_right_rounded,color:Color(0xFF8A8394))))),Container(decoration:BoxDecoration(color:const Color(0xFFFFEEEE),borderRadius:BorderRadius.circular(15)),child:ListTile(onTap:()=>Supabase.instance.client.auth.signOut(),leading:const Icon(Icons.logout_rounded,color:Color(0xFFD33A3A)),title:const Text('Çıkış Yap',style:TextStyle(color:Color(0xFFD33A3A),fontWeight:FontWeight.w800))))]);}
}
'''
s = replace_class(s, 'ProfilePage', profile) if 'class ProfilePage' in s else s + '\n' + profile

# The generated shell expects ProfilePage; ensure no stale dark-only background survives in common widgets.
s = s.replace('const Color(0xFF081120)', 'const Color(0xFFF8F7FC)')
s = s.replace('brightness: Brightness.dark', 'brightness: Brightness.light')

p.write_text(s, encoding='utf-8')
print('v30 clean reference UI applied')
