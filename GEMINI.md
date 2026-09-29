# Kararsızım - Proje Kuralları

Bu bir Django web uygulamasıdır. Aşağıdaki kurallara her zaman uy:

## Teknoloji
- **Backend:** Python, Django 4.2.x
- **Veritabanı:** Supabase (sadece PostgreSQL olarak, Supabase Auth kullanma)
- **Frontend:** Django templates + HTML/CSS/JavaScript (framework yok)
- **Deploy:** Vercel (serverless) + WhiteNoise (statik dosyalar)
- **User Modeli:** Django'nun built-in `django.contrib.auth.models.User` (custom model YOK)

## Dil & İsimlendirme
- Arayüz, URL'ler ve model/form alanları **Türkçe** (ör: `soru`, `olusturan`, `anket/olustur/`)
- Python sınıf/fonksiyon isimleri **Türkçe** (ör: `AnketOlusturFormu`, `oyla_view`)
- Yorum ve commit mesajları Türkçe

## Mevcut Uygulama İsimleri
- `anketler` — Anket CRUD ve oylama (app_name='anketler')
- `hesap` — Kullanıcı kayıt/giriş/çıkış/profil (app_name='hesap')

## Temel Kurallar
- Misafir kullanıcılar anketleri görebilir ve oylayabilir
- Anket oluşturmak için `@login_required`
- E-posta asla frontend'de gösterilmez, sadece kullanıcı adı görünür
- Anketler 2-5 arası seçenek içermelidir
- Oylama AJAX ile yapılır (fetch API + JsonResponse)
- Mükerrer oy engelleme `oturum_id` (session_key) ile yapılır

## Proje Skill'i
Detaylı proje planı, mevcut yapı ve gelecek iyileştirmeler için `.agents/skills/kararsizim-project/SKILL.md` dosyasını oku.
