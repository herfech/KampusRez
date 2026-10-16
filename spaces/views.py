"""
TR: Alan listesi ve alan detay (müsaitlik) görünümleri.
ES: Vistas de la lista de espacios y del detalle (disponibilidad) de un espacio.
"""
from datetime import datetime, time, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from reservations.models import Reservation

from .models import Space


@login_required
def space_list(request):
    """
    TR: Rezervasyona açık alanları türe ve binaya göre filtreleyerek listeler.
    ES: Lista los espacios abiertos a reserva, con filtros por tipo y edificio.
    """
    spaces = Space.objects.filter(is_active=True)

    selected_type = request.GET.get("tur", "")
    selected_building = request.GET.get("bina", "")
    if selected_type:
        spaces = spaces.filter(space_type=selected_type)
    if selected_building:
        spaces = spaces.filter(building=selected_building)

    buildings = (
        Space.objects.filter(is_active=True).order_by("building")
        .values_list("building", flat=True).distinct()
    )
    return render(request, "spaces/space_list.html", {
        "spaces": spaces,
        "space_types": Space.SpaceType.choices,
        "buildings": buildings,
        "selected_type": selected_type,
        "selected_building": selected_building,
    })


@login_required
def space_detail(request, pk):
    """
    TR: Alanın bilgilerini ve önümüzdeki günlerdeki dolu saatlerini gösterir.
        KVKK gereği rezervasyonu kimin yaptığı gösterilmez, sadece "dolu" bilgisi verilir.
    ES: Muestra la información del espacio y sus horas ocupadas en los próximos días.
        Por la KVKK no se muestra quién hizo la reserva, solo que está "ocupado".
    """
    space = get_object_or_404(Space, pk=pk, is_active=True)

    today = timezone.localdate()
    days = [today + timedelta(days=i) for i in range(space.max_advance_days + 1)]

    # TR: Görüntülenen aralıktaki aktif rezervasyonları tek sorguda al
    # ES: Obtener en una sola consulta las reservas activas del periodo mostrado
    range_start = timezone.make_aware(datetime.combine(days[0], time.min))
    range_end = range_start + timedelta(days=len(days))
    reservations = space.reservations.filter(
        status__in=Reservation.ACTIVE_STATUSES,
        start_time__lt=range_end,
        end_time__gt=range_start,
    ).order_by("start_time")

    # TR: Rezervasyonları başladıkları güne göre grupla
    # ES: Agrupar las reservas según el día en que empiezan
    by_day = {day: [] for day in days}
    for r in reservations:
        start_day = timezone.localtime(r.start_time).date()
        if start_day in by_day:
            by_day[start_day].append(r)
    schedule = [{"day": day, "busy": by_day[day]} for day in days]

    return render(request, "spaces/space_detail.html", {"space": space, "schedule": schedule})
