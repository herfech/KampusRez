from django.contrib import admin

from .models import Space


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    # TR: Yönetici alanları listeleyip filtreleyebilir
    # ES: El administrador puede listar y filtrar los espacios
    list_display = ("name", "space_type", "building", "floor", "capacity", "requires_approval", "is_active")
    list_filter = ("space_type", "building", "requires_approval", "is_active")
    search_fields = ("name", "building", "equipment")
    list_editable = ("is_active",)
    fieldsets = (
        ("Genel bilgiler", {"fields": ("name", "space_type", "building", "floor", "capacity", "equipment", "is_active")}),
        ("Kurallar", {"fields": ("requires_approval", "max_duration_hours", "weekly_limit", "max_advance_days")}),
    )
