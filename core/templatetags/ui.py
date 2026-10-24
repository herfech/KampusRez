"""
TR: Arayüz için küçük şablon yardımcıları (Bootstrap sınıfları, durum rozetleri).
ES: Pequeñas utilidades de plantilla para la interfaz (clases de Bootstrap, etiquetas de estado).

TR: Kullanım: şablonun başına {% load ui %} yazılır.
ES: Uso: se escribe {% load ui %} al principio de la plantilla.
"""
from django import template
from django.forms import CheckboxInput, Select

register = template.Library()


@register.filter
def bootstrap(field):
    """
    TR: Form alanını Bootstrap sınıflarıyla çizer; hatalı alanlar kırmızı çerçeveyle gösterilir.
    ES: Dibuja un campo de formulario con clases de Bootstrap; los campos con error se marcan en rojo.
    """
    widget = field.field.widget
    if isinstance(widget, CheckboxInput):
        css = "form-check-input"
    elif isinstance(widget, Select):
        css = "form-select"
    else:
        css = "form-control"
    if field.errors:
        css += " is-invalid"
    return field.as_widget(attrs={"class": css})


# TR: Rezervasyon durumu -> (Bootstrap rengi, ikon)
# ES: Estado de la reserva -> (color de Bootstrap, icono)
STATUS_STYLES = {
    "pending": ("warning", "bi-hourglass-split"),
    "approved": ("success", "bi-check-circle"),
    "rejected": ("danger", "bi-x-circle"),
    "cancelled": ("secondary", "bi-slash-circle"),
}


@register.inclusion_tag("partials/status_badge.html")
def status_badge(reservation):
    color, icon = STATUS_STYLES.get(reservation.status, ("secondary", "bi-question-circle"))
    return {"label": reservation.get_status_display(), "color": color, "icon": icon}


# TR: Alan türü -> ikon / ES: Tipo de espacio -> icono
SPACE_ICONS = {
    "classroom": "bi-easel",
    "lab": "bi-pc-display",
    "study_room": "bi-people",
}


@register.filter
def space_icon(space):
    return SPACE_ICONS.get(space.space_type, "bi-building")


@register.filter
def is_checkbox(field):
    # TR: Onay kutusu alanı mı? (formda farklı çizilir) / ES: ¿Es una casilla? (se dibuja distinto en el formulario)
    return isinstance(field.field.widget, CheckboxInput)
