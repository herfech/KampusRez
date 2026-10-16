"""
TR: Rezervasyon oluşturma, "Rezervasyonlarım" ve iptal görünümleri.
ES: Vistas para crear reservas, "Mis reservas" y cancelar.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from spaces.models import Space

from .forms import ReservationForm
from .models import Reservation


@login_required
def reservation_create(request, space_pk):
    space = get_object_or_404(Space, pk=space_pk, is_active=True)
    form = ReservationForm(request.POST or None, user=request.user, space=space)

    if request.method == "POST" and form.is_valid():
        reservation = form.save()
        if reservation.status == Reservation.Status.APPROVED:
            messages.success(request, "Rezervasyonunuz onaylandı.")
        else:
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
