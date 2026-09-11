import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class UserCard {
  final String id, bank, card, network, customerType, cardType;
  const UserCard({required this.id, required this.bank, required this.card, required this.network, required this.customerType, required this.cardType});
}

class CardService {
  CardService._();
  static final instance = CardService._();
  static const banks = <String>['Akbank','Garanti BBVA','Yapı Kredi','İş Bankası','Ziraat Bankası','Halkbank','QNB','DenizBank','TEB','VakıfBank','Kuveyt Türk','Türkiye Finans','Albaraka Türk','ING','Fibabanka','HSBC','Anadolubank','Odeabank','Enpara','CEPTETEB','Alternatif Bank'];
  static const cardMap = <String,List<String>>{
    'Akbank':['Axess','Wings','Free','Akbank Kart'],'Garanti BBVA':['Bonus','Bonus Gold','Bonus Platinum','Bonus Genç','Paracard'],'Yapı Kredi':['World','World Gold','World Platinum','World Elite','Play','Adios','Yapı Kredi Banka Kartı'],'İş Bankası':['Maximum','Maximum Gold','Maximum Platinum','Maximum Black','Maximum Genç','İş Bankası Bankamatik Kartı'],'Ziraat Bankası':['Bankkart','Bankkart Gold','Bankkart Platinum','Bankkart Genç','Ziraat Bankkart'],'Halkbank':['Paraf','Paraf Gold','Paraf Platinum','Parafly','Halkbank Banka Kartı'],'QNB':['CardFinans','CardFinans Gold','CardFinans Platinum','CardFinans Xtra','QNB Banka Kartı'],'DenizBank':['Bonus','Bonus Gold','Bonus Platinum','DenizBank Banka Kartı'],'TEB':['Bonus','Bonus Platinum','TEB Platinum','TEB Banka Kartı'],'VakıfBank':['World','World Gold','World Platinum','VakıfBank Banka Kartı'],'Kuveyt Türk':['Sağlam Kart','Sağlam Kart Platinum','Kuveyt Türk Banka Kartı'],'Türkiye Finans':['Happy Card','Happy Card Platinum','Türkiye Finans Banka Kartı'],'Albaraka Türk':['Bonus Card','Albaraka Banka Kartı'],'ING':['ING Bonus','ING Banka Kartı'],'Fibabanka':['Bonus Card','Fibabanka Banka Kartı'],'HSBC':['HSBC Premier','HSBC Advantage','HSBC Banka Kartı'],'Anadolubank':['Anadolubank Kart','Anadolubank Banka Kartı'],'Odeabank':['Odeabank Kart','Odeabank Banka Kartı'],'Enpara':['Enpara Kredi Kartı','Enpara Banka Kartı'],'CEPTETEB':['CEPTETEB Bonus','CEPTETEB Banka Kartı'],'Alternatif Bank':['Bonus','Alternatif Banka Kartı']};
  Future<List<UserCard>> fetchMyCards() async {
    final uid=Supabase.instance.client.auth.currentUser?.id; if(uid==null) return const [];
    final rows=await Supabase.instance.client.from('user_cards').select('id,bank_name,card_name,network,customer_type,card_type').eq('user_id',uid).order('created_at');
    return List<Map<String,dynamic>>.from(rows).map((m)=>UserCard(id:'${m['id']}',bank:'${m['bank_name']??''}',card:'${m['card_name']??''}',network:'${m['network']??'Visa'}',customerType:'${m['customer_type']??'Bireysel'}',cardType:'${m['card_type']??'Kredi'}')).toList();
  }
  Future<void> addCard(UserCard c) async { final uid=Supabase.instance.client.auth.currentUser?.id; if(uid==null) throw StateError('Oturum bulunamadı.'); await Supabase.instance.client.from('user_cards').insert({'user_id':uid,'bank_name':c.bank,'card_name':c.card,'network':c.network,'customer_type':c.customerType,'card_type':c.cardType}); }
  Future<void> deleteCard(UserCard c) => Supabase.instance.client.from('user_cards').delete().eq('id',c.id);
  Color bankColor(String bank){const m={'Akbank':Color(0xFFE30613),'Garanti BBVA':Color(0xFF007A3D),'Yapı Kredi':Color(0xFF0054A6),'İş Bankası':Color(0xFF0057A8),'Ziraat Bankası':Color(0xFF00853F),'Halkbank':Color(0xFF00529B),'QNB':Color(0xFF5B2C83)};return m[bank]??const Color(0xFF6D3DF5);}
}
