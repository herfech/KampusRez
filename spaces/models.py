"""
TR: Alanlar (derslik, laboratuvar, çalışma alanı) ve alan bazlı kurallar.
ES: Espacios (aula, laboratorio, sala de estudio) y sus reglas por espacio.
"""
from django.db import models


class Space(models.Model):
    """
    TR: Rezerve edilebilen bir alan.
    ES: Un espacio que se puede reservar.
    """

    class SpaceType(models.TextChoices):
        CLASSROOM = "classroom", "Derslik"
        LAB = "lab", "Laboratuvar"
        STUDY_ROOM = "study_room", "Çalışma Alanı"

    name = models.CharField("Alan adı", max_length=100)
    space_type = models.CharField("Alan türü", max_length=20, choices=SpaceType.choices)
    building = models.CharField("Bina", max_length=100)
    floor = models.CharField("Kat", max_length=20, blank=True)
    capacity = models.PositiveIntegerField("Kapasite")
    equipment = models.TextField(
        "Donanım", blank=True, help_text="Örn. projeksiyon, 30 bilgisayar, akıllı tahta"
    )

    # TR: Yönetici alanı bakım vb. nedenlerle kapatabilir
    # ES: El administrador puede cerrar el espacio por mantenimiento, etc.
    is_active = models.BooleanField("Rezervasyona açık", default=True)

    # --- TR: Alan bazlı kurallar / ES: Reglas por espacio ---

    # TR: True ise rezervasyon personel onayıyla kesinleşir (ör. laboratuvarlar)
    # ES: Si es True, la reserva requiere la aprobación del personal (p. ej., laboratorios)
    requires_approval = models.BooleanField("Onay gerekli", default=False)

    # TR: Tek seferde en fazla kaç saat rezerve edilebilir
    # ES: Máximo de horas por reserva
    max_duration_hours = models.PositiveSmallIntegerField("En fazla süre (saat)", default=2)

    # TR: Bir kullanıcının bu alan için haftalık en fazla rezervasyon sayısı
    # ES: Máximo de reservas semanales de un usuario en este espacio
    weekly_limit = models.PositiveSmallIntegerField("Haftalık hak", default=3)

    # TR: En fazla kaç gün öncesinden rezervasyon yapılabilir
    # ES: Con cuántos días de antelación como máximo se puede reservar
    max_advance_days = models.PositiveSmallIntegerField("En fazla kaç gün önceden", default=7)

    class Meta:
        verbose_name = "Alan"
        verbose_name_plural = "Alanlar"
        ordering = ["building", "name"]

    def __str__(self):
        return f"{self.name} ({self.building})"
