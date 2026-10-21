"""
TR: Rezervasyon e-posta bildirimleri. Geliştirmede e-postalar gönderilmez, terminale yazdırılır.
ES: Notificaciones de reserva por correo. En desarrollo no se envían, se imprimen en la terminal.
"""
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

# TR: Bildirim türü -> (konu, şablon)
# ES: Tipo de notificación -> (asunto, plantilla)
NOTIFICATIONS = {
    "received": ("Rezervasyon talebiniz alındı", "notifications/received.txt"),
    "approved": ("Rezervasyonunuz onaylandı", "notifications/approved.txt"),
    "rejected": ("Rezervasyon talebiniz reddedildi", "notifications/rejected.txt"),
    "restricted": ("Rezervasyon hakkınız kısıtlandı", "notifications/restricted.txt"),
}


def notify(kind, user, **context):
    """
    TR: Kullanıcıya bildirim e-postası gönderir. E-posta gönderilemezse hata kaydedilir
        ama işlem (onay, ret vb.) yarıda kalmaz.
    ES: Envía un correo de notificación al usuario. Si el correo falla se registra el error,
        pero la operación (aprobar, rechazar, etc.) no se interrumpe.
    """
    if not user.email:
        return False

    subject, template = NOTIFICATIONS[kind]
    body = render_to_string(template, {"user": user, **context})
    try:
        send_mail(f"KampüsRez · {subject}", body, settings.DEFAULT_FROM_EMAIL, [user.email])
        return True
    except Exception:
        logger.exception("E-posta gönderilemedi: %s -> %s", kind, user.email)
        return False
