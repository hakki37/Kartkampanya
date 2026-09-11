import 'package:flutter/material.dart';
class CategoryMenu extends StatelessWidget{
  final List<String> categories,selected; final ValueChanged<String> onSelected;
  const CategoryMenu({super.key,required this.categories,required this.selected,required this.onSelected});
  @override Widget build(BuildContext context)=>SizedBox(height:40,child:ListView.separated(scrollDirection:Axis.horizontal,padding:const EdgeInsets.symmetric(horizontal:16),itemCount:categories.length,separatorBuilder:(_,__)=>const SizedBox(width:8),itemBuilder:(_,i){final c=categories[i],active=c==selected;return ChoiceChip(label:Text(c),selected:active,showCheckmark:false,onSelected:(_)=>onSelected(c),labelStyle:TextStyle(color:active?Colors.white:const Color(0xFF5F5969),fontWeight:FontWeight.w700,fontSize:12.5),selectedColor:const Color(0xFF6D3DF5),backgroundColor:const Color(0xFFF0EEF5),side:BorderSide.none,padding:const EdgeInsets.symmetric(horizontal:12,vertical:4),shape:RoundedRectangleBorder(borderRadius:BorderRadius.circular(20)));}));
}
