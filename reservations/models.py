"""
TR: Rezervasyon modeli ve kural kontrolleri (çakışma, süre, haftalık hak, önceden rezervasyon).
ES: Modelo de reserva y validación de reglas (solapamiento, duración, límite semanal, antelación).
"""
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from spaces.models import Space


class Reservation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Beklemede"
        APPROVED = "approved", "Onaylandı"
        REJECTED = "rejected", "Reddedildi"
        CANCELLED = "cancelled", "İptal edildi"

    # TR: Alanı "dolu" yapan durumlar (çakışma ve haftalık hak hesabında kullanılır)
    # ES: Estados que dejan el espacio "ocupado" (se usan para solapamientos y límite semanal)
    ACTIVE_STATUSES = [Status.PENDING, Status.APPROVED]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="reservations", verbose_name="Kullanıcı",
    )
    space = models.ForeignKey(
        Space, on_delete=models.CASCADE, related_name="reservations", verbose_name="Alan",
    )
    start_time = models.DateTimeField("Başlangıç")
    end_time = models.DateTimeField("Bitiş")
    purpose = models.CharField("Amaç", max_length=200, blank=True)
    status = models.CharField("Durum", max_length=20, choices=Status.choices, default=Status.PENDING)

    # TR: Personel, kullanıcının gelmediğini işaretleyebilir
    # ES: El personal puede marcar que el usuario no se presentó
    no_show = models.BooleanField("Gelmedi", default=False)

    # TR: Onaylayan/reddeden personel
    # ES: Personal que aprobó o rechazó la reserva
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="reviewed_reservations", verbose_name="İnceleyen",
    )
    created_at = models.DateTimeField("Oluşturulma", auto_now_add=True)

    class Meta:
        verbose_name = "Rezervasyon"
        verbose_name_plural = "Rezervasyonlar"
        ordering = ["-start_time"]
        constraints = [
            # TR: Bitiş, başlangıçtan sonra olmalı (veritabanı seviyesinde güvence)
            # ES: El fin debe ser posterior al inicio (garantía a nivel de base de datos)
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="reservation_end_after_start",
            ),
        ]

    def __str__(self):
        return f"{self.space} | {self.start_time:%d.%m.%Y %H:%M} | {self.user}"

    # ------------------------------------------------------------------
    # TR: Kural kontrolleri — formlar ve admin paneli kaydetmeden önce clean() çağırır
    # ES: Validación de reglas — los formularios y el admin llaman a clean() antes de guardar
    # ------------------------------------------------------------------
    def clean(self):
        # TR: Alan veya saatler henüz seçilmediyse diğer kontrolleri atla
        # ES: Si aún no se eligió espacio u horario, omitir el resto de comprobaciones
        if not (self.space_id and self.start_time and self.end_time):
            return

        if self.end_time <= self.start_time:
            raise ValidationError("Bitiş saati başlangıç saatinden sonra olmalıdır.")

        # TR: İptal/ret durumundaki kayıtlar için kural kontrolü gerekmez
        # ES: Las reservas canceladas o rechazadas no necesitan validar reglas
        if self.status not in self.ACTIVE_STATUSES:
            return

        errors = []
        now = timezone.now()
        is_new = self._state.adding

        if not self.space.is_active:
            errors.append("Bu alan şu anda rezervasyona kapalıdır.")

        # TR: Geçmiş tarih ve "en fazla X gün önceden" kuralları sadece yeni kayıtlarda
        # ES: Las reglas de fecha pasada y antelación máxima solo se aplican a reservas nuevas
        if is_new:
            if self.start_time < now:
                errors.append("Geçmiş bir tarih için rezervasyon yapılamaz.")
            if self.start_time > now + timedelta(days=self.space.max_advance_days):
                errors.append(
                    f"Bu alan için en fazla {self.space.max_advance_days} gün önceden rezervasyon yapılabilir."
                )

        # TR: Süre sınırı / ES: Límite de duración
        if self.end_time - self.start_time > timedelta(hours=self.space.max_duration_hours):
            errors.append(
                f"Bu alan için tek seferde en fazla {self.space.max_duration_hours} saat rezervasyon yapılabilir."
            )

        # TR: Gelmeme nedeniyle kısıtlanan kullanıcı / ES: Usuario restringido por ausencias
        if self.user_id and self.user.restricted_until and self.user.restricted_until > now:
            errors.append(
                f"Rezervasyon hakkınız {timezone.localtime(self.user.restricted_until):%d.%m.%Y} "
                "tarihine kadar kısıtlanmıştır."
            )

        if self.has_conflict():
            errors.append("Bu alan seçilen saat aralığında başka bir rezervasyonla çakışmaktadır.")

        if self.user_id and self.exceeds_weekly_limit():
            errors.append(
                f"Bu alan için haftalık rezervasyon hakkınızı ({self.space.weekly_limit}) doldurdunuz."
            )

        if errors:
            raise ValidationError(errors)

    def has_conflict(self):
        """
        TR: Aynı alanda saatleri kesişen aktif bir rezervasyon var mı?
            İki aralık, biri diğeri bitmeden başlıyorsa çakışır: A.başlangıç < B.bitiş VE A.bitiş > B.başlangıç
        ES: ¿Hay otra reserva activa en el mismo espacio cuyo horario se solape?
            Dos intervalos se solapan si uno empieza antes de que termine el otro: A.inicio < B.fin Y A.fin > B.inicio
        """
        return (
            Reservation.objects.filter(
                space=self.space,
                status__in=self.ACTIVE_STATUSES,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
            )
            .exclude(pk=self.pk)
            .exists()
        )

    def exceeds_weekly_limit(self):
        """
        TR: Kullanıcının bu alandaki, aynı haftaya (Pazartesi–Pazar) ait aktif rezervasyon sayısı sınırı aşıyor mu?
        ES: ¿El usuario supera el límite de reservas activas en este espacio en la misma semana (lunes–domingo)?
        """
        local_start = timezone.localtime(self.start_time)
        week_start = (local_start - timedelta(days=local_start.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        week_end = week_start + timedelta(days=7)
        count = (
            Reservation.objects.filter(
                user=self.user,
                space=self.space,
                status__in=self.ACTIVE_STATUSES,
                start_time__gte=week_start,
                start_time__lt=week_end,
            )
            .exclude(pk=self.pk)
            .count()
        )
        return count >= self.space.weekly_limit

    def save(self, *args, **kwargs):
        # TR: Onay gerektirmeyen alanlarda (ör. çalışma salonu) yeni rezervasyon anında onaylanır
        # ES: En espacios que no requieren aprobación (p. ej., sala de estudio) la reserva nueva se aprueba al instante
        if self._state.adding and self.status == self.Status.PENDING and not self.space.requires_approval:
            self.status = self.Status.APPROVED
        super().save(*args, **kwargs)
