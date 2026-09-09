from pathlib import Path
p=Path('lib/main.dart')
s=p.read_text(encoding='utf-8')

def replace_class(src,name,repl):
    start=src.find('class '+name)
    if start<0: raise SystemExit(name+' not found')
    brace=src.find('{',start); depth=0
    for i in range(brace,len(src)):
        if src[i]=='{': depth+=1
        elif src[i]=='}':
            depth-=1
            if depth==0:return src[:start]+repl+src[i+1:]
    raise SystemExit(name+' end not found')

def replace_method(src, state_name, method_name, repl):
    state=src.find('class '+state_name)
    start=src.find('  @override\n  Widget '+method_name, state)
    if start<0: raise SystemExit(state_name+' '+method_name+' not found')
    brace=src.find('{',start);depth=0
    for i in range(brace,len(src)):
        if src[i]=='{':depth+=1
        elif src[i]=='}':
            depth-=1
            if depth==0:return src[:start]+repl+src[i+1:]
    raise SystemExit('method end not found')

smart=r'''class SmartCampaignCard extends StatelessWidget {
  final Map<String,dynamic> campaign;
  final bool isFavorite,isCompared,showAllCampaigns,expiringSoon;
  final int daysRemaining,requiredSteps,completedSteps;
  final VoidCallback onFavorite,onCompare;
  final Future<void> Function(String url) onOpenUrl;
  final ValueChanged<int> onProgressChange;
  const SmartCampaignCard({super.key,required this.campaign,required this.isFavorite,required this.isCompared,required this.showAllCampaigns,required this.expiringSoon,required this.daysRemaining,required this.onFavorite,required this.onCompare,required this.onOpenUrl,required this.requiredSteps,required this.completedSteps,required this.onProgressChange});
  String text(dynamic v)=>v==null?'':'$v'.trim();
  String logo(){for(final k in ['logo_url','image_url','merchant_logo','brand_logo']){final v=text(campaign[k]);if(v.isNotEmpty)return v;}return '';}
  @override Widget build(BuildContext context){
    final title=text(campaign['title']).isEmpty?'Kampanya':text(campaign['title']);
    final merchant=text(campaign['merchant']);
    final cat=text(campaign['category']).isEmpty?campaignSection(campaign):text(campaign['category']);
    final image=logo();
    return InkWell(
      borderRadius:BorderRadius.circular(18),
      onTap:()=>Navigator.of(context).push(MaterialPageRoute(builder:(_)=>CampaignDetailPage(campaign:campaign))),
      child:Container(
        margin:const EdgeInsets.only(bottom:12),
        padding:const EdgeInsets.all(12),
        decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(18),border:Border.all(color:const Color(0xFFE5E1EF)),boxShadow:const[BoxShadow(color:Color(0x0A000000),blurRadius:10,offset:Offset(0,3))]),
        child:Row(crossAxisAlignment:CrossAxisAlignment.start,children:[
          Container(width:58,height:58,decoration:BoxDecoration(color:const Color(0xFFF1EDFA),borderRadius:BorderRadius.circular(13)),child:image.isEmpty?const Icon(Icons.local_offer_rounded,color:Color(0xFF6D3DF5),size:27):ClipRRect(borderRadius:BorderRadius.circular(13),child:Image.network(image,fit:BoxFit.contain,errorBuilder:(_,__,___)=>const Icon(Icons.local_offer_rounded,color:Color(0xFF6D3DF5),size:27)))),
          const SizedBox(width:11),
          Expanded(child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[
            if(merchant.isNotEmpty)Text(merchant,maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:10,color:Color(0xFF7C7488),fontWeight:FontWeight.w800)),
            Text(title,maxLines:3,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:14,height:1.16,color:Color(0xFF211D2D),fontWeight:FontWeight.w900)),
            const SizedBox(height:7),
            Wrap(spacing:6,runSpacing:5,children:[Container(padding:const EdgeInsets.symmetric(horizontal:8,vertical:4),decoration:BoxDecoration(color:const Color(0xFFEDE7FF),borderRadius:BorderRadius.circular(9)),child:Text(cat,style:const TextStyle(fontSize:9,color:Color(0xFF5B21B6),fontWeight:FontWeight.w900))),if(expiringSoon)Container(padding:const EdgeInsets.symmetric(horizontal:7,vertical:4),decoration:BoxDecoration(color:const Color(0xFFFFE7E7),borderRadius:BorderRadius.circular(9)),child:Text('Son $daysRemaining Gün',style:const TextStyle(fontSize:8,color:Color(0xFFD33A3A),fontWeight:FontWeight.w900)))])
          ])),
          IconButton(onPressed:onFavorite,icon:Icon(isFavorite?Icons.favorite_rounded:Icons.favorite_border_rounded,color:isFavorite?const Color(0xFFE33F77):const Color(0xFF777187),size:22)),
        ]),
      ),
    );
  }
}
'''
s=replace_class(s,'SmartCampaignCard',smart)

campaign_build=r'''  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<Map<String,dynamic>>>(
      future: future,
      builder: (context,snapshot) {
        var list=snapshot.data ?? <Map<String,dynamic>>[];
        if(search.text.trim().isNotEmpty){final q=_norm(search.text);list=list.where((c)=>_norm([c['title'],c['merchant'],c['category'],c['description'],c['campaign_text']].where((x)=>x!=null).join(' ')).contains(q)).toList();}
        if(category.isNotEmpty)list=list.where((c)=>campaignSection(c)==category||'${c['category']??''}'==category).toList();
        if(showFavoritesOnly)list=list.where((c)=>favoriteIds.contains(campaignId(c))).toList();
        return RefreshIndicator(
          onRefresh:()async{setState(()=>future=fetchCampaigns());await future;},
          child:ListView(padding:const EdgeInsets.fromLTRB(16,14,16,30),children:[
            Row(children:[Container(width:38,height:38,decoration:BoxDecoration(gradient:const LinearGradient(colors:[Color(0xFF8B5CF6),Color(0xFF5B21B6)]),borderRadius:BorderRadius.circular(11)),child:const Icon(Icons.credit_card_rounded,color:Colors.white,size:23)),const SizedBox(width:9),const Expanded(child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[Text('Kart Kampanya',style:TextStyle(fontSize:19,fontWeight:FontWeight.w900,color:Color(0xFF211D2D))),Text('Tüm Banka Kampanyaları Tek Uygulamada',style:TextStyle(fontSize:10,color:Color(0xFF777187),fontWeight:FontWeight.w600))])),IconButton(onPressed:()=>setState(()=>future=fetchCampaigns()),icon:const Icon(Icons.refresh_rounded,color:Color(0xFF4B4655))),IconButton(onPressed:()=>Supabase.instance.client.auth.signOut(),icon:const Icon(Icons.logout_rounded,color:Color(0xFF4B4655)))]),
            const SizedBox(height:12),
            TextField(controller:search,onChanged:(_)=>setState((){}),decoration:const InputDecoration(prefixIcon:Icon(Icons.search_rounded),hintText:'Kampanya, marka veya kategori ara...')),
            const SizedBox(height:12),
            SingleChildScrollView(scrollDirection:Axis.horizontal,child:Row(children:[_pill('▦','Tümü',category.isEmpty&&!showFavoritesOnly,()=>setState((){category='';showFavoritesOnly=false;})),_pill('✧','Bana Uygun',widget.mode=='matched',()=>setState(()=>category='')), _pill('♥','Favoriler',showFavoritesOnly,()=>setState(()=>showFavoritesOnly=!showFavoritesOnly)),_pill('◷','Son Eklenen',false,() {})])),
            if(widget.mode=='home')...[
              const SizedBox(height:14),
              Container(height:140,padding:const EdgeInsets.all(16),decoration:BoxDecoration(gradient:const LinearGradient(colors:[Color(0xFF5424CF),Color(0xFF8C62F7)]),borderRadius:BorderRadius.circular(22)),child:Stack(children:[const Positioned(right:10,top:4,child:Text('☀️',style:TextStyle(fontSize:28))),const Positioned(right:16,bottom:-2,child:Text('🏖️',style:TextStyle(fontSize:42))),Column(crossAxisAlignment:CrossAxisAlignment.start,children:[const Text('Yaz Fırsatları\nDevam Ediyor!',style:TextStyle(color:Colors.white,fontSize:22,height:1.0,fontWeight:FontWeight.w900)),const SizedBox(height:8),const Text('Alışverişte kazancının\ntam zamanını yakala.',style:TextStyle(color:Colors.white,fontSize:11,fontWeight:FontWeight.w700)),const Spacer(),Container(padding:const EdgeInsets.symmetric(horizontal:11,vertical:6),decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(13)),child:const Text('Tüm Kampanyalar  →',style:TextStyle(color:Color(0xFF5B21B6),fontSize:10,fontWeight:FontWeight.w900)))])]),
              const SizedBox(height:16),
              const Text('Kategoriler',style:TextStyle(fontSize:18,fontWeight:FontWeight.w900,color:Color(0xFF211D2D))),
              const SizedBox(height:9),
              GridView.count(shrinkWrap:true,physics:const NeverScrollableScrollPhysics(),crossAxisCount:4,crossAxisSpacing:8,mainAxisSpacing:8,childAspectRatio:1.05,children:const[_HomeCat('⛽','Akaryakıt',0xFFFFE4E8),_HomeCat('🛒','Market',0xFFE1F8EF),_HomeCat('🍴','Restoran',0xFFFFEAD8),_HomeCat('🛍','E-Ticaret',0xFFE8E1FF),_HomeCat('📱','Elektronik',0xFFE1EEFF),_HomeCat('✈','Seyahat',0xFFFFE8D8),_HomeCat('👕','Giyim',0xFFFFE2F1),_HomeCat('⌂','Ev & Yaşam',0xFFE3F4E9)]),
              const SizedBox(height:16),
            ],
            if(snapshot.connectionState==ConnectionState.waiting)const Center(child:Padding(padding:EdgeInsets.all(40),child:CircularProgressIndicator())),
            if(snapshot.hasError)const Center(child:Padding(padding:EdgeInsets.all(30),child:Text('Kampanyalar yüklenemedi.\nAşağı çekerek tekrar dene.',textAlign:TextAlign.center,style:TextStyle(color:Color(0xFF777187))))),
            if(snapshot.connectionState!=ConnectionState.waiting&&!snapshot.hasError&&list.isEmpty)const Center(child:Padding(padding:EdgeInsets.all(30),child:Text('Bu filtreye uygun kampanya bulunamadı.',style:TextStyle(color:Color(0xFF777187))))),
            if(snapshot.connectionState!=ConnectionState.waiting&&!snapshot.hasError)...list.map((c)=>SmartCampaignCard(campaign:c,isFavorite:favoriteIds.contains(campaignId(c)),isCompared:compareIds.contains(campaignId(c)),showAllCampaigns:showAllCampaigns,expiringSoon:isExpiringSoon(c),daysRemaining:daysLeft(c),onFavorite:()=>toggleFavorite(c),onCompare:()=>toggleCompare(c),onOpenUrl:openCampaignUrl,requiredSteps:requiredSteps(c),completedSteps:campaignProgress[campaignId(c)]??0,onProgressChange:(v)=>setState(()=>campaignProgress[campaignId(c)]=v)))
          ]),
        );
      },
    );
  }
  Widget _pill(String icon,String label,bool selected,VoidCallback onTap)=>Padding(padding:const EdgeInsets.only(right:7),child:InkWell(onTap:onTap,borderRadius:BorderRadius.circular(15),child:Container(padding:const EdgeInsets.symmetric(horizontal:15,vertical:10),decoration:BoxDecoration(color:selected?const Color(0xFF6D3DF5):const Color(0xFFEFEAF9),borderRadius:BorderRadius.circular(15)),child:Row(children:[Text(icon,style:TextStyle(color:selected?Colors.white:const Color(0xFF6D3DF5),fontSize:16)),const SizedBox(width:6),Text(label,style:TextStyle(color:selected?Colors.white:const Color(0xFF4B4655),fontSize:11,fontWeight:FontWeight.w900))]))));
}
class _HomeCat extends StatelessWidget{final String icon,label;final int bg;const _HomeCat(this.icon,this.label,this.bg);@override Widget build(BuildContext context)=>Container(decoration:BoxDecoration(color:Color(bg),borderRadius:BorderRadius.circular(16)),child:Column(mainAxisAlignment:MainAxisAlignment.center,children:[Text(icon,style:const TextStyle(fontSize:21)),const SizedBox(height:4),Text(label,maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:9,color:Color(0xFF353146),fontWeight:FontWeight.w800))]));}
'''
s=replace_method(s,'_CampaignsPageState','build',campaign_build)

profile=r'''class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});
  @override
  Widget build(BuildContext context){
    final email=Supabase.instance.client.auth.currentUser?.email??'';
    final items=['Bendeki Kartlar','Favori Kampanyalar','Bildirimler','Ayarlar','Yardım & Destek'];
    return Scaffold(backgroundColor:const Color(0xFFF8F7FC),appBar:AppBar(title:const Text('Profil',style:TextStyle(fontSize:23,fontWeight:FontWeight.w900)),actions:[IconButton(onPressed:(){},icon:const Icon(Icons.settings_outlined))]),body:ListView(padding:const EdgeInsets.all(18),children:[Center(child:Container(width:76,height:76,decoration:BoxDecoration(color:const Color(0xFFE7DEFF),shape:BoxShape.circle),alignment:Alignment.center,child:const Text('H',style:TextStyle(fontSize:32,color:Color(0xFF6D3DF5),fontWeight:FontWeight.w900)))),const SizedBox(height:10),const Center(child:Text('Kart Kampanya',style:TextStyle(fontSize:18,fontWeight:FontWeight.w900,color:Color(0xFF211D2D)))),Center(child:Text(email,style:const TextStyle(fontSize:11,color:Color(0xFF777187)))),const SizedBox(height:22),...items.map((x)=>Container(margin:const EdgeInsets.only(bottom:9),decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(15),border:Border.all(color:const Color(0xFFE5E1EF))),child:ListTile(title:Text(x,style:const TextStyle(fontWeight:FontWeight.w700)),trailing:const Icon(Icons.chevron_right_rounded,color:Color(0xFF8A8394))))),Container(decoration:BoxDecoration(color:const Color(0xFFFFEEEE),borderRadius:BorderRadius.circular(15)),child:ListTile(onTap:()=>Supabase.instance.client.auth.signOut(),leading:const Icon(Icons.logout_rounded,color:Color(0xFFD33A3A)),title:const Text('Çıkış Yap',style:TextStyle(color:Color(0xFFD33A3A),fontWeight:FontWeight.w800))))]);
  }
}
'''
s=replace_class(s,'ProfilePage',profile)

p.write_text(s,encoding='utf-8')
print('v31 syntax fixes applied')
