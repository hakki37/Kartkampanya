import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:url_launcher/url_launcher.dart';

class AuthService {
  AuthService._();
  static final instance = AuthService._();
  SupabaseClient get client => Supabase.instance.client;
  User? get currentUser => client.auth.currentUser;
  Stream<AuthState> get authStateChanges => client.auth.onAuthStateChange;
  Future<void> signInWithGoogle() async { await client.auth.signInWithOAuth(OAuthProvider.google, redirectTo: 'io.supabase.flutter://login-callback/', authScreenLaunchMode: LaunchMode.externalApplication); }
  Future<void> signIn(String email, String password) async { await client.auth.signInWithPassword(email: email.trim(), password: password); }
  Future<void> signUp(String email, String password) async { await client.auth.signUp(email: email.trim(), password: password); }
  Future<void> signOut() async { await client.auth.signOut(); }
}
