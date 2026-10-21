"""
TR: Rezervasyon görünümleri: oluşturma, "Rezervasyonlarım", iptal ve personel onay paneli.
ES: Vistas de reservas: crear, "Mis reservas", cancelar y panel de aprobación del personal.
"""
from datetime import timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from notifications.emails import notify
from spaces.models import Space

from .forms import ReservationForm
from .models import Reservation


def manager_required(view):
    """
    TR: Sadece rezervasyon yönetme yetkisi olanlar (yönetici rolü) erişebilir.
    ES: Solo pueden acceder quienes tienen permiso para gestionar reservas (rol administrador).
    """
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.can_manage_reservations:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


# ----------------------------------------------------------------------
# TR: Kullanıcı ekranları / ES: Pantallas del usuario
# ----------------------------------------------------------------------
@login_required
def reservation_create(request, space_pk):
    space = get_object_or_404(Space, pk=space_pk, is_active=True)
    form = ReservationForm(request.POST or None, user=request.user, space=space)

    if request.method == "POST" and form.is_valid():
        reservation = form.save()
        if reservation.status == Reservation.Status.APPROVED:
            notify("approved", request.user, reservation=reservation)
            messages.success(request, "Rezervasyonunuz onaylandı.")
        else:
            notify("received", request.user, reservation=reservation)
            messages.info(request, "Rezervasyon talebiniz alındı. Personel onayından sonra kesinleşecektir.")
        return redirect("reservations:my")

    return render(request, "reservations/reservation_form.html", {"form": form, "space": space})


@login_required
def my_reservations(request):
    """
    TR: Kullanıcının kendi rezervasyonları: yaklaşan ve geçmiş olarak ikiye ayrılır.
    ES: Las reservas del propio usuario, separadas en próximas y pasadas.
    """
    now = timezone.now()
    reservations = request.user.reservations.select_related("space")
    return render(request, "reservations/my_reservations.html", {
        "upcoming": reservations.filter(end_time__gte=now).order_by("start_time"),
        "past": reservations.filter(end_time__lt=now).order_by("-start_time")[:20],
    })


@login_required
@require_POST
def reservation_cancel(request, pk):
    # TR: Kullanıcı sadece kendi rezervasyonunu iptal edebilir
    # ES: El usuario solo puede cancelar sus propias reservas
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)

    if not reservation.can_be_cancelled:
        messages.error(request, "Bu rezervasyon iptal edilemez.")
    else:
        reservation.status = Reservation.Status.CANCELLED
        reservation.save(update_fields=["status"])
        messages.success(request, "Rezervasyonunuz iptal edildi.")
    return redirect("reservations:my")


# ----------------------------------------------------------------------
# TR: Personel paneli / ES: Panel del personal
# ----------------------------------------------------------------------
@manager_required
def manage_panel(request):
    """
    TR: Onay bekleyen talepler ve son 3 günün onaylı rezervasyonları (gelmeme işaretlemek için).
    ES: Solicitudes pendientes y reservas aprobadas de los últimos 3 días (para marcar ausencias).
    """
    now = timezone.now()
    base = Reservation.objects.select_related("space", "user")
    return render(request, "reservations/manage_panel.html", {
        "pending": base.filter(status=Reservation.Status.PENDING, end_time__gte=now).order_by("start_time"),
        "recent": base.filter(
            status=Reservation.Status.APPROVED,
            start_time__lte=now,
            start_time__gte=now - timedelta(days=3),
        ).order_by("-start_time"),
    })


@manager_required
@require_POST
def manage_action(request, pk, action):
    """
    TR: Personel işlemi: onayla / reddet / gelmedi.
    ES: Acción del personal: aprobar / rechazar / no se presentó.
    """
    reservation = get_object_or_404(Reservation, pk=pk)
    actions = {
        "onayla": (reservation.approve, "Rezervasyon onaylandı."),
        "reddet": (reservation.reject, "Rezervasyon reddedildi."),
        "gelmedi": (reservation.mark_no_show, "Kullanıcı 'gelmedi' olarak işaretlendi."),
    }
    if action not in actions:
        raise PermissionDenied

    method, success_message = actions[action]
    if method(by=request.user):
        messages.success(request, success_message)
    else:
        messages.error(request, "Bu işlem bu rezervasyon için yapılamaz.")
    return redirect("reservations:manage")
