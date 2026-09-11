import 'package:flutter/material.dart';
import '../services/campaign_service.dart';
import '../services/card_service.dart';
import '../pages/campaign_detail_page.dart';
import 'campaign_card.dart';
import 'category_menu.dart';

class CampaignContent extends StatefulWidget{
  final List<UserCard> cards; final String mode; final String initialCategory;
  const CampaignContent({super.key,required this.cards,this.mode='home',this.initialCategory='Tümü'});
  @override State<CampaignContent> createState()=>_CampaignContentState();
}
class _CampaignContentState extends State<CampaignContent>{
  final service=CampaignService.instance,search=TextEditingController();late String category=widget.initialCategory;String query='';bool loading=true;List<Campaign> campaigns=const[];
  @override void initState(){super.initState();_load();}
  Future<void> _load() async{try{final data=await service.fetchCampaigns();if(mounted)setState((){campaigns=data;loading=false;});}catch(_){if(mounted)setState(()=>loading=false);}}
  @override void dispose(){search.dispose();super.dispose();}
  List<Campaign> get filtered{Iterable<Campaign> r=campaigns;if(widget.mode=='matched')r=r.where((c)=>service.matchesAnyCard(c,widget.cards));if(category!='Tümü')r=r.where((c)=>c.category==category);final q=normalizeCampaignText(query);if(q.isNotEmpty)r=r.where((c)=>normalizeCampaignText('${c.title} ${c.brand} ${c.bankName} ${c.category} ${c.description}').contains(q));return r.toList();}
  @override Widget build(BuildContext context){if(loading)return const Center(child:CircularProgressIndicator());final list=filtered;return Column(children:[Padding(padding:const EdgeInsets.fromLTRB(16,8,16,12),child:Row(children:[Expanded(child:TextField(controller:search,onChanged:(v)=>setState(()=>query=v),decoration:InputDecoration(hintText:'Kampanya, banka veya kategori ara...',prefixIcon:const Icon(Icons.search,size:20),isDense:true,contentPadding:const EdgeInsets.symmetric(vertical:12),filled:true,fillColor:const Color(0xFFF0EEF5),border:OutlineInputBorder(borderRadius:BorderRadius.all(Radius.circular(13)),borderSide:BorderSide.none)))),const SizedBox(width:8),OutlinedButton.icon(onPressed:_filterSheet,icon:const Icon(Icons.tune,size:18),label:const Text('Filtrele'),style:OutlinedButton.styleFrom(padding:const EdgeInsets.symmetric(horizontal:12,vertical:12),shape:RoundedRectangleBorder(borderRadius:BorderRadius.circular(13))))])),CategoryMenu(categories:service.categories,selected:category,onSelected:(v)=>setState(()=>category=v)),const SizedBox(height:7),Expanded(child:list.isEmpty?Center(child:Padding(padding:const EdgeInsets.all(30),child:Text(widget.mode=='matched'&&widget.cards.isEmpty?'Önce Bendeki Kartlar bölümünden kart ekle.':'Bu filtreye uygun kampanya bulunamadı.',textAlign:TextAlign.center,style:const TextStyle(color:Color(0xFF777187),fontWeight:FontWeight.w700)))):ListView.builder(padding:const EdgeInsets.only(bottom:18,top:3),itemCount:list.length,itemBuilder:(_,i)=>CampaignCard(campaign:list[i],isFavorite:service.isFavorite(list[i].id),onFavoriteTap:()async{await service.toggleFavorite(list[i].id);if(mounted)setState((){});},onTap:()=>Navigator.of(context).push(MaterialPageRoute(builder:(_)=>CampaignDetailPage(campaign:list[i])))))]) ;}
  void _filterSheet(){showModalBottomSheet(context:context,showDragHandle:true,builder:(_)=>SafeArea(child:Padding(padding:const EdgeInsets.fromLTRB(20,4,20,25),child:Column(mainAxisSize:MainAxisSize.min,crossAxisAlignment:CrossAxisAlignment.start,children:[const Text('Filtrele',style:TextStyle(fontSize:20,fontWeight:FontWeight.w900)),const SizedBox(height:14),Wrap(spacing:8,runSpacing:8,children:service.categories.map((c)=>ChoiceChip(label:Text(c),selected:category==c,showCheckmark:false,onSelected:(_){setState(()=>category=c);Navigator.pop(context);})).toList())]))));}
}
