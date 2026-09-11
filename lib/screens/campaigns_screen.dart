import 'package:flutter/material.dart';
import '../services/card_service.dart';
import '../widgets/app_header.dart';
import '../widgets/campaign_content.dart';
class CampaignsScreen extends StatelessWidget{
  final List<UserCard> cards; final String mode,initialCategory; final bool showHeader;
  const CampaignsScreen({super.key,required this.cards,this.mode='all',this.initialCategory='Tümü',this.showHeader=true});
  @override Widget build(BuildContext context){final content=CampaignContent(cards:cards,mode:mode,initialCategory:initialCategory);if(!showHeader)return content;return Scaffold(appBar:AppHeader(title:mode=='matched'?'Kartıma Uygun':'Kampanyalar'),body:content);}
}
