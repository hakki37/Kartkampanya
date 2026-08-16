# Kart Kampanya V6

Amaç: Flutter'ı bilgisayara kurmadan GitHub Actions ile APK üretmek.

## GitHub kurulumu
1. Yeni bir GitHub repository aç.
2. Bu projenin tüm dosyalarını yükle.
3. Repository > Settings > Secrets and variables > Actions.
4. New repository secret:
   - Name: SUPABASE_PUBLISHABLE_KEY
   - Secret: Supabase `sb_publishable_...` anahtarın.
5. Actions sekmesine gir.
6. `Build Android APK` workflow'unu seç.
7. `Run workflow` de.
8. İşlem bitince Actions > workflow run > Artifacts bölümünden `kart-kampanya-apk` dosyasını indir.

## Supabase
`supabase/schema.sql` dosyasını Supabase SQL Editor'da bir kez çalıştır.

Secret/service_role anahtarını GitHub'a veya uygulamaya koyma.
