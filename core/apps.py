from django.apps import AppConfig


class CoreConfig(AppConfig):
    # TR: Ortak yardımcılar (şablon etiketleri vb.) / ES: Utilidades comunes (etiquetas de plantilla, etc.)
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Ortak"
