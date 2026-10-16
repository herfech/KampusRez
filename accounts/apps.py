from django.apps import AppConfig


class AccountsConfig(AppConfig):
    # TR: Kullanıcı yönetimi uygulaması / ES: Aplicación de gestión de usuarios
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "Kullanıcılar"
