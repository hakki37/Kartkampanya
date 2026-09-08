from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text(encoding='utf-8')

# final-catalog-polish can replace the old logo block before rebuilding MyCardsPage.
# Guarantee the shared widget exists after every generated transformation.
if 'class CatalogLogo extends StatelessWidget' not in s:
    logo = r'''

class CatalogLogo extends StatelessWidget {
  final String label;
  final bool big;
  const CatalogLogo({super.key, required this.label, this.big = false});

  @override
  Widget build(BuildContext context) {
    final n = _norm(label);
    final w = big ? 108.0 : 82.0;
    final h = big ? 48.0 : 30.0;
    if (n == 'visa') return SizedBox(width:w,height:h,child:Center(child:Text('VISA',style:TextStyle(fontSize:big?27:20,fontWeight:FontWeight.w900,fontStyle:FontStyle.italic))));
    if (n == 'mastercard') return SizedBox(width:w,height:h,child:Center(child:Row(mainAxisAlignment:MainAxisAlignment.center,children:[Container(width:big?28:20,height:big?28:20,decoration:const BoxDecoration(shape:BoxShape.circle,color:Color(0xFFE9283F))),Container(margin:const EdgeInsets.only(left:-9),width:big?28:20,height:big?28:20,decoration:const BoxDecoration(shape:BoxShape.circle,color:Color(0xFFFFA500)))])));
    if (n == 'troy') return SizedBox(width:w,height:h,child:Center(child:Text('troy',style:TextStyle(fontSize:big?24:18,fontWeight:FontWeight.w900))));
    if (n == 'akbank') return SizedBox(width:w,height:h,child:Center(child:Text('AKBANK',style:TextStyle(fontSize:big?21:16,fontWeight:FontWeight.w900))));
    if (n == 'axess') return SizedBox(width:w,height:h,child:Center(child:Text('Axess',style:TextStyle(fontSize:big?22:16,fontWeight:FontWeight.w900))));
    return SizedBox(width:w,height:h,child:Center(child:Text(label,maxLines:1,overflow:TextOverflow.ellipsis,textAlign:TextAlign.center,style:TextStyle(fontSize:big?16:13,fontWeight:FontWeight.w900))));
  }
}
'''
    s += logo
    p.write_text(s, encoding='utf-8')
    print('CatalogLogo restored')
else:
    print('CatalogLogo already present')
