from django.apps import AppConfig


class ReservationsConfig(AppConfig):
    # TR: Rezervasyon ve onay uygulaması / ES: Aplicación de reservas y aprobación
    default_auto_field = "django.db.models.BigAutoField"
    name = "reservations"
    verbose_name = "Rezervasyonlar"
