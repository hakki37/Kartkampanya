from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

def replace_class(src, name, replacement):
    start = src.find('class ' + name)
    if start < 0: raise SystemExit(name + ' not found')
    brace = src.find('{', start)
    depth = 0; quote = None; esc = False
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
            if depth == 0: return src[:start] + replacement + src[i+1:]
    raise SystemExit(name + ' end not found')

card = r'''class SmartCampaignCard extends StatelessWidget {
  final Map<String,dynamic> campaign;
  final bool isFavorite,isCompared,showAllCampaigns,expiringSoon;
  final int daysRemaining,requiredSteps,completedSteps;
  final VoidCallback onFavorite,onCompare;
  final Future<void> Function(String url) onOpenUrl;
  final ValueChanged<int> onProgressChange;
  const SmartCampaignCard({super.key,required this.campaign,required this.isFavorite,required this.isCompared,required this.showAllCampaigns,required this.expiringSoon,required this.daysRemaining,required this.onFavorite,required this.onCompare,required this.onOpenUrl,required this.requiredSteps,required this.completedSteps,required this.onProgressChange});

  String clean(dynamic v){if(v==null)return '';return decodeHtmlEntities('$v').replaceAll(RegExp(r'<[^>]*>'),' ').replaceAll(RegExp(r'\\s+'),' ').trim();}
  String value(List<String> keys){for(final k in keys){final v=clean(campaign[k]);if(v.isNotEmpty)return v;}return '';}
  String logoDomain(String v){final n=_norm(v);const m={'akbank':'akbank.com','axess':'axess.com.tr','garanti':'garantibbva.com.tr','bonus':'bonus.com.tr','vakifbank':'vakifbank.com.tr','world':'worldcard.com.tr','yapi kredi':'worldcard.com.tr','qnb':'qnb.com.tr','cardfinans':'cardfinans.com.tr','teb':'teb.com.tr','hsbc':'hsbc.com','isbank':'isbank.com.tr','maximum':'maximum.com.tr','ziraat':'ziraatbank.com.tr','denizbank':'denizbank.com','enpara':'enpara.com','kuveytturk':'kuveytturk.com.tr','ing':'ing.com.tr'};for(final e in m.entries){if(n.contains(e.key))return e.value;}return '';}
  String merchantDomain(String v){final n=_norm(v);const m={'migros':'migros.com.tr','carrefour':'carrefoursa.com','trendyol':'trendyol.com','hepsiburada':'hepsiburada.com','amazon':'amazon.com.tr','a101':'a101.com.tr','bim':'bim.com.tr','sok':'sokmarket.com.tr','opet':'opet.com.tr','shell':'shell.com.tr','petrol ofisi':'petrolofisi.com.tr','mediamarkt':'mediamarkt.com.tr','teknosa':'teknosa.com','boyner':'boyner.com.tr','mavi':'mavi.com','ikea':'ikea.com.tr','ispark':'ispark.istanbul'};for(final e in m.entries){if(n.contains(e.key))return e.value;}return '';}
  String logo(String d)=>d.isEmpty?'':'https://cdn.brandfetch.io/$d/w/600/h/180/logo';
  Widget logoBox(String v){final d=logoDomain(v);return Container(width:78,height:38,padding:const EdgeInsets.all(6),decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(9)),alignment:Alignment.center,child:d.isEmpty?Text(v,maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(color:Color(0xFF172033),fontSize:10,fontWeight:FontWeight.w900)):Image.network(logo(d),fit:BoxFit.contain,errorBuilder:(_,__,___)=>Text(v,maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(color:Color(0xFF172033),fontSize:10,fontWeight:FontWeight.w900))));}

  @override Widget build(BuildContext context){
    final title=value(['title','name']); final merchant=value(['merchant','brand']); final category=value(['category']).isNotEmpty?value(['category']):campaignSection(campaign); final description=value(['description','campaign_text','summary','details','content']); final benefit=value(['benefit','benefit_label','advantage_label','reward','reward_amount','cashback','discount']); final minSpend=value(['min_spend','minimum_spend']); final cards=(campaign['_cards'] as List?)?.whereType<UserCard>().toList()??<UserCard>[];
    final labels=<String>[]; for(final c in cards){for(final x in [c.bank,c.card,c.network]){if(x.trim().isNotEmpty&&!labels.contains(x.trim()))labels.add(x.trim());}}
    final md=merchantDomain(merchant);
    return InkWell(borderRadius:BorderRadius.circular(22),onTap:()=>Navigator.of(context).push(MaterialPageRoute(builder:(_)=>CampaignDetailPage(campaign:campaign))),child:Container(margin:const EdgeInsets.only(bottom:14),padding:const EdgeInsets.all(14),decoration:BoxDecoration(color:const Color(0xFF0D1728),borderRadius:BorderRadius.circular(22),border:Border.all(color:const Color(0xFF243B59),width:1.15)),child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[
      Row(crossAxisAlignment:CrossAxisAlignment.start,children:[
        Container(width:86,height:66,padding:const EdgeInsets.all(7),decoration:BoxDecoration(color:Colors.white,borderRadius:BorderRadius.circular(12)),alignment:Alignment.center,child:md.isNotEmpty?Image.network(logo(md),fit:BoxFit.contain,errorBuilder:(_,__,___)=>Text(merchant.isEmpty?'KAMPANYA':merchant,maxLines:2,overflow:TextOverflow.ellipsis,textAlign:TextAlign.center,style:const TextStyle(color:Color(0xFF172033),fontWeight:FontWeight.w900,fontSize:11))):Text(merchant.isEmpty?'KAMPANYA':merchant,maxLines:2,overflow:TextOverflow.ellipsis,textAlign:TextAlign.center,style:const TextStyle(color:Color(0xFF172033),fontWeight:FontWeight.w900,fontSize:11))),
        const SizedBox(width:11),Expanded(child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[Text(title.isEmpty?'Kampanya':title,maxLines:3,overflow:TextOverflow.ellipsis,style:const TextStyle(color:Colors.white,fontSize:16,height:1.15,fontWeight:FontWeight.w900)),if(merchant.isNotEmpty)...[const SizedBox(height:4),Text(merchant,maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(color:Color(0xFFAAB6C8),fontSize:12,fontWeight:FontWeight.w600))],if(benefit.isNotEmpty)...[const SizedBox(height:7),Text('💰 Tahmini avantaj: $benefit',maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(color:Color(0xFFFFD166),fontSize:12.5,fontWeight:FontWeight.w900))]])),
        Column(children:[IconButton(visualDensity:VisualDensity.compact,padding:EdgeInsets.zero,constraints:const BoxConstraints(minWidth:32,minHeight:32),onPressed:onFavorite,icon:Icon(isFavorite?Icons.star_rounded:Icons.star_border_rounded,color:isFavorite?const Color(0xFFC5B5FF):const Color(0xFF7E8CA3),size:27)),IconButton(visualDensity:VisualDensity.compact,padding:EdgeInsets.zero,constraints:const BoxConstraints(minWidth:32,minHeight:32),onPressed:onCompare,icon:Icon(Icons.compare_arrows_rounded,color:isCompared?const Color(0xFFC5B5FF):const Color(0xFF7E8CA3),size:25))])]),
      if(labels.isNotEmpty)...[const SizedBox(height:11),SizedBox(height:38,child:ListView.separated(scrollDirection:Axis.horizontal,itemCount:labels.length>4?4:labels.length,separatorBuilder:(_,__)=>const SizedBox(width:7),itemBuilder:(_,i)=>logoBox(labels[i])))],
      if(description.isNotEmpty)...[const SizedBox(height:9),Text(description,maxLines:2,overflow:TextOverflow.ellipsis,style:const TextStyle(color:Color(0xFFAAB6C8),fontSize:12.5,height:1.25))],
      if(minSpend.isNotEmpty)...[const SizedBox(height:6),Text('Minimum harcama: $minSpend',maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(color:Color(0xFFDCE5F2),fontSize:12,fontWeight:FontWeight.w700))],
      const SizedBox(height:10),Row(children:[Container(constraints:const BoxConstraints(maxWidth:145),padding:const EdgeInsets.symmetric(horizontal:10,vertical:6),decoration:BoxDecoration(color:const Color(0xFF172943),borderRadius:BorderRadius.circular(15),border:Border.all(color:const Color(0xFF2A4668))),child:Text(category,maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(color:Color(0xFFD6CCFF),fontSize:11,fontWeight:FontWeight.w800))),const SizedBox(width:8),Expanded(child:Text(cards.isNotEmpty?'Kayıtlı kartlarınla eşleşiyor':'Kayıtlı kartlarınla eşleşmiyor',maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(color:Color(0xFF7F8DA4),fontSize:10.5,fontWeight:FontWeight.w600))),const Icon(Icons.chevron_right_rounded,color:Color(0xFF93A1B6),size:23)])
    ])));
  }
}
'''
s = replace_class(s,'SmartCampaignCard',card)
p.write_text(s,encoding='utf-8')
print('Reference card V3 applied')
