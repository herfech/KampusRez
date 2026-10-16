"""
TR: Kullanıcıların yönetim panelinde gösterimi.
ES: Cómo se muestran los usuarios en el panel de administración.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "get_full_name", "email", "role", "school_number", "no_show_count")
    list_filter = ("role", "is_active")
    search_fields = ("username", "first_name", "last_name", "email", "school_number")

    # TR: Hazır alanlara ek olarak KampüsRez alanlarını göster
    # ES: Mostrar los campos de KampüsRez además de los campos estándar
    fieldsets = UserAdmin.fieldsets + (
        ("KampüsRez", {"fields": ("role", "school_number", "no_show_count", "restricted_until")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("KampüsRez", {"fields": ("email", "first_name", "last_name", "role", "school_number")}),
    )
