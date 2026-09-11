import 'package:flutter/material.dart';
class AppBottomNavigation extends StatelessWidget{
  final int currentIndex; final ValueChanged<int> onTap;
  const AppBottomNavigation({super.key,required this.currentIndex,required this.onTap});
  static const items=[_NavItem(Icons.home_outlined,Icons.home_rounded,'Ana Sayfa'),_NavItem(Icons.auto_awesome_outlined,Icons.auto_awesome,'Kartıma Uygun'),_NavItem(Icons.local_offer_outlined,Icons.local_offer_rounded,'Kampanyalar'),_NavItem(Icons.credit_card_outlined,Icons.credit_card_rounded,'Kartlarım'),_NavItem(Icons.grid_view_outlined,Icons.grid_view_rounded,'Kategoriler')];
  @override Widget build(BuildContext context)=>Container(decoration:const BoxDecoration(color:Colors.white,border:Border(top:BorderSide(color:Color(0xFFE9E4F1)))),child:SafeArea(top:false,child:SizedBox(height:64,child:Row(children:List.generate(items.length,(i){final x=items[i],active=i==currentIndex;return Expanded(child:InkWell(onTap:()=>onTap(i),child:Column(mainAxisAlignment:MainAxisAlignment.center,children:[Icon(active?x.active:x.icon,size:21,color:active?const Color(0xFF6D3DF5):const Color(0xFF77717F)),const SizedBox(height:3),Text(x.label,textAlign:TextAlign.center,maxLines:1,overflow:TextOverflow.ellipsis,style:TextStyle(fontSize:9.5,fontWeight:active?FontWeight.w800:FontWeight.w600,color:active?const Color(0xFF6D3DF5):const Color(0xFF77717F)))])));})))));
}
class _NavItem{final IconData icon,active;final String label;const _NavItem(this.icon,this.active,this.label);}
