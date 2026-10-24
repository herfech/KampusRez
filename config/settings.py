"""
TR: KampüsRez proje ayarları.
ES: Configuración del proyecto KampüsRez.

TR: Gizli bilgiler (SECRET_KEY vb.) koda yazılmaz; .env dosyasından okunur.
ES: Los datos secretos (SECRET_KEY, etc.) no se escriben en el código; se leen del archivo .env.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# TR: Proje kök dizini (manage.py'nin bulunduğu klasör)
# ES: Directorio raíz del proyecto (carpeta donde está manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# TR: .env dosyasındaki değişkenleri yükle
# ES: Cargar las variables del archivo .env
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-sadece-gelistirme-icin")
DEBUG = os.environ.get("DEBUG", "True") == "True"
ALLOWED_HOSTS = [h for h in os.environ.get("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h]


# TR: Uygulamalar — her biri raporda tanımlanan bir modüle karşılık gelir
# ES: Aplicaciones — cada una corresponde a un módulo definido en el informe
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # TR: Proje uygulamaları / ES: Aplicaciones del proyecto
    "core",           # TR: Ortak şablon araçları / ES: Utilidades comunes de plantillas
    "accounts",       # TR: Kullanıcı yönetimi ve roller / ES: Usuarios y roles
    "spaces",         # TR: Alan yönetimi / ES: Gestión de espacios
    "reservations",   # TR: Rezervasyon ve onay / ES: Reservas y aprobación
    "notifications",  # TR: E-posta bildirimleri / ES: Notificaciones por correo
    "reports",        # TR: Kullanım istatistikleri / ES: Estadísticas de uso
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# TR: Veritabanı — geliştirme için SQLite yeterlidir
# ES: Base de datos — para desarrollo basta con SQLite
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# TR: Özel kullanıcı modeli (roller için). İlk migrate'ten ÖNCE tanımlanmalıdır.
# ES: Modelo de usuario propio (para los roles). Debe definirse ANTES del primer migrate.
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# TR: Dil ve saat dilimi — arayüz Türkçe, saatler İstanbul saatine göre
# ES: Idioma y zona horaria — interfaz en turco, horas según Estambul
# TR: Sistem her ziyaretçiye Türkçe gösterilir; tarayıcının dili dikkate alınmaz
#     (bu yüzden LocaleMiddleware kullanılmıyor).
# ES: El sistema se muestra en turco a todos los visitantes; no se tiene en cuenta el idioma del navegador
#     (por eso no se usa LocaleMiddleware).
LANGUAGE_CODE = "tr"
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True


# TR: Statik dosyalar (CSS, JS, görseller)
# ES: Archivos estáticos (CSS, JS, imágenes)
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# TR: Giriş/çıkış yönlendirmeleri
# ES: Redirecciones de inicio y cierre de sesión
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "spaces:list"
LOGOUT_REDIRECT_URL = "home"

# TR: Kayıtta kabul edilen kurumsal e-posta alan adları (alt alan adları da kabul edilir,
#     ör. "gumushane.edu.tr" yazılırsa "ogr.gumushane.edu.tr" de geçerlidir)
# ES: Dominios de correo institucional aceptados en el registro (también se aceptan subdominios,
#     p. ej., si se pone "gumushane.edu.tr", "ogr.gumushane.edu.tr" también es válido)
#     .env'de boş bırakılırsa (ALLOWED_EMAIL_DOMAINS=) her e-posta kabul edilir — sadece geliştirme için!
#     Si se deja vacío en el .env (ALLOWED_EMAIL_DOMAINS=) se acepta cualquier correo — ¡solo para desarrollo!
ALLOWED_EMAIL_DOMAINS = [
    d.strip().lower()
    for d in os.environ.get("ALLOWED_EMAIL_DOMAINS", "gumushane.edu.tr").split(",")
    if d.strip()
]

# TR: Gelmeme (no-show) kuralı: kullanıcı NO_SHOW_LIMIT kez gelmezse NO_SHOW_RESTRICTION_DAYS gün kısıtlanır
# ES: Regla de no-show: si el usuario falta NO_SHOW_LIMIT veces, queda restringido NO_SHOW_RESTRICTION_DAYS días
NO_SHOW_LIMIT = int(os.environ.get("NO_SHOW_LIMIT", 3))
NO_SHOW_RESTRICTION_DAYS = int(os.environ.get("NO_SHOW_RESTRICTION_DAYS", 14))


# TR: E-posta — geliştirmede e-postalar gönderilmez, konsola yazdırılır
# ES: Correo — en desarrollo no se envían correos, se imprimen en la consola
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "kampusrez@example.edu.tr")
