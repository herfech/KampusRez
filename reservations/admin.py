from django.contrib import admin

from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("space", "user", "start_time", "end_time", "status", "no_show")
    list_filter = ("status", "space__space_type", "space", "no_show")
    search_fields = ("user__username", "user__first_name", "user__last_name", "space__name", "purpose")
    date_hierarchy = "start_time"
    autocomplete_fields = ("user",)
    actions = ["approve", "reject"]

    # TR: Toplu onay/ret işlemleri (personel için)
    # ES: Acciones para aprobar/rechazar en bloque (para el personal)
    @admin.action(description="Seçili rezervasyonları onayla")
    def approve(self, request, queryset):
        updated = queryset.filter(status=Reservation.Status.PENDING).update(
            status=Reservation.Status.APPROVED, reviewed_by=request.user
        )
        self.message_user(request, f"{updated} rezervasyon onaylandı.")

    @admin.action(description="Seçili rezervasyonları reddet")
    def reject(self, request, queryset):
        updated = queryset.filter(status=Reservation.Status.PENDING).update(
            status=Reservation.Status.REJECTED, reviewed_by=request.user
        )
        self.message_user(request, f"{updated} rezervasyon reddedildi.")
