class AppConfig {
  static const supabaseUrl = 'https://bwkfehgzupbewfeovfnb.supabase.co';
  // GitHub Actions secret olarak SUPABASE_PUBLISHABLE_KEY tanımlanacak.
  static const supabasePublishableKey =
      String.fromEnvironment('SUPABASE_PUBLISHABLE_KEY');
}
