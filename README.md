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
- İptal ve e-posta bildirimleri
- Gelmeme (no-show) takibi ve geçici kısıtlama
- Yönetim paneli ve kullanım istatistikleri
- Duyarlı (responsive) arayüz

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

# (İsteğe bağlı) Örnek alanları yükleyin
python manage.py demo_data

# 6. Sunucuyu başlatın
python manage.py runserver
```

Ardından tarayıcıda `http://127.0.0.1:8000/` (ana sayfa) ve `http://127.0.0.1:8000/admin/` (yönetim paneli) adreslerini açın.

## Testler

```bash
python manage.py test
```

## Kod Kuralları

- Değişken, fonksiyon, sınıf ve model adları **İngilizce** yazılır.
- Kullanıcının gördüğü tüm metinler (arayüz, mesajlar) **Türkçe**dir.
- Yorumlar **Türkçe ve İspanyolca** yazılır (`# TR:` / `# ES:`).
- Veritabanında saklanan seçim değerleri İngilizce, arayüzde gösterilen etiketler Türkçedir:

```python
class Status(models.TextChoices):
    APPROVED = "approved", "Onaylandı"
```
