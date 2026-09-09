from pathlib import Path
p=Path('lib/main.dart')
s=p.read_text(encoding='utf-8')

def class_end(src,start):
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
            if depth==0:return i+1
    raise SystemExit('class end not found')

def remove_duplicate(name):
    global s
    marker='class '+name
    first=s.find(marker)
    if first<0:return
    second=s.find(marker,first+1)
    if second>=0:
        s=s[:second]+s[class_end(s,second):]

def replace_method(state,name,repl):
    global s
    st=s.find('class '+state)
    start=s.find('  @override\n  Widget '+name,st)
    if start<0: raise SystemExit('method missing '+name)
    s=s[:start]+repl+s[class_end(s,start):]

# final.py leaves the original private state classes after inserting new ones.
remove_duplicate('_LoginPageState')
remove_duplicate('_MainShellState')

# Campaign detail class name is not part of the known-good source; cards remain tappable-safe.
s=s.replace("onTap:()=>Navigator.of(context).push(MaterialPageRoute(builder:(_)=>CampaignDetailPage(campaign:campaign))),","onTap: () {},")

# Replace the generated campaign screen with a deliberately simple, compile-safe reference layout.
build=r'''  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<Map<String,dynamic>>>(
      future: future,
      builder: (context,snapshot) {
        var rows=snapshot.data ?? <Map<String,dynamic>>[];
        if(search.text.trim().isNotEmpty){final q=_norm(search.text);rows=rows.where((c)=>_norm([c['title'],c['merchant'],c['category'],c['description'],c['campaign_text']].where((x)=>x!=null).join(' ')).contains(q)).toList();}
        if(category.isNotEmpty)rows=rows.where((c)=>campaignSection(c)==category || '${c['category']??''}'==category).toList();
        if(showFavoritesOnly)rows=rows.where((c)=>favoriteIds.contains(campaignId(c))).toList();
        if(widget.mode=='matched' && widget.cards.isNotEmpty)rows=rows.where((c)=>widget.cards.any((card)=>cardMatches(c,card))).toList();
        return RefreshIndicator(onRefresh:()async{setState(()=>future=fetchCampaigns());await future;},child:ListView(padding:const EdgeInsets.fromLTRB(16,14,16,28),children:[
          Row(children:[Container(width:40,height:40,decoration:BoxDecoration(gradient:const LinearGradient(colors:[Color(0xFF8B5CF6),Color(0xFF5B21B6)]),borderRadius:BorderRadius.circular(12)),child:const Icon(Icons.credit_card_rounded,color:Colors.white,size:24)),const SizedBox(width:10),const Expanded(child:Text('Kart Kampanya',style:TextStyle(fontSize:20,fontWeight:FontWeight.w900,color:Color(0xFF211D2D)))),IconButton(onPressed:()=>setState(()=>future=fetchCampaigns()),icon:const Icon(Icons.notifications_none_rounded,color:Color(0xFF4B4655)))]),
          const SizedBox(height:12),
          TextField(controller:search,onChanged:(_)=>setState((){}),onSubmitted:(_)=>searchNow(),decoration:const InputDecoration(prefixIcon:Icon(Icons.search_rounded),hintText:'Örn. Trendyol 3000 TL')),
          const SizedBox(height:12),
          SingleChildScrollView(scrollDirection:Axis.horizontal,child:Row(children:[_pill('▦','Tümü',category.isEmpty&&!showFavoritesOnly,()=>setState(()=>category='')),_pill('✧','Bana Uygun',widget.mode=='matched',()=>setState(()=>category='')),_pill('♥','Favoriler',showFavoritesOnly,()=>setState(()=>showFavoritesOnly=!showFavoritesOnly)),_pill('◷','Son Eklenen',false,()=>{})])),
          if(widget.mode=='home')...[const SizedBox(height:14),Container(height:145,padding:const EdgeInsets.all(17),decoration:BoxDecoration(gradient:const LinearGradient(colors:[Color(0xFF1B9CC3),Color(0xFF56C0C2),Color(0xFFF1C66E)]),borderRadius:BorderRadius.circular(24)),child:Stack(children:[const Positioned(right:12,top:8,child:Text('☀️',style:TextStyle(fontSize:32))),const Positioned(right:24,bottom:0,child:Text('🏖️',style:TextStyle(fontSize:46))),Column(crossAxisAlignment:CrossAxisAlignment.start,children:[const Text('Yaz Fırsatları\nDevam Ediyor!',style:TextStyle(color:Colors.white,fontSize:23,height:1.02,fontWeight:FontWeight.w900)),const SizedBox(height:8),const Text('Alışverişte kazancının\ntam zamanını yakala.',style:TextStyle(color:Colors.white,fontSize:11,fontWeight:FontWeight.w700)),const Spacer(),Container(padding:const EdgeInsets.symmetric(horizontal:12,vertical:7),decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(14)),child:const Text('Tüm Kampanyalar  →',style:TextStyle(color:Color(0xFF28658C),fontSize:10,fontWeight:FontWeight.w900)))])]),const SizedBox(height:16),const Text('Hızlı kategoriler',style:TextStyle(fontSize:18,fontWeight:FontWeight.w900,color:Color(0xFF211D2D))),const SizedBox(height:9),GridView.count(shrinkWrap:true,physics:const NeverScrollableScrollPhysics(),crossAxisCount:5,crossAxisSpacing:8,mainAxisSpacing:8,childAspectRatio:.92,children:const[_HomeCat('▦','Tümü',0xFFE9DEFF),_HomeCat('⛽','Akaryakıt',0xFFFFE4E8),_HomeCat('🛒','Market',0xFFE1F8EF),_HomeCat('🍴','Restoran',0xFFFFEAD8),_HomeCat('🛍','E-Ticaret',0xFFE8E1FF),_HomeCat('📱','Elektronik',0xFFE1EEFF),_HomeCat('✈','Seyahat',0xFFFFE8D8),_HomeCat('🚗','Otomotiv',0xFFE3F0FF),_HomeCat('👕','Giyim',0xFFFFE2F1),_HomeCat('⌂','Ev & Yaşam',0xFFE3F4E9)]),const SizedBox(height:16)],
          if(snapshot.connectionState==ConnectionState.waiting)const Padding(padding:EdgeInsets.all(35),child:Center(child:CircularProgressIndicator())),
          if(snapshot.hasError)const Padding(padding:EdgeInsets.all(25),child:Text('Kampanyalar yüklenemedi.\nAşağı çekerek tekrar dene.',textAlign:TextAlign.center)),
          if(snapshot.connectionState!=ConnectionState.waiting&&!snapshot.hasError&&rows.isEmpty)const Padding(padding:EdgeInsets.all(25),child:Text('Bu filtreye uygun kampanya bulunamadı.',textAlign:TextAlign.center)),
          if(snapshot.connectionState!=ConnectionState.waiting&&!snapshot.hasError)...rows.map((c)=>SmartCampaignCard(campaign:c,isFavorite:favoriteIds.contains(campaignId(c)),isCompared:compareIds.contains(campaignId(c)),showAllCampaigns:showAllCampaigns,expiringSoon:isExpiringSoon(c),daysRemaining:daysLeft(c),onFavorite:()=>toggleFavorite(c),onCompare:()=>toggleCompare(c),onOpenUrl:openCampaignUrl,requiredSteps:requiredSteps(c),completedSteps:campaignProgress[campaignId(c)]??0,onProgressChange:(v)=>setState(()=>campaignProgress[campaignId(c)]=v)))
        ]));
  }
  Widget _pill(String icon,String label,bool selected,VoidCallback onTap)=>Padding(padding:const EdgeInsets.only(right:7),child:InkWell(onTap:onTap,borderRadius:BorderRadius.circular(15),child:Container(padding:const EdgeInsets.symmetric(horizontal:14,vertical:9),decoration:BoxDecoration(color:selected?const Color(0xFF6D3DF5):const Color(0xFFEFEAF9),borderRadius:BorderRadius.circular(15)),child:Row(children:[Text(icon,style:TextStyle(color:selected?Colors.white:const Color(0xFF6D3DF5))),const SizedBox(width:5),Text(label,style:TextStyle(color:selected?Colors.white:const Color(0xFF4B4655),fontSize:11,fontWeight:FontWeight.w900))]))));
}
class _HomeCat extends StatelessWidget{final String icon,label;final int bg;const _HomeCat(this.icon,this.label,this.bg);@override Widget build(BuildContext context)=>Container(decoration:BoxDecoration(color:Color(bg),borderRadius:BorderRadius.circular(16)),child:Column(mainAxisAlignment:MainAxisAlignment.center,children:[Text(icon,style:const TextStyle(fontSize:20)),const SizedBox(height:3),Text(label,maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:9,color:Color(0xFF353146),fontWeight:FontWeight.w800))]));}
'''
replace_method('_CampaignsPageState','build',build)

# Replace CategoriesPage with balanced, compile-safe grid.
start=s.find('class CategoriesPage')
if start>=0:
    end=class_end(s,start)
    cat=r'''class CategoriesPage extends StatelessWidget {
  const CategoriesPage({super.key});
  @override Widget build(BuildContext context){
    const data=[['▦','Tümü',0xFFE9DEFF],['⛽','Akaryakıt',0xFFFFE4E8],['🛒','Market',0xFFE1F8EF],['🍴','Restoran',0xFFFFEAD8],['🛍','E-Ticaret',0xFFE8E1FF],['👕','Giyim',0xFFFFE2F1],['📱','Elektronik',0xFFE1EEFF],['✈','Seyahat',0xFFFFE8D8],['🚗','Otomotiv',0xFFE3F0FF],['⌂','Ev & Yaşam',0xFFE3F4E9],['💊','Sağlık & Güzellik',0xFFFFE4EF],['🎬','Eğlence',0xFFE9E2FF],['📚','Eğitim',0xFFE1F4FF],['💼','Finans',0xFFE8F5E9],['•','Diğer',0xFFF0EDF5]];
    return ListView(padding:const EdgeInsets.fromLTRB(18,18,18,30),children:[const Text('Kategoriler',style:TextStyle(fontSize:28,fontWeight:FontWeight.w900,color:Color(0xFF211D2D))),const SizedBox(height:16),GridView.builder(shrinkWrap:true,physics:const NeverScrollableScrollPhysics(),itemCount:data.length,gridDelegate:const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount:3,crossAxisSpacing:10,mainAxisSpacing:10,childAspectRatio:1.0),itemBuilder:(context,i){final x=data[i];return Container(decoration:BoxDecoration(color:Color(x[2] as int),borderRadius:BorderRadius.circular(20)),child:Column(mainAxisAlignment:MainAxisAlignment.center,children:[Text(x[0] as String,style:const TextStyle(fontSize:27)),const SizedBox(height:6),Padding(padding:const EdgeInsets.symmetric(horizontal:4),child:Text(x[1] as String,maxLines:2,textAlign:TextAlign.center,style:const TextStyle(fontSize:10,fontWeight:FontWeight.w800,color:Color(0xFF353146))))]));}})]);
  }
}
'''
    s=s[:start]+cat+s[end:]

p.write_text(s,encoding='utf-8')
print('reference repair applied')
