from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

def replace_class(src, name, replacement):
    start = src.find(f'class {name}')
    if start < 0: raise SystemExit(f'{name} not found')
    brace = src.find('{', start)
    depth = 0
    for i in range(brace, len(src)):
        if src[i] == '{': depth += 1
        elif src[i] == '}':
            depth -= 1
            if depth == 0: return src[:start] + replacement + src[i+1:]
    raise SystemExit(f'{name} end not found')

logo = r'''class _CatalogLogo extends StatelessWidget {
  final String url;
  final double size;
  const _CatalogLogo(this.url, {this.size = 42});
  String get fallback {
    final u = url.toLowerCase();
    const m = {'axess':'axess','akbank':'AKBANK','garanti':'Garanti BBVA','vakif':'VakıfBank','qnb':'QNB','teb':'TEB','hsbc':'HSBC','ispark':'İSPARK','migros':'MİGROS','mastercard':'mastercard','visa':'VISA','troy':'troy'};
    for (final e in m.entries) { if (u.contains(e.key)) return e.value; }
    return '';
  }
  @override
  Widget build(BuildContext context) {
    final label = fallback;
    return Container(
      width: size * 2.45, height: size,
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(10), border: Border.all(color: const Color(0xFFE1E5EC))),
      alignment: Alignment.center,
      child: Image.network(url, fit: BoxFit.contain, filterQuality: FilterQuality.high,
        errorBuilder: (_, __, ___) => label.isEmpty
          ? const Icon(Icons.credit_card_rounded, color: Color(0xFF667085), size: 22)
          : FittedBox(child: Text(label, maxLines: 1, style: const TextStyle(color: Color(0xFF172033), fontWeight: FontWeight.w900, fontSize: 17))),
    );
  }
}
'''
s = replace_class(s, '_CatalogLogo', logo)

smart = r'''class SmartCampaignCard extends StatelessWidget {
  final Map<String, dynamic> campaign;
  final bool isFavorite, isCompared, showAllCampaigns, expiringSoon;
  final int daysRemaining, requiredSteps, completedSteps;
  final VoidCallback onFavorite, onCompare;
  final Future<void> Function(String url) onOpenUrl;
  final ValueChanged<int> onProgressChange;
  const SmartCampaignCard({super.key, required this.campaign, required this.isFavorite, required this.isCompared, required this.showAllCampaigns, required this.expiringSoon, required this.daysRemaining, required this.onFavorite, required this.onCompare, required this.onOpenUrl, required this.requiredSteps, required this.completedSteps, required this.onProgressChange});

  String t(dynamic v) => v == null ? '' : '$v'.trim();
  String merchantDomain(String v) {
    final m = _norm(v);
    const d = {'ispark':'ispark.istanbul','migros':'migros.com.tr','carrefour':'carrefoursa.com','trendyol':'trendyol.com','hepsiburada':'hepsiburada.com','amazon':'amazon.com.tr','a101':'a101.com.tr','bim':'bim.com.tr','sok':'sokmarket.com.tr','opet':'opet.com.tr','shell':'shell.com.tr','petrol ofisi':'petrolofisi.com.tr','mediamarkt':'mediamarkt.com.tr','teknosa':'teknosa.com','vatan':'vatanbilgisayar.com','boyner':'boyner.com.tr','mavi':'mavi.com','ikea':'ikea.com.tr','thy':'turkishairlines.com','pegasus':'flypgs.com'};
    for (final e in d.entries) { if (m.contains(e.key)) return e.value; }
    return '';
  }
  String brandDomain(String v) {
    final m = _norm(v);
    const d = {'akbank':'akbank.com','axess':'axess.com.tr','garanti':'garantibbva.com.tr','bonus':'bonus.com.tr','vakifbank':'vakifbank.com.tr','world':'worldcard.com.tr','yapi kredi':'worldcard.com.tr','qnb':'qnb.com.tr','cardfinans':'cardfinans.com.tr','teb':'teb.com.tr','cepteteb':'teb.com.tr','hsbc':'hsbc.com.tr','isbank':'isbank.com.tr','maximum':'maximum.com.tr','ziraat':'ziraatbank.com.tr','denizbank':'denizbank.com','enpara':'enpara.com','kuveytturk':'kuveytturk.com.tr','ing':'ing.com.tr'};
    for (final e in d.entries) { if (m.contains(e.key)) return e.value; }
    return '';
  }
  String logo(String domain) => domain.isEmpty ? '' : 'https://cdn.brandfetch.io/$domain/w/600/h/180/logo';

  @override
  Widget build(BuildContext context) {
    final merchant = t(campaign['merchant']);
    final title = t(campaign['title']).isEmpty ? 'Kampanya' : t(campaign['title']);
    final cat = t(campaign['category']).isEmpty ? campaignSection(campaign) : t(campaign['category']);
    final cards = (campaign['_cards'] as List?)?.whereType<UserCard>().toList() ?? <UserCard>[];
    final brands = <String>[];
    for (final c in cards) { for (final x in [c.bank,c.card,c.network]) { if (x.trim().isNotEmpty && !brands.contains(x)) brands.add(x); } }
    final md = merchantDomain(merchant);
    final benefit = t(campaign['benefit']);
    final minSpend = t(campaign['min_spend'] ?? campaign['minimum_spend']);
    return InkWell(
      borderRadius: BorderRadius.circular(24),
      onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => CampaignDetailPage(campaign: campaign))),
      child: Container(
        margin: const EdgeInsets.only(bottom: 16), padding: const EdgeInsets.fromLTRB(14,14,14,16),
        decoration: BoxDecoration(color: const Color(0xFF121A2A), borderRadius: BorderRadius.circular(24), border: Border.all(color: const Color(0xFF34445E), width: 1.2)),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            if (md.isNotEmpty) _CatalogLogo(logo(md), size: 54) else Container(width: 132,height:54,alignment:Alignment.center,decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(10)),child:Text(merchant.isEmpty?'KAMPANYA':merchant,maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(color:Color(0xFF172033),fontWeight:FontWeight.w900))),
            const SizedBox(width: 12), Expanded(child: Column(crossAxisAlignment:CrossAxisAlignment.start,children:[Text(title,maxLines:3,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:18,height:1.12,fontWeight:FontWeight.w800,color:Colors.white)),if(merchant.isNotEmpty) ...[const SizedBox(height:5),Text(merchant,maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:13,color:Color(0xFFB8C2D8),fontWeight:FontWeight.w600))]])),
            IconButton(onPressed:onFavorite,icon:Icon(isFavorite?Icons.star_rounded:Icons.star_border_rounded,color:isFavorite?const Color(0xFFC5B5FF):Colors.white70,size:28)),
            IconButton(onPressed:onCompare,icon:Icon(Icons.compare_arrows_rounded,color:isCompared?const Color(0xFFC5B5FF):Colors.white70,size:27)),
          ]),
          if (brands.isNotEmpty) ...[const SizedBox(height:12),Wrap(spacing:7,runSpacing:7,children:brands.take(5).map((b){final d=brandDomain(b);return d.isEmpty?Container(padding:const EdgeInsets.symmetric(horizontal:10,vertical:7),decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(9)),child:Text(b,style:const TextStyle(color:Color(0xFF172033),fontWeight:FontWeight.w800,fontSize:12))):_CatalogLogo(logo(d),size:34);}).toList())],
          if (benefit.isNotEmpty) ...[const SizedBox(height:12),Text('💰  Tahmini avantaj: $benefit',maxLines:2,overflow:TextOverflow.ellipsis,style:const TextStyle(color:Color(0xFFE8ECF5),fontSize:14,fontWeight:FontWeight.w600))],
          if (minSpend.isNotEmpty) ...[const SizedBox(height:6),Text('💳  Minimum harcama: $minSpend',maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(color:Color(0xFFE8ECF5),fontSize:14,fontWeight:FontWeight.w600))],
          const SizedBox(height:12),Row(children:[Container(padding:const EdgeInsets.symmetric(horizontal:12,vertical:7),decoration:BoxDecoration(color:const Color(0xFF5D43E7).withOpacity(.25),borderRadius:BorderRadius.circular(18)),child:Text(cat,style:const TextStyle(color:Color(0xFFD5CCFF),fontWeight:FontWeight.w700))),const Spacer(),const Icon(Icons.arrow_forward_rounded,color:Colors.white70,size:24)]),
        ]),
      ),
    );
  }
}
'''
s = replace_class(s, 'SmartCampaignCard', smart)

# Replace only CampaignsPage build, preserving all fetch/matching/favorite methods.
state = s.find('class _CampaignsPageState extends State<CampaignsPage> {')
start = s.find('  @override\n  Widget build(BuildContext context) {', state)
if start < 0: raise SystemExit('Campaign build not found')
brace = s.find('{', start); depth = 0
for i in range(brace, len(s)):
    if s[i]=='{': depth += 1
    elif s[i]=='}':
        depth -= 1
        if depth==0:
            end=i+1; break
else: raise SystemExit('Campaign build end not found')

build = r'''  @override
  Widget build(BuildContext context) {
    final quickItems = showAllQuickCategories ? quick : quick.take(8).toList();
    return FutureBuilder<List<Map<String, dynamic>>>(
      future: future,
      builder: (context, snapshot) {
        var campaigns = snapshot.data ?? <Map<String, dynamic>>[];
        if (search.text.trim().isNotEmpty) { final q=_norm(search.text); campaigns=campaigns.where((c)=>_norm([c['title'],c['merchant'],c['category'],c['description'],c['campaign_text']].where((x)=>x!=null).join(' ')).contains(q)).toList(); }
        if (category.isNotEmpty) campaigns=campaigns.where((c)=>campaignSection(c)==category || '${c['category']??''}'==category).toList();
        if (showFavoritesOnly) campaigns=campaigns.where((c)=>favoriteIds.contains(campaignId(c))).toList();
        final groups=<String,List<Map<String,dynamic>>>{}; for(final c in campaigns){groups.putIfAbsent(campaignSection(c),()=>[]).add(c);}
        return RefreshIndicator(
          onRefresh: () async { setState(()=>future=fetchCampaigns()); await future; },
          child: CustomScrollView(slivers:[
            SliverPadding(padding:const EdgeInsets.fromLTRB(16,14,16,0),sliver:SliverToBoxAdapter(child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[
              Row(children:[Expanded(child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[const Text('Kart Kampanya',style:TextStyle(fontSize:27,fontWeight:FontWeight.w900,color:Colors.white)),const SizedBox(height:3),const Text('Tüm banka kampanyaları tek yerde!',style:TextStyle(fontSize:14,color:Color(0xFFAEB9D0),fontWeight:FontWeight.w500))])),IconButton(onPressed:()=>setState(()=>future=fetchCampaigns()),icon:const Icon(Icons.refresh_rounded,size:29,color:Colors.white)),IconButton(onPressed:()=>Supabase.instance.client.auth.signOut(),icon:const Icon(Icons.logout_rounded,size:27,color:Colors.white))]),
              const SizedBox(height:16),
              TextField(controller:search,onChanged:(_)=>setState((){}),decoration:InputDecoration(hintText:'Kampanya, marka veya kategori ara...',hintStyle:const TextStyle(color:Color(0xFF91A0BC)),prefixIcon:const Icon(Icons.search_rounded,color:Color(0xFFB7C2D8)),filled:true,fillColor:const Color(0xFF111C30),contentPadding:const EdgeInsets.symmetric(vertical:15),border:OutlineInputBorder(borderRadius:BorderRadius.all(Radius.circular(18)),borderSide:const BorderSide(color:Color(0xFF30415C))),enabledBorder:OutlineInputBorder(borderRadius:BorderRadius.all(Radius.circular(18)),borderSide:const BorderSide(color:Color(0xFF30415C))),focusedBorder:OutlineInputBorder(borderRadius:BorderRadius.all(Radius.circular(18)),borderSide:const BorderSide(color:Color(0xFF6B52E8),width:1.5)))),
              const SizedBox(height:16),
              GridView.builder(shrinkWrap:true,physics:const NeverScrollableScrollPhysics(),itemCount:quickItems.length,gridDelegate:const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount:4,crossAxisSpacing:9,mainAxisSpacing:9,childAspectRatio:.94),itemBuilder:(_,i){final q=quickItems[i];final selected=category==q[1];return InkWell(onTap:()=>setState(()=>category=selected?'':q[1]),borderRadius:BorderRadius.circular(18),child:Container(decoration:BoxDecoration(color:selected?const Color(0xFF6245EF):const Color(0xFF0E1B30),borderRadius:BorderRadius.circular(18),border:Border.all(color:selected?const Color(0xFF8069FF):const Color(0xFF2B4666))),child:Column(mainAxisAlignment:MainAxisAlignment.center,children:[Text(q[0],style:const TextStyle(fontSize:27)),const SizedBox(height:5),Padding(padding:const EdgeInsets.symmetric(horizontal:4),child:Text(q[1],maxLines:1,overflow:TextOverflow.ellipsis,textAlign:TextAlign.center,style:const TextStyle(color:Colors.white,fontWeight:FontWeight.w700,fontSize:12)))])));}),
              if(quick.length>8) Align(alignment:Alignment.center,child:TextButton(onPressed:()=>setState(()=>showAllQuickCategories=!showAllQuickCategories),child:Text(showAllQuickCategories?'Daha az':'Tüm kategoriler'))),
              SingleChildScrollView(scrollDirection:Axis.horizontal,child:Row(children:[chip('Tümü',!showFavoritesOnly&&category.isEmpty,()=>setState((){category='';showFavoritesOnly=false;})),chip('Bana Uygun',widget.mode=='matched',()=>setState(()=>showFavoritesOnly=false)),chip('Favoriler',showFavoritesOnly,()=>setState(()=>showFavoritesOnly=!showFavoritesOnly)),chip('Son Eklenen',false,()=>setState(()=>showAllCampaigns=true))])),
              const SizedBox(height:18),
            ]))),
            if(snapshot.connectionState==ConnectionState.waiting) const SliverFillRemaining(hasScrollBody:false,child:Center(child:CircularProgressIndicator()))
            else if(snapshot.hasError) const SliverFillRemaining(hasScrollBody:false,child:Center(child:Text('Kampanyalar yüklenemedi. Aşağı çekerek tekrar dene.',textAlign:TextAlign.center,style:TextStyle(color:Colors.white70))))
            else if(groups.isEmpty) const SliverFillRemaining(hasScrollBody:false,child:Center(child:Text('Bu filtreye uygun kampanya bulunamadı.',style:TextStyle(color:Colors.white70))))
            else ...groups.entries.map((e)=>SliverPadding(padding:const EdgeInsets.fromLTRB(16,0,16,4),sliver:SliverToBoxAdapter(child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[Row(children:[Expanded(child:Text('${emoji(e.key)}  ${e.key}',style:const TextStyle(fontSize:22,fontWeight:FontWeight.w900,color:Colors.white))),Text('${e.value.length} kampanya',style:const TextStyle(color:Color(0xFFB5C0D6),fontWeight:FontWeight.w600))]),const SizedBox(height:10),...e.value.map((c)=>SmartCampaignCard(campaign:c,isFavorite:favoriteIds.contains(campaignId(c)),isCompared:compareIds.contains(campaignId(c)),showAllCampaigns:showAllCampaigns,expiringSoon:isExpiringSoon(c),daysRemaining:daysLeft(c),onFavorite:()=>toggleFavorite(c),onCompare:()=>toggleCompare(c),onOpenUrl:openCampaignUrl,requiredSteps:requiredSteps(c),completedSteps:campaignProgress[campaignId(c)]??0,onProgressChange:(v)=>setState(()=>campaignProgress[campaignId(c)]=v)))]))),),
            const SliverToBoxAdapter(child:SizedBox(height:20)),
          ]),
        );
      },
    );
  }

  Widget chip(String label,bool selected,VoidCallback onTap)=>Padding(padding:const EdgeInsets.only(right:8),child:InkWell(onTap:onTap,borderRadius:BorderRadius.circular(14),child:Container(padding:const EdgeInsets.symmetric(horizontal:15,vertical:11),decoration:BoxDecoration(color:selected?const Color(0xFF5D43E7):const Color(0xFF151A25),borderRadius:BorderRadius.circular(14),border:Border.all(color:selected?const Color(0xFF806BFF):const Color(0xFF3A3F4B))),child:Row(mainAxisSize:MainAxisSize.min,children:[Icon(label=='Favoriler'?Icons.star_rounded:label=='Bana Uygun'?Icons.track_changes_rounded:label=='Son Eklenen'?Icons.schedule_rounded:Icons.apps_rounded,size:18,color:Colors.white),const SizedBox(width:7),Text(label,style:const TextStyle(color:Colors.white,fontWeight:FontWeight.w700))]))));
  String emoji(String v){const m={'Otomotiv':'🚗','Akaryakıt':'⛽','Market':'🛒','Restoran':'🍔','E-ticaret':'🛍️','Elektronik':'📱','Giyim':'👕','Ev & Yaşam':'🏠','Seyahat':'✈️','Eğlence':'🎬','Spor':'🏋️'};return m[v]??'✨';}
'''
s = s[:start] + build + s[end:]
p.write_text(s,encoding='utf-8')
print('v22 applied')
