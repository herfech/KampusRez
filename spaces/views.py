"""
TR: Alan listesi ve alan detay (müsaitlik) görünümleri.
ES: Vistas de la lista de espacios y del detalle (disponibilidad) de un espacio.
"""
from datetime import datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.decorators import manager_required
from reservations.models import Reservation

from .forms import SpaceForm
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


# ----------------------------------------------------------------------
# TR: Alan yönetimi (sadece yönetici rolü)
# ES: Gestión de espacios (solo rol administrador)
# ----------------------------------------------------------------------
@manager_required
def manage_list(request):
    """
    TR: Açık ve kapalı tüm alanlar; her alanın yaklaşan rezervasyon sayısıyla birlikte.
    ES: Todos los espacios, abiertos y cerrados, con el número de reservas próximas de cada uno.
    """
    now = timezone.now()
    spaces = Space.objects.annotate(
        upcoming_count=Count(
            "reservations",
            filter=Q(reservations__status__in=Reservation.ACTIVE_STATUSES, reservations__end_time__gte=now),
        )
    ).order_by("-is_active", "building", "name")
    return render(request, "spaces/manage_list.html", {
        "spaces": spaces,
        "active_count": sum(1 for s in spaces if s.is_active),
    })


# TR: Formu iki bölüm halinde göstermek için alan grupları
# ES: Grupos de campos para mostrar el formulario en dos secciones
GENERAL_FIELDS = ("name", "space_type", "building", "floor", "capacity", "equipment", "is_active")
RULE_FIELDS = ("requires_approval", "max_duration_hours", "weekly_limit", "max_advance_days")


def render_space_form(request, form, **extra):
    return render(request, "spaces/space_form.html", {
        "form": form,
        "general_fields": [form[name] for name in GENERAL_FIELDS],
        "rule_fields": [form[name] for name in RULE_FIELDS],
        **extra,
    })


@manager_required
def manage_create(request):
    form = SpaceForm(request.POST or None, initial={"is_active": True})
    if request.method == "POST" and form.is_valid():
        space = form.save()
        messages.success(request, f"“{space.name}” alanı oluşturuldu.")
        return redirect("spaces:manage")
    return render_space_form(request, form, is_edit=False)


@manager_required
def manage_edit(request, pk):
    space = get_object_or_404(Space, pk=pk)
    form = SpaceForm(request.POST or None, instance=space)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"“{space.name}” alanı güncellendi.")
        return redirect("spaces:manage")
    return render_space_form(request, form, is_edit=True, space=space)


@manager_required
@require_POST
def manage_toggle(request, pk):
    """
    TR: Alanı rezervasyona açar veya kapatır (silinmez; geçmiş rezervasyonlar ve istatistikler korunur).
        Mevcut rezervasyonlar iptal edilmez, yöneticiye bilgi verilir.
    ES: Abre o cierra el espacio a las reservas (no se borra; se conservan el historial y las estadísticas).
        Las reservas existentes no se cancelan; se informa al administrador.
    """
    space = get_object_or_404(Space, pk=pk)
    space.is_active = not space.is_active
    space.save(update_fields=["is_active"])

    if space.is_active:
        messages.success(request, f"“{space.name}” rezervasyona açıldı.")
    else:
        upcoming = space.reservations.filter(
            status__in=Reservation.ACTIVE_STATUSES, end_time__gte=timezone.now()
        ).count()
        if upcoming:
            messages.warning(
                request,
                f"“{space.name}” kapatıldı. Bu alanda {upcoming} yaklaşan rezervasyon var; "
                "gerekirse Onay Paneli'nden veya yönetim panelinden kontrol edin.",
            )
        else:
            messages.success(request, f"“{space.name}” rezervasyona kapatıldı.")
    return redirect("spaces:manage")
