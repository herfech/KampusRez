from django.apps import AppConfig


class ReportsConfig(AppConfig):
    # TR: Kullanım istatistikleri (doluluk oranı, yoğun saatler) — sonraki sprintlerde doldurulacak
    # ES: Estadísticas de uso (tasa de ocupación, horas punta) — se completará en próximos sprints
    default_auto_field = "django.db.models.BigAutoField"
    name = "reports"
    verbose_name = "Raporlar"
