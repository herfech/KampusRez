from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    # TR: E-posta bildirimleri (onay, ret, hatırlatma) — sonraki sprintlerde doldurulacak
    # ES: Notificaciones por correo (aprobación, rechazo, recordatorio) — se completará en próximos sprints
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"
    verbose_name = "Bildirimler"
