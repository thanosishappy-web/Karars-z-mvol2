---
name: kararsizim-project
description: >-
  Kararsızım web uygulamasının tam proje planı ve geliştirme rehberi.
  Bu skill, projenin mevcut durumunu, mimari kararları, veritabanı şemasını,
  bilinen sorunları ve gelecek iyileştirmeleri içerir.
  Kullanıcı proje geliştirme ile ilgili bir istekte bulunduğunda bu skill aktif edilmelidir.
---

# Kararsızım - Proje Geliştirme Rehberi

## 🎯 Proje Özeti

**Kararsızım**, kullanıcıların kararsız oldukları konularda diğer kullanıcılara danışarak anket oluşturabildiği bir web uygulamasıdır. Kullanıcılar günlük hayattaki ikilemlerini (örneğin: "Bugün sinemaya mı gitsem yoksa restorana mı?") anket olarak paylaşır, diğer kullanıcılar da oy vererek yardımcı olur.

**Hedef:** Hızlı bir prototip çıkarmak. Basit, çalışan, genişletilebilir.

---

## 📐 Temel Kurallar & Kısıtlamalar

- **Takip mekanizması YOK**: Her kullanıcı platformdaki tüm anketleri görebilir ve oylayabilir.
- **Misafir erişimi VAR**: Üye olmayan kullanıcılar anketleri görebilir ve oylayabilir.
- **Anket oluşturma üyelik gerektirir**: Sadece kayıtlı kullanıcılar anket oluşturabilir.
- **Kayıt bilgileri**: E-posta, şifre ve kullanıcı adı gereklidir.
- **Gizlilik**: Anketlerde yalnızca kullanıcı adı görünür, e-posta asla gösterilmez.
- **Anket seçenekleri**: Minimum 2, maksimum 5 seçenek.

---

## 🛠 Teknoloji Stack

| Katman       | Teknoloji                                                     |
| ------------ | ------------------------------------------------------------- |
| Backend      | Python 3.14, Django 4.2.x                                     |
| Veritabanı   | Supabase (PostgreSQL), dev'de SQLite                           |
| Frontend     | HTML, CSS, JavaScript (framework yok, Django templates)        |
| Font         | Google Fonts — Inter                                           |
| Deployment   | Vercel (Serverless), WhiteNoise (statik dosyalar)              |
| Repo Yapısı  | Monorepo (tek repo, frontend + backend birlikte)               |

---

## 📁 Mevcut Proje Dizin Yapısı

```
kararsizim/
├── .agents/
│   └── skills/
│       └── kararsizim-project/
│           └── SKILL.md              # Bu dosya
├── kararsizim/                       # Django proje konfigürasyonu
│   ├── __init__.py
│   ├── settings.py                   # Tam konfigürasyon (Supabase, WhiteNoise, auth)
│   ├── urls.py                       # admin + hesap + anketler
│   ├── wsgi.py                       # Vercel entry point (app = application)
│   └── asgi.py
├── hesap/                            # Kullanıcı yönetimi uygulaması
│   ├── models.py                     # Boş — Django built-in User kullanılıyor
│   ├── views.py                      # kayit, giris, cikis, profil view'ları
│   ├── urls.py                       # app_name='hesap'
│   ├── forms.py                      # KayitFormu (UserCreationForm), GirisFormu
│   └── admin.py
├── anketler/                         # Anket uygulaması
│   ├── models.py                     # Anket, Secenek, Oy modelleri
│   ├── views.py                      # anasayfa, detay, olustur, oyla (AJAX)
│   ├── urls.py                       # app_name='anketler'
│   ├── forms.py                      # AnketOlusturFormu (soru + 5 secenek)
│   └── admin.py                      # AnketAdmin, SecenekAdmin, OyAdmin
├── templates/
│   ├── base.html                     # Ana şablon (navbar, mesajlar, footer)
│   ├── 404.html
│   ├── 500.html
│   ├── anketler/
│   │   ├── anasayfa.html             # Ana sayfa — hero + anket listesi + pagination
│   │   ├── anket_detay.html          # Oylama formu (AJAX) veya sonuçlar
│   │   └── anket_olustur.html        # Dinamik seçenek ekleme/çıkarma JS
│   └── hesap/
│       ├── giris.html
│       ├── kayit.html
│       └── profil.html
├── static/
│   ├── css/
│   │   └── style.css                 # ~960 satır, tam responsive tasarım
│   └── js/
│       └── app.js                    # Minimal — sayfa bazlı JS template'lerde
├── manage.py
├── requirements.txt
├── vercel.json
├── build_files.sh
├── .env.example
├── .gitignore
├── GEMINI.md
└── venv/                             # Python virtual environment
```

---

## 🗄 Veritabanı Şeması (Mevcut)

> **NOT:** Proje custom User modeli KULLANMIYOR. Django'nun built-in `django.contrib.auth.models.User` modelini kullanıyor. `AUTH_USER_MODEL` settings'te tanımlı DEĞİL.

### Anket Modeli
```python
class Anket(models.Model):
    soru = CharField(max_length=300)
    olusturan = ForeignKey(User, CASCADE, related_name='anketler')
    olusturma_tarihi = DateTimeField(auto_now_add=True)
    aktif = BooleanField(default=True)
    # Property: toplam_oy
```

### Secenek Modeli
```python
class Secenek(models.Model):
    anket = ForeignKey(Anket, CASCADE, related_name='secenekler')
    metin = CharField(max_length=200)
    oy_sayisi = PositiveIntegerField(default=0)
    # Property: oy_yuzdesi
```

### Oy Modeli
```python
class Oy(models.Model):
    secenek = ForeignKey(Secenek, CASCADE, related_name='oylar')
    anket = ForeignKey(Anket, CASCADE, related_name='oylar')
    oturum_id = CharField(max_length=64)       # session_key ile mükerrer oy kontrolü
    kullanici = ForeignKey(User, SET_NULL, null, blank, related_name='oylar')
    tarih = DateTimeField(auto_now_add=True)
    # Constraint: UniqueConstraint(['anket', 'oturum_id'], name='unique_oturum_oy')
```

### ER Diyagramı
```
User (1) ──── (N) Anket
                    │
Anket (1) ──── (N) Secenek
                    │
Secenek (1) ──── (N) Oy
                    │
User (1) ──── (N) Oy (nullable — misafirler oturum_id ile)
```

---

## 🔗 URL Yapısı (Mevcut)

| URL                              | View                 | Metod     | Açıklama                   | Yetki        |
| -------------------------------- | -------------------- | --------- | -------------------------- | ------------ |
| `/`                              | anasayfa_view        | GET       | Ana sayfa, anket listesi   | Herkese açık |
| `/anket/olustur/`               | anket_olustur_view   | GET, POST | Anket oluşturma            | @login_required |
| `/anket/<int:pk>/`              | anket_detay_view     | GET       | Anket detay & oylama       | Herkese açık |
| `/anket/<int:pk>/oyla/`         | oyla_view            | POST      | AJAX oylama endpoint       | Herkese açık |
| `/hesap/kayit/`                 | kayit_view           | GET, POST | Kullanıcı kaydı            | Herkese açık |
| `/hesap/giris/`                 | giris_view           | GET, POST | Giriş                      | Herkese açık |
| `/hesap/cikis/`                 | cikis_view           | POST      | Çıkış                      | Üye gerekli  |
| `/hesap/profil/`                | profil_view          | GET       | Kullanıcı profili           | @login_required |
| `/admin/`                       | Django Admin          | GET       | Admin paneli               | Staff gerekli |

---

## ✅ Tamamlanan Özellikler

### Faz 1: Proje Kurulumu & Veritabanı ✅
- [x] Django projesi oluşturuldu
- [x] Supabase/SQLite veritabanı bağlantısı (dj-database-url)
- [x] Anket, Secenek, Oy modelleri
- [x] Admin paneli (inline seçenekler, filtreleme, arama)

### Faz 2: Kimlik Doğrulama ✅
- [x] Kayıt formu (username, email, şifre)
- [x] Giriş (kullanıcı adı VEYA email ile)
- [x] Çıkış
- [x] Profil sayfası (kendi anketleri listesi)
- [x] Email benzersizlik kontrolü
- [x] Username validasyonu (harf, rakam, alt çizgi)

### Faz 3: Anket CRUD & Oylama ✅
- [x] Anket oluşturma (soru + 2-5 seçenek)
- [x] Anket listesi (pagination, 10/sayfa)
- [x] Anket detay sayfası
- [x] AJAX oylama (fetch API)
- [x] Mükerrer oy engelleme (oturum_id bazlı)
- [x] Oy sonuçları (progress bar + yüzde)
- [x] Oy sonrası animasyon

### Faz 4: Frontend & UI ✅
- [x] Responsive tasarım (mobil hamburger menü)
- [x] CSS custom properties ile renk teması (mor/pembe)
- [x] Anket kartları, hero section
- [x] Dinamik seçenek ekleme/çıkarma (JavaScript)
- [x] Django messages framework entegrasyonu
- [x] 404 ve 500 hata sayfaları

### Faz 5: Vercel Deploy Konfigürasyonu ✅
- [x] vercel.json yapılandırması
- [x] build_files.sh (collectstatic)
- [x] WhiteNoise statik dosya servisi
- [x] Production güvenlik ayarları (SSL, CSRF, XSS)
- [x] .env.example

---

## ⚠️ Bilinen Sorunlar & Dikkat Edilmesi Gerekenler

### 1. `giris_view` — `next` Parametresi Sorunu
```python
# Mevcut (sorunlu): URL name'i doğrudan redirect'e veriyor
next_url = request.GET.get('next', 'anketler:anasayfa')
return redirect(next_url)
```
Bu durumda `next=/anket/olustur/` gibi bir URL path geldiğinde doğru çalışır, ama `next` gelmediğinde `'anketler:anasayfa'` bir URL name olarak resolve edilir. Django'nun `redirect()` fonksiyonu hem URL name hem de path kabul ettiği için şu an çalışıyor, ama karışıklığa açık.

### 2. `oyla_view` — `F()` Sonrası `refresh_from_db` Eksik
```python
secenek.oy_sayisi = F('oy_sayisi') + 1
secenek.save(update_fields=['oy_sayisi'])
# Sonra secenekler yeniden sorgulanıyor ama anket.secenekler.all() 
# önceki prefetch cache'ini kullanabilir
```
`anket.refresh_from_db()` çağrılıyor ama `secenekler` cache'i invalidate edilmeyebilir. Çalışıyor görünüyor çünkü `all()` yeni sorgu atıyor, ama dikkat edilmeli.

### 3. AUTH_USER_MODEL Tanımlı Değil
Proje Django'nun built-in `User` modelini kullanıyor. Bu prototip için yeterli, ama gelecekte custom user modeline geçmek istenirse **en baştan migration yapmak gerekir** çünkü Django custom user modelini projenin başında tanımlamayı önerir.

---

## 🔮 Gelecek İyileştirmeler (Prototip Sonrası)

Bu özellikler prototipte **yer almıyor**, gelecekte eklenebilir:

### Kısa Vadeli (Kolay)
- [ ] Anket silme (kendi anketini sil)
- [ ] Anket kapatma (oylama durdurma)
- [ ] Ana sayfada sıralama (en yeni, en popüler)
- [ ] Daha iyi form hata mesajları (Türkçe)

### Orta Vadeli
- [ ] Anket kategorileri (Yemek, Eğlence, Giyim vb.)
- [ ] Arama ve filtreleme
- [ ] Anket süre limiti (ör: 24 saat)
- [ ] Sosyal medya paylaşımı (link kopyala, Twitter, WhatsApp)
- [ ] Dark mode (CSS variables ile kolay)

### Uzun Vadeli
- [ ] Anket yorumları
- [ ] Seçeneklere resim ekleme
- [ ] Bildirimler (oylama sonuçları güncellemesi)
- [ ] Custom User modeline geçiş
- [ ] API endpoint'leri (DRF ile)
- [ ] Real-time oy güncellemeleri (WebSocket / SSE)

---

## 🧪 Lokal Geliştirme

### Ortam Kurulumu
```bash
# Virtual environment aktif et
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# .env dosyasını oluştur
copy .env.example .env
# DATABASE_URL, SECRET_KEY değerlerini doldur

# Migration
python manage.py migrate

# Superuser oluştur
python manage.py createsuperuser

# Dev server başlat
python manage.py runserver
```

### Ortam Değişkenleri
```env
DATABASE_URL=postgresql://...  # Supabase bağlantı URL'i veya boş bırak (SQLite)
SECRET_KEY=...                 # Rastgele güvenli string
DEBUG=True                     # Development'ta True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

### Vercel'e Deploy
```bash
# Vercel CLI kurulu olmalı
npm i -g vercel

# Deploy
vercel --prod

# Vercel dashboard'dan ortam değişkenlerini ayarla:
# SECRET_KEY, DATABASE_URL, DEBUG=False, 
# ALLOWED_HOSTS=.vercel.app
# CSRF_TRUSTED_ORIGINS=https://kararsizim.vercel.app
```
