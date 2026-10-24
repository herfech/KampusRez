# KampüsRez

**Derslik, Laboratuvar ve Çalışma Alanı Rezervasyon Sistemi**

KampüsRez; derslik, bilgisayar laboratuvarı ve çalışma alanlarını tek bir platformda toplayan, müsaitlik durumunu gösteren ve alan türüne göre yapılandırılabilen kurallar ve onay süreçleriyle alanların şeffaf ve adil biçimde paylaşılmasını sağlayan web tabanlı bir rezervasyon sistemidir.

> Gümüşhane Üniversitesi – **Web Proje Yönetimi (BLSEC205)** dersi grup projesi
> Ders Sorumlusu: Dr. Rabia Yaşa Koştaş

## Ekip – Alpha Team

| Üye | Rol |
|---|---|
| Matias Fernando Ndong | Grup Sözcüsü |
| Daniel Obiang Ondo | |
| Daniel Ramses Mbourou | |
| Heriberto Fernandez Chale | |
| Rodolfo Mba Ndong | |

## Özellikler (Kapsam)

- Kurumsal e-posta ile giriş; **öğrenci**, **akademik personel** ve **yönetici** rolleri
- Alan listesi ve müsaitlik takvimi (kapasite, bina, kat, donanım)
- Rezervasyon oluşturma ve **çakışma kontrolü**
- Alan bazlı kurallar: en fazla süre, haftalık hak, en fazla kaç gün önceden
- Onay mekanizması (laboratuvarlar onaylı, çalışma alanları anında)
- Rezervasyon düzenleme, iptal ve duruma göre filtreleme
- E-posta bildirimleri
- Gelmeme (no-show) takibi ve geçici kısıtlama
- Yönetim paneli ve kullanım istatistikleri
- Profil sayfası, parola değiştirme ve e-posta ile parola sıfırlama
- Duyarlı (responsive) arayüz (Bootstrap 5.3 + Bootstrap Icons)

**Kapsam dışı:** fiziksel erişim kontrolü, ders programı hazırlama, envanter takibi, öğrenci bilgi sistemi entegrasyonu, mobil uygulama, SMS ve ödeme.

## Teknolojiler

- Python 3.11+
- Django 5.2 (LTS)
- SQLite (geliştirme)

## Proje Yapısı

```
KampusRez/
├── config/          # Proje ayarları ve URL'ler
├── accounts/        # Kullanıcılar ve roller
├── spaces/          # Alanlar ve alan bazlı kurallar
├── reservations/    # Rezervasyonlar, onay, çakışma kontrolü
├── notifications/   # E-posta bildirimleri
├── reports/         # Kullanım istatistikleri
├── templates/       # HTML şablonları
└── static/          # CSS, JS, görseller
```

## Kurulum

```bash
# 1. Depoyu klonlayın
git clone https://github.com/herfech/KampusRez.git
cd KampusRez

# 2. Sanal ortam oluşturup etkinleştirin
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. Ortam değişkenlerini hazırlayın
copy .env.example .env         # Windows
cp .env.example .env           # macOS / Linux

# 5. Veritabanını oluşturun ve yönetici hesabı açın
python manage.py migrate
python manage.py createsuperuser

# (İsteğe bağlı) Örnek alanları yükleyin / silin
python manage.py demo_data
python manage.py demo_data --sil

# 6. Sunucuyu başlatın
python manage.py runserver
```

Ardından tarayıcıda `http://127.0.0.1:8000/` (ana sayfa) ve `http://127.0.0.1:8000/admin/` (yönetim paneli) adreslerini açın.

## Roller ve Onay Paneli

- Kayıt olan her kullanıcı **öğrenci** rolüyle başlar.
- **Yönetici** rolü yönetim panelinden (`/admin/`) verilir. Yönetici rolündeki kullanıcılar
  `/rezervasyonlarim/yonetim/` adresindeki **Onay Paneli**'nde talepleri onaylayabilir/reddedebilir
  ve gelmeyen kullanıcıları işaretleyebilir.
- Yönetici rolündeki kullanıcılar `/alanlar/yonetim/` adresindeki **Alan Yönetimi** ekranında alan ekleyebilir,
  düzenleyebilir ve rezervasyona açıp kapatabilir. Alanlar silinmez; geçmiş ve istatistikler korunur.
- Bir kullanıcı `NO_SHOW_LIMIT` kez gelmezse `NO_SHOW_RESTRICTION_DAYS` gün boyunca rezervasyon yapamaz.
- Geliştirme ortamında e-postalar gönderilmez, `runserver` çalışan terminale yazdırılır.

## Testler

```bash
python manage.py test
```

## Logo

Logo, "ü" harfini 7 modülden (alanlar) oluşturur; mavi nokta boş alanı, kırmızı nokta rezervasyonu temsil eder.

| Dosya | Kullanım |
|---|---|
| `static/img/logo.svg` | Açık zemin (üst menü, giriş ekranı) |
| `static/img/logo-white.svg` | Koyu zemin |
| `static/img/favicon.svg` | Tarayıcı sekmesi ve küçük boyutlar |

Şablonlarda: `{% include "partials/logo.html" %}` (beyaz sürüm: `with variant="white"`).
Renkler: lacivert `#1f3b63`, kırmızı `#c8102e` · Yazı tipi: Space Grotesk.

## Kod Kuralları

- Değişken, fonksiyon, sınıf ve model adları **İngilizce** yazılır.
- Kullanıcının gördüğü tüm metinler (arayüz, mesajlar) **Türkçe**dir.
- Yorumlar **Türkçe ve İspanyolca** yazılır (`# TR:` / `# ES:`).
- Veritabanında saklanan seçim değerleri İngilizce, arayüzde gösterilen etiketler Türkçedir:

```python
class Status(models.TextChoices):
    APPROVED = "approved", "Onaylandı"
```
