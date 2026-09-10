from pathlib import Path
p=Path('lib/main.dart')
s=p.read_text(encoding='utf-8')

def replace_class(src,name,repl):
    start=src.find('class '+name)
    if start<0: raise SystemExit(name+' not found')
    brace=src.find('{',start); depth=0; quote=None; esc=False
    for i in range(brace,len(src)):
        ch=src[i]
        if quote:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch==quote: quote=None
        elif ch in "'\"": quote=ch
        elif ch=='{': depth+=1
        elif ch=='}':
            depth-=1
            if depth==0: return src[:start]+repl+src[i+1:]
    raise SystemExit(name+' end not found')

def replace_method(src,state,method,repl):
    st=src.find('class '+state)
    start=src.find('  @override\n  Widget '+method,st)
    if start<0: raise SystemExit(state+' '+method+' not found')
    brace=src.find('{',start); depth=0; quote=None; esc=False
    for i in range(brace,len(src)):
        ch=src[i]
        if quote:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch==quote: quote=None
        elif ch in "'\"": quote=ch
        elif ch=='{': depth+=1
        elif ch=='}':
            depth-=1
            if depth==0: return src[:start]+repl+src[i+1:]
    raise SystemExit(method+' end not found')

old="""      theme: ThemeData(\n        useMaterial3: true,\n        colorScheme: ColorScheme.fromSeed(\n          seedColor: const Color(0xFF5B4BDB),\n          brightness: Brightness.dark,\n        ),\n        scaffoldBackgroundColor: const Color(0xFF081120),\n        appBarTheme: const AppBarTheme(\n          elevation: 0,\n          backgroundColor: const Color(0xFF081120),\n          foregroundColor: Colors.white,\n        ),\n        cardTheme: const CardThemeData(\n          elevation: 0,\n          margin: EdgeInsets.zero,\n          surfaceTintColor: Colors.transparent,\n        ),\n      ),"""
new="""      theme: ThemeData(\n        useMaterial3: true,\n        brightness: Brightness.light,\n        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF6C5CE7), brightness: Brightness.light),\n        scaffoldBackgroundColor: const Color(0xFFF3F2F8),\n        appBarTheme: const AppBarTheme(elevation: 0, scrolledUnderElevation: 0, backgroundColor: Color(0xFFF3F2F8), foregroundColor: Color(0xFF1E1B2E)),\n        inputDecorationTheme: const InputDecorationTheme(\n          filled: true, fillColor: Colors.white,\n          border: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(14)), borderSide: BorderSide(color: Color(0xFFECEAF3))),\n          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(14)), borderSide: BorderSide(color: Color(0xFFECEAF3))),\n          focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(14)), borderSide: BorderSide(color: Color(0xFF6C5CE7), width: 1.4)),\n          contentPadding: EdgeInsets.symmetric(horizontal: 14, vertical: 13),\n        ),\n        cardTheme: const CardThemeData(elevation: 0, margin: EdgeInsets.zero, surfaceTintColor: Colors.transparent),\n      ),"""
if old in s: s=s.replace(old,new,1)

helpers=r'''String _claudeCleanTitle(Map<String,dynamic> c) {
  final raw=decodeHtmlEntities('${c['title']??''}').replaceAll(RegExp(r'\\s+'),' ').trim();
  final bad=RegExp(r'(men[uü]|kampanyalar|kredi kartlar[iı]|banka kartlar[iı]|[oö]deme kolayl[iı]klar[iı]|blog|hemen ba[sş]vur|ba[sş]vur arama)',caseSensitive:false);
  if(raw.length>80 && bad.hasMatch(raw)) {
    final merchant=decodeHtmlEntities('${c['merchant']??''}').trim();
    final value='${c['reward_value']??c['reward']??''}'.trim();
    final type='${c['reward_type']??''}'.trim();
    if(merchant.isNotEmpty && value.isNotEmpty) return "$merchant’ta $value ${type.isNotEmpty?type:'Avantaj'}";
    if(merchant.isNotEmpty) return merchant;
  }
  return raw.isEmpty?'Kampanya':raw;
}
String _claudeMerchantUrl(String merchant) {
  final m=_norm(merchant);
  const domains=<String,String>{
    'petrol ofisi':'petrolofisi.com','migros':'migros.com.tr','trendyol':'trendyol.com','shell':'shell.com','starbucks':'starbucks.com','amazon':'amazon.com.tr','hepsiburada':'hepsiburada.com','a101':'a101.com.tr','carrefour':'carrefoursa.com','opet':'opet.com.tr','akbank':'akbank.com','garanti':'garantibbva.com.tr','qnb':'qnb.com.tr','yapi kredi':'worldcard.com.tr','is bankasi':'isbank.com.tr','iş bankası':'isbank.com.tr'};
  for(final e in domains.entries) if(m.contains(e.key)) return 'https://cdn.brandfetch.io/${e.value}/w/600/h/600/logo';
  return '';
}
String _claudeDate(Map<String,dynamic> c) {
  final a='${c['start_date']??''}'.trim(),b='${c['end_date']??''}'.trim();
  String f(String x){final d=DateTime.tryParse(x);return d==null?x:'${d.day}-${d.month} ${d.year}';}
  if(a.isNotEmpty&&b.isNotEmpty)return '${f(a)} - ${f(b)}';
  if(b.isNotEmpty)return f(b);
  return '';
}
'''
if '_claudeCleanTitle(' not in s:
    marker='class SmartCampaignCard extends StatelessWidget {'
    s=s.replace(marker,helpers+'\n'+marker,1)

build=r'''  @override
  Widget build(BuildContext context) {
    final isHome=widget.mode=='home';
    return Scaffold(
      backgroundColor: const Color(0xFFF3F2F8),
      body: FutureBuilder<List<Map<String,dynamic>>>(
        future: future,
        builder:(context,snapshot){
          var rows=List<Map<String,dynamic>>.from(snapshot.data??const <Map<String,dynamic>>[]);
          if(search.text.trim().isNotEmpty){final q=_norm(search.text);rows=rows.where((c)=>_norm([c['title'],c['merchant'],c['category'],c['description'],c['campaign_text']].where((x)=>x!=null).join(' ')).contains(q)).toList();}
          if(category.isNotEmpty)rows=rows.where((c)=>campaignSection(c)==category||'${c['category']??''}'==category).toList();
          if(showFavoritesOnly)rows=rows.where((c)=>favoriteIds.contains(campaignId(c))).toList();
          if(widget.mode=='matched'&&widget.cards.isNotEmpty)rows=rows.where((c)=>widget.cards.any((card)=>cardMatches(c,card))).toList();
          return RefreshIndicator(onRefresh:()async{setState(()=>future=fetchCampaigns());await future;},child:ListView(padding:const EdgeInsets.fromLTRB(20,8,20,20),children:[
            if(!isHome) ...[
              Row(children:[Expanded(child:TextField(controller:search,onChanged:(_)=>setState((){}),onSubmitted:(_)=>searchNow(),decoration:const InputDecoration(prefixIcon:Icon(Icons.search_rounded),hintText:'Kampanya, banka veya kategori ara...'))),const SizedBox(width:9),InkWell(onTap:(){showModalBottomSheet(context:context,showDragHandle:true,builder:(_)=>Padding(padding:const EdgeInsets.fromLTRB(20,8,20,30),child:Wrap(spacing:8,runSpacing:8,children:[for(final x in const ['Tümü','Market','Akaryakıt','Restoran','Seyahat','E-ticaret','Elektronik','Giyim'])ActionChip(label:Text(x),onPressed:(){Navigator.pop(context);setState(()=>category=x=='Tümü'?'':x);})])));},borderRadius:BorderRadius.circular(14),child:Container(padding:const EdgeInsets.symmetric(horizontal:13,vertical:13),decoration:BoxDecoration(color:const Color(0xFFEFEBFC),borderRadius:BorderRadius.circular(14),border:Border.all(color:const Color(0xFFE1D9FA))),child:const Row(children:[Icon(Icons.tune_rounded,size:17,color:Color(0xFF6C5CE7)),SizedBox(width:5),Text('Filtrele',style:TextStyle(fontSize:12,fontWeight:FontWeight.w800,color:Color(0xFF6C5CE7))) ]))) ]),
              const SizedBox(height:11),
              SingleChildScrollView(scrollDirection:Axis.horizontal,child:Row(children:[_claudeChip('Tümü',category.isEmpty,()=>setState(()=>category='')),_claudeChip('Market',category=='Market',()=>setState(()=>category='Market')),_claudeChip('Akaryakıt',category=='Akaryakıt',()=>setState(()=>category='Akaryakıt')),_claudeChip('Yemek',category=='Restoran',()=>setState(()=>category='Restoran')),_claudeChip('Seyahat',category=='Seyahat',()=>setState(()=>category='Seyahat')),_claudeChip('Online',category=='E-ticaret',()=>setState(()=>category='E-ticaret'))])),
              const SizedBox(height:12),
            ],
            if(isHome)...[const Padding(padding:EdgeInsets.only(bottom:10),child:Text('Kampanyalar',style:TextStyle(fontSize:22,fontWeight:FontWeight.w900,color:Color(0xFF1E1B2E))))],
            if(snapshot.connectionState==ConnectionState.waiting)const Padding(padding:EdgeInsets.all(45),child:Center(child:CircularProgressIndicator())),
            if(snapshot.hasError)const Padding(padding:EdgeInsets.all(30),child:Center(child:Text('Kampanyalar yüklenemedi.\nAşağı çekerek tekrar dene.',textAlign:TextAlign.center))),
            if(snapshot.connectionState!=ConnectionState.waiting&&!snapshot.hasError&&rows.isEmpty)const Padding(padding:EdgeInsets.all(30),child:Center(child:Text('Bu filtreye uygun kampanya bulunamadı.'))),
            if(snapshot.connectionState!=ConnectionState.waiting&&!snapshot.hasError)...rows.map((c)=>SmartCampaignCard(campaign:c,isFavorite:favoriteIds.contains(campaignId(c)),isCompared:compareIds.contains(campaignId(c)),showAllCampaigns:showAllCampaigns,expiringSoon:isExpiringSoon(c),daysRemaining:daysLeft(c),onFavorite:()=>toggleFavorite(c),onCompare:()=>toggleCompare(c),onOpenUrl:openCampaignUrl,requiredSteps:requiredSteps(c),completedSteps:currentProgress(c),onProgressChange:(d)=>changeProgress(c,d)))
          ]));
        },
      ),
    );
  }
  Widget _claudeChip(String text,bool selected,VoidCallback onTap)=>Padding(padding:const EdgeInsets.only(right:8),child:InkWell(onTap:onTap,borderRadius:BorderRadius.circular(20),child:Container(padding:const EdgeInsets.symmetric(horizontal:17,vertical:10),decoration:BoxDecoration(color:selected?const Color(0xFF6C5CE7):Colors.white,borderRadius:BorderRadius.circular(20),border:Border.all(color:selected?const Color(0xFF6C5CE7):const Color(0xFFECEAF3))),child:Text(text,style:TextStyle(color:selected?Colors.white:const Color(0xFF1E1B2E),fontSize:12.5,fontWeight:FontWeight.w700)))));
'''
s=replace_method(s,'_CampaignsPageState','build',build)

smart=r'''class SmartCampaignCard extends StatelessWidget {
  final Map<String,dynamic> campaign;
  final bool isFavorite,isCompared,showAllCampaigns,expiringSoon;
  final int daysRemaining,requiredSteps,completedSteps;
  final VoidCallback onFavorite,onCompare;
  final Future<void> Function(String url) onOpenUrl;
  final ValueChanged<int> onProgressChange;
  const SmartCampaignCard({super.key,required this.campaign,required this.isFavorite,required this.isCompared,required this.showAllCampaigns,required this.expiringSoon,required this.daysRemaining,required this.onFavorite,required this.onCompare,required this.onOpenUrl,required this.requiredSteps,required this.completedSteps,required this.onProgressChange});
  @override Widget build(BuildContext context){
    final title=_claudeCleanTitle(campaign);
    final merchant=decodeHtmlEntities('${campaign['merchant']??''}').trim();
    final desc=decodeHtmlEntities('${campaign['description']??campaign['campaign_text']??''}').replaceAll(RegExp(r'\\s+'),' ').trim();
    final cat=decodeHtmlEntities('${campaign['category']??''}').trim();
    final date=_claudeDate(campaign);
    final logo=_claudeMerchantUrl(merchant);
    final reward=campaign['_calculatedReward']??campaign['_reward'];
    String initials(String x){final q=x.trim();if(q.isEmpty)return 'K';final a=q.split(RegExp(r'\\s+'));return a.length>1?'${a.first[0]}${a.last[0]}':a.first.substring(0,1).toUpperCase();}
    return Container(margin:const EdgeInsets.only(bottom:13),padding:const EdgeInsets.fromLTRB(14,14,14,13),decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(18),border:Border.all(color:const Color(0xFFECEAF3)),boxShadow:[BoxShadow(color:Colors.black12.withOpacity(.025),blurRadius:9,offset:const Offset(0,2))]),child:InkWell(borderRadius:BorderRadius.circular(18),onTap:()=>Navigator.of(context).push(MaterialPageRoute(builder:(_)=>CampaignDetailPage(campaign:campaign))),child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[
      Row(crossAxisAlignment:CrossAxisAlignment.start,children:[Container(width:102,height:102,decoration:BoxDecoration(color:const Color(0xFFF8F7FB),borderRadius:BorderRadius.circular(15)),padding:const EdgeInsets.all(10),child:logo.isEmpty?Center(child:Text(initials(merchant),style:const TextStyle(fontSize:25,fontWeight:FontWeight.w900,color:Color(0xFF6C5CE7)))):Image.network(logo,fit:BoxFit.contain,errorBuilder:(_,__,___)=>Center(child:Text(initials(merchant),style:const TextStyle(fontSize:25,fontWeight:FontWeight.w900,color:Color(0xFF6C5CE7))))),const SizedBox(width:13),Expanded(child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[Row(children:[Expanded(child:Text(title,maxLines:3,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:16.5,height:1.12,fontWeight:FontWeight.w900,color:Color(0xFF1E1B2E)))),IconButton(onPressed:onFavorite,padding:EdgeInsets.zero,constraints:const BoxConstraints(minWidth:34,minHeight:34),icon:Icon(isFavorite?Icons.star_rounded:Icons.star_border_rounded,size:29,color:Color(0xFF575361)))]),if(expiringSoon)Align(alignment:Alignment.centerRight,child:Container(margin:const EdgeInsets.only(top:2),padding:const EdgeInsets.symmetric(horizontal:10,vertical:6),decoration:BoxDecoration(color:daysRemaining<=3?const Color(0xFFFDE7E9):const Color(0xFFE3F9EB),borderRadius:BorderRadius.circular(18)),child:Text(daysRemaining<=0?'Son gün': 'Son $daysRemaining Gün',style:TextStyle(fontSize:10,fontWeight:FontWeight.w800,color:daysRemaining<=3?const Color(0xFFE0435C):const Color(0xFF1EA35A))))),])),
      ]),
      const SizedBox(height:10),
      if(desc.isNotEmpty)Text(desc,maxLines:3,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:12.5,height:1.28,color:Color(0xFF676373))),
      const SizedBox(height:11),
      Wrap(spacing:7,runSpacing:7,children:[if(cat.isNotEmpty)_infoChip(Icons.local_offer_outlined,cat),if(merchant.isNotEmpty)_infoChip(Icons.credit_card_outlined,merchant),if(date.isNotEmpty)_infoChip(Icons.calendar_today_outlined,date),if(reward!=null&&reward is num)_infoChip(Icons.card_giftcard_outlined,'${reward.toStringAsFixed(0)} TL')]),
      const SizedBox(height:11),
      Row(children:[const Spacer(),IconButton(onPressed:onCompare,icon:Icon(Icons.compare_arrows_rounded,size:22,color:Color(0xFF5A5662))),const SizedBox(width:2),InkWell(onTap:()=>Navigator.of(context).push(MaterialPageRoute(builder:(_)=>CampaignDetailPage(campaign:campaign))),borderRadius:BorderRadius.circular(13),child:Container(padding:const EdgeInsets.symmetric(horizontal:18,vertical:11),decoration:BoxDecoration(gradient:const LinearGradient(colors:[Color(0xFF7B45EF),Color(0xFF6840D9)]),borderRadius:BorderRadius.circular(13)),child:const Row(mainAxisSize:MainAxisSize.min,children:[Text('Detaylar',style:TextStyle(fontSize:12,fontWeight:FontWeight.w800,color:Colors.white)),SizedBox(width:4),Icon(Icons.arrow_forward_rounded,size:16,color:Colors.white)])))])
    ])));
  }
  Widget _infoChip(IconData icon,String text)=>Container(padding:const EdgeInsets.symmetric(horizontal:10,vertical:7),decoration:BoxDecoration(color:const Color(0xFFF1EFFA),borderRadius:BorderRadius.circular(15)),child:Row(mainAxisSize:MainAxisSize.min,children:[Icon(icon,size:13,color:const Color(0xFF4A4762)),const SizedBox(width:5),ConstrainedBox(constraints:const BoxConstraints(maxWidth:145),child:Text(text,maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:10.5,fontWeight:FontWeight.w600,color:Color(0xFF4A4762))))]));
}
'''
s=replace_class(s,'SmartCampaignCard',smart)
p.write_text(s,encoding='utf-8')
print('Applied Claude Flutter reference UI')
